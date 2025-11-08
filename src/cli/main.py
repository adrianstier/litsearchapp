#!/usr/bin/env python3
"""Main CLI entry point for literature search application"""

import click
import json
import sys
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from src.models import SearchQuery, Source, PaperType
from src.search.orchestrator import SearchOrchestrator
from src.retrieval.pdf_retriever import PDFRetriever
from src.utils.config import Config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Literature Search Tool - Intelligent academic paper discovery

    Search multiple academic databases, download papers, and synthesize findings.
    """
    pass


@cli.command()
@click.argument('query')
@click.option('--sources', '-s', multiple=True,
              type=click.Choice(['pubmed', 'arxiv', 'crossref', 'scholar']),
              default=['pubmed', 'arxiv', 'crossref'],
              help='Sources to search')
@click.option('--max-results', '-n', default=50, type=int,
              help='Maximum results per source')
@click.option('--year-start', type=int, help='Start year for filtering')
@click.option('--year-end', type=int, help='End year for filtering')
@click.option('--output', '-o', type=click.Path(), help='Output file (JSON)')
@click.option('--download/--no-download', default=False,
              help='Download PDFs automatically')
def search(query: str, sources: tuple, max_results: int,
           year_start: Optional[int], year_end: Optional[int],
           output: Optional[str], download: bool):
    """
    Search for academic papers

    Example:
        litsearch search "machine learning healthcare" -n 20 --download
    """
    console.print(f"\n[bold cyan]🔍 Searching for:[/bold cyan] {query}")
    console.print(f"[dim]Sources: {', '.join(sources)}[/dim]\n")

    # Convert source strings to enum
    source_enums = []
    for source in sources:
        try:
            source_enums.append(Source(source))
        except ValueError:
            console.print(f"[red]Invalid source: {source}[/red]")
            continue

    # Create search query
    search_query = SearchQuery(
        query=query,
        sources=source_enums,
        max_results=max_results,
        year_start=year_start,
        year_end=year_end
    )

    # Execute search
    orchestrator = SearchOrchestrator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching databases...", total=None)
        results = orchestrator.search(search_query)
        progress.remove_task(task)

    # Display results
    console.print(f"\n[bold green]✓ Found {len(results.papers)} unique papers[/bold green]")

    # Show statistics
    stats = results.get_statistics()
    stats_table = Table(title="Search Statistics", show_header=False)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")

    stats_table.add_row("Total papers", str(stats['total_papers']))
    stats_table.add_row("Search time", f"{stats['search_time']:.2f}s")
    stats_table.add_row("Average citations", f"{stats['avg_citations']:.1f}")

    if stats['papers_by_source']:
        source_str = ", ".join([f"{k}: {v}" for k, v in stats['papers_by_source'].items()])
        stats_table.add_row("By source", source_str)

    console.print(stats_table)

    # Display top papers
    if results.papers:
        console.print("\n[bold]Top Results:[/bold]")

        papers_table = Table(show_header=True, header_style="bold magenta")
        papers_table.add_column("#", style="dim", width=3)
        papers_table.add_column("Title", width=50)
        papers_table.add_column("Authors", width=20)
        papers_table.add_column("Year", width=4)
        papers_table.add_column("Citations", width=8)
        papers_table.add_column("Type", width=10)

        for i, paper in enumerate(results.papers[:10], 1):
            # Truncate title if needed
            title = paper.title
            if len(title) > 47:
                title = title[:47] + "..."

            # Format authors
            if paper.authors:
                if len(paper.authors) == 1:
                    authors = paper.authors[0].name
                elif len(paper.authors) == 2:
                    authors = f"{paper.authors[0].name.split()[-1]} & {paper.authors[1].name.split()[-1]}"
                else:
                    authors = f"{paper.authors[0].name.split()[-1]} et al."
            else:
                authors = "Unknown"

            papers_table.add_row(
                str(i),
                title,
                authors[:20],
                str(paper.year or ""),
                str(paper.citations),
                paper.paper_type.value
            )

        console.print(papers_table)

    # Download PDFs if requested
    if download and results.papers:
        console.print("\n[bold cyan]📥 Downloading PDFs...[/bold cyan]")

        # Try to load UCSB authentication
        from src.auth.ucsb_auth import UCSBAuth
        ucsb_auth = UCSBAuth()
        ucsb_session = None

        if ucsb_auth.load_session():
            console.print("[green]✓ Using UCSB library access[/green]\n")
            ucsb_session = ucsb_auth.get_session()
        else:
            console.print("[dim]No institutional access - will only download open access papers[/dim]")
            console.print("[dim]To enable UCSB access: python -m src.cli.main auth import-cookies[/dim]\n")

        retriever = PDFRetriever(ucsb_session=ucsb_session)
        download_results = retriever.download_papers(results.papers[:max_results])

        console.print(f"\n[green]✓ Downloaded: {len(download_results['successful'])}[/green]")
        console.print(f"[red]✗ Failed: {len(download_results['failed'])}[/red]")

    # Save results if output specified
    if output:
        output_path = Path(output)
        with open(output_path, 'w') as f:
            # Convert to dict for JSON serialization
            results_dict = {
                'query': search_query.model_dump(),
                'statistics': stats,
                'papers': [p.model_dump() for p in results.papers],
                'search_time': results.search_time,
                'errors': results.errors
            }
            json.dump(results_dict, f, indent=2, default=str)
        console.print(f"\n[green]Results saved to: {output_path}[/green]")


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--max-papers', '-n', default=50, type=int,
              help='Maximum papers to download')
@click.option('--concurrent', '-c', default=3, type=int,
              help='Concurrent downloads')
def download(results_file: str, max_papers: int, concurrent: int):
    """
    Download PDFs from search results

    Example:
        litsearch download results.json -n 20
    """
    # Load results
    with open(results_file) as f:
        data = json.load(f)

    papers_data = data.get('papers', [])
    if not papers_data:
        console.print("[red]No papers found in results file[/red]")
        return

    # Convert to Paper objects
    from src.models import Paper
    papers = []
    for paper_dict in papers_data[:max_papers]:
        try:
            # Handle datetime strings
            if 'retrieved_at' in paper_dict:
                paper_dict['retrieved_at'] = paper_dict['retrieved_at'].split('T')[0]
            papers.append(Paper(**paper_dict))
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load paper: {e}[/yellow]")
            continue

    console.print(f"\n[bold cyan]📥 Downloading {len(papers)} papers...[/bold cyan]")

    # Try to load UCSB authentication
    from src.auth.ucsb_auth import UCSBAuth
    ucsb_auth = UCSBAuth()
    ucsb_session = None

    if ucsb_auth.load_session():
        console.print("[green]✓ Using UCSB library access[/green]\n")
        ucsb_session = ucsb_auth.get_session()
    else:
        console.print("[dim]No institutional access - will only download open access papers[/dim]")
        console.print("[dim]To enable UCSB access: python -m src.cli.main auth import-cookies[/dim]\n")

    retriever = PDFRetriever(ucsb_session=ucsb_session)
    results = retriever.download_papers(papers, max_concurrent=concurrent)

    # Show results
    console.print(f"\n[bold]Download Summary:[/bold]")
    console.print(f"[green]✓ Successful: {len(results['successful'])}[/green]")
    console.print(f"[red]✗ Failed: {len(results['failed'])}[/red]")

    if results['successful']:
        console.print("\n[bold green]Downloaded papers:[/bold green]")
        for item in results['successful'][:10]:
            console.print(f"  • {item['paper'].title[:60]}...")
            console.print(f"    [dim]{item['filepath']}[/dim]")

    if results['failed']:
        console.print("\n[bold red]Failed downloads:[/bold red]")
        for item in results['failed'][:5]:
            console.print(f"  • {item['paper'].title[:60]}...")
            console.print(f"    [dim]{item['error']}[/dim]")


@cli.command()
@click.argument('identifier')
@click.option('--source', '-s', type=click.Choice(['pubmed', 'arxiv', 'crossref']),
              help='Source hint for the identifier')
def get(identifier: str, source: Optional[str]):
    """
    Get a specific paper by ID (PMID, DOI, arXiv ID)

    Examples:
        litsearch get 10.1038/nature12373
        litsearch get 35360497 --source pubmed
        litsearch get 2301.08727 --source arxiv
    """
    console.print(f"\n[bold cyan]🔍 Fetching paper: {identifier}[/bold cyan]")

    orchestrator = SearchOrchestrator()

    source_enum = Source(source) if source else None
    paper = orchestrator.get_paper_by_id(identifier, source_enum)

    if not paper:
        console.print(f"[red]Paper not found: {identifier}[/red]")
        return

    # Display paper details
    panel_content = f"""[bold]{paper.title}[/bold]

[cyan]Authors:[/cyan] {', '.join([a.name for a in paper.authors[:5]])}
[cyan]Year:[/cyan] {paper.year or 'Unknown'}
[cyan]Journal:[/cyan] {paper.journal or 'Unknown'}
[cyan]Citations:[/cyan] {paper.citations}
[cyan]Type:[/cyan] {paper.paper_type.value}

[cyan]Identifiers:[/cyan]
  DOI: {paper.doi or 'N/A'}
  PMID: {paper.pmid or 'N/A'}
  arXiv: {paper.arxiv_id or 'N/A'}
"""

    if paper.abstract:
        abstract_preview = paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract
        panel_content += f"\n[cyan]Abstract:[/cyan]\n{abstract_preview}"

    panel = Panel(panel_content, title="Paper Details", border_style="green")
    console.print(panel)

    # Ask if user wants to download
    if paper.pdf_url or paper.pmcid or paper.arxiv_id:
        if click.confirm("\nDownload PDF?"):
            retriever = PDFRetriever()
            success, result = retriever.download_paper(paper)
            if success:
                console.print(f"[green]✓ Downloaded to: {result}[/green]")
            else:
                console.print(f"[red]✗ Download failed: {result}[/red]")


@cli.command()
def config():
    """Show current configuration"""
    console.print("\n[bold]Literature Search Configuration[/bold]\n")

    config_table = Table(show_header=False)
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="white")

    config_table.add_row("Cache Directory", str(Config.CACHE_DIR))
    config_table.add_row("Papers Directory", str(Config.PAPERS_DIR))
    config_table.add_row("Output Directory", str(Config.OUTPUT_DIR))
    config_table.add_row("PubMed Rate Limit", f"{Config.PUBMED_RATE_LIMIT} req/s")
    config_table.add_row("arXiv Rate Limit", f"{Config.ARXIV_RATE_LIMIT} req/s")
    config_table.add_row("Crossref Rate Limit", f"{Config.CROSSREF_RATE_LIMIT} req/s")
    config_table.add_row("AI Synthesis Available", "✓" if Config.has_ai_capabilities() else "✗")

    console.print(config_table)

    console.print("\n[dim]Edit .env file to change settings[/dim]")


@cli.command()
@click.argument('query')
def quick(query: str):
    """
    Quick search with default settings

    Example:
        litsearch quick "CRISPR gene editing"
    """
    # Quick search with sensible defaults
    search_query = SearchQuery(
        query=query,
        sources=[Source.PUBMED, Source.ARXIV],
        max_results=20
    )

    console.print(f"\n[bold cyan]⚡ Quick search: {query}[/bold cyan]\n")

    orchestrator = SearchOrchestrator()
    results = orchestrator.search(search_query)

    # Show compact results
    for i, paper in enumerate(results.papers[:10], 1):
        # Format citation
        if paper.authors:
            first_author = paper.authors[0].name.split()[-1]
        else:
            first_author = "Unknown"

        citation = f"{first_author} ({paper.year or 'n.d.'})"

        console.print(f"[bold]{i}.[/bold] {paper.title}")
        console.print(f"   [dim]{citation} - {paper.journal or 'Unknown'} - {paper.citations} citations[/dim]")
        if paper.doi:
            console.print(f"   [blue]https://doi.org/{paper.doi}[/blue]")
        console.print()

    console.print(f"[green]Found {len(results.papers)} papers total[/green]")


@cli.group()
def auth():
    """
    Manage UCSB library authentication for institutional access

    Use these commands to enable downloading of paywalled papers
    through your UCSB library subscription.
    """
    pass


@auth.command('import-cookies')
@click.argument('cookies_file', type=click.Path(exists=True))
def import_cookies(cookies_file: str):
    """
    Import browser cookies for UCSB library access

    Steps:
    1. Install "Get cookies.txt LOCALLY" browser extension
    2. Log into library.ucsb.edu with your NetID and DUO
    3. Export cookies using the extension
    4. Run this command with the cookies file

    Example:
        litsearch auth import-cookies ~/Downloads/cookies.txt
    """
    from src.auth.ucsb_auth import UCSBAuth

    console.print("\n[bold cyan]📚 Importing UCSB Library Cookies[/bold cyan]\n")

    auth_manager = UCSBAuth()
    cookies_path = Path(cookies_file)

    # Try to import as Netscape format first
    success = auth_manager.import_cookies_netscape(cookies_path)

    if success:
        console.print("\n[bold green]✓ Successfully authenticated with UCSB library![/bold green]")
        console.print("\n[dim]You can now download paywalled papers with:")
        console.print("  python -m src.cli.main search 'your topic' --download[/dim]")
    else:
        console.print("\n[bold red]✗ Authentication failed[/bold red]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Make sure you're logged into library.ucsb.edu")
        console.print("2. Export fresh cookies (they may have expired)")
        console.print("3. Use 'Get cookies.txt LOCALLY' extension")


@auth.command('status')
def auth_status():
    """
    Check UCSB library authentication status

    Example:
        litsearch auth status
    """
    from src.auth.ucsb_auth import UCSBAuth

    console.print("\n[bold]UCSB Library Authentication Status[/bold]\n")

    auth_manager = UCSBAuth()

    # Try to load existing session
    if auth_manager.load_session():
        status = auth_manager.get_status()
    else:
        status = auth_manager.get_status()

    status_table = Table(show_header=False)
    status_table.add_column("Property", style="cyan")
    status_table.add_column("Value", style="white")

    status_table.add_row(
        "Status",
        "[green]✓ Authenticated[/green]" if status['authenticated'] else "[red]✗ Not authenticated[/red]"
    )
    status_table.add_row("Config Directory", status['config_dir'])
    status_table.add_row("Session File Exists", "✓" if status['session_file_exists'] else "✗")
    status_table.add_row("Cookies Count", str(status['cookies_count']))

    console.print(status_table)

    if not status['authenticated']:
        console.print("\n[dim]To enable institutional access:[/dim]")
        console.print("[dim]  python -m src.cli.main auth import-cookies <cookies_file>[/dim]")
    else:
        console.print("\n[green]✓ Institutional access enabled[/green]")
        console.print("[dim]Paywalled papers will be downloaded through UCSB library[/dim]")


@auth.command('clear')
def clear_auth():
    """
    Clear saved UCSB authentication

    Use this when:
    - Switching accounts
    - Cookies expired
    - Troubleshooting

    Example:
        litsearch auth clear
    """
    from src.auth.ucsb_auth import UCSBAuth

    if click.confirm("\nClear UCSB library authentication?"):
        auth_manager = UCSBAuth()
        auth_manager.clear_session()
        console.print("\n[green]✓ Authentication cleared[/green]")
        console.print("[dim]Import new cookies with: python -m src.cli.main auth import-cookies[/dim]")
    else:
        console.print("\n[dim]Cancelled[/dim]")


if __name__ == '__main__':
    cli()