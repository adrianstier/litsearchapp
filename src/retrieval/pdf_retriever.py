"""PDF retrieval from various sources"""

import os
import requests
from pathlib import Path
from typing import Tuple, List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.models import Paper
from src.utils.config import Config
from src.utils.rate_limiter import RateLimiter


class PDFRetriever:
    """Download PDFs from various sources"""

    def __init__(self, papers_dir: Optional[Path] = None, ucsb_session: Optional[requests.Session] = None):
        """
        Initialize PDF retriever

        Args:
            papers_dir: Directory to save PDFs
            ucsb_session: Optional authenticated UCSB library session
        """
        self.papers_dir = papers_dir or Config.PAPERS_DIR
        self.papers_dir.mkdir(parents=True, exist_ok=True)

        # Use UCSB session if provided, otherwise create new session
        self.session = ucsb_session if ucsb_session else requests.Session()
        if not ucsb_session:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Academic Literature Tool)'
            })

        self.has_institutional_access = ucsb_session is not None
        self.rate_limiter = RateLimiter(calls_per_second=1)

    def download_paper(self, paper: Paper) -> Tuple[bool, str]:
        """
        Download a single paper

        Args:
            paper: Paper to download

        Returns:
            (success, filepath or error message)
        """
        # Generate filename
        filename = self._generate_filename(paper)
        filepath = self.papers_dir / filename

        # Check if already downloaded
        if filepath.exists():
            paper.local_pdf_path = str(filepath)
            return True, str(filepath)

        # Try different download strategies
        strategies = [
            ("PMC", self._download_from_pmc),
            ("arXiv", self._download_from_arxiv),
            ("Direct URL", self._download_from_url),
            ("Unpaywall", self._download_from_unpaywall),
        ]

        # Add UCSB proxy strategy if we have institutional access
        if self.has_institutional_access:
            strategies.insert(0, ("UCSB Library", self._download_from_ucsb_proxy))

        for strategy_name, strategy_func in strategies:
            try:
                success = strategy_func(paper, filepath)
                if success:
                    paper.local_pdf_path = str(filepath)
                    print(f"  ✓ Downloaded via {strategy_name}: {paper.title[:50]}...")
                    return True, str(filepath)
            except Exception as e:
                continue

        error_msg = f"All download strategies failed for: {paper.title}"
        return False, error_msg

    def download_papers(self, papers: List[Paper], max_concurrent: int = 3) -> Dict:
        """
        Download multiple papers

        Args:
            papers: List of papers to download
            max_concurrent: Maximum concurrent downloads

        Returns:
            Dictionary with download results
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(papers)
        }

        print(f"\nDownloading {len(papers)} papers...")

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_paper = {
                executor.submit(self.download_paper, paper): paper
                for paper in papers
            }

            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    success, result = future.result()
                    if success:
                        results['successful'].append({
                            'paper': paper,
                            'filepath': result
                        })
                    else:
                        results['failed'].append({
                            'paper': paper,
                            'error': result
                        })
                except Exception as e:
                    results['failed'].append({
                        'paper': paper,
                        'error': str(e)
                    })

                # Progress update
                completed = len(results['successful']) + len(results['failed'])
                print(f"Progress: {completed}/{results['total']} "
                      f"({len(results['successful'])} successful)")

        return results

    def _generate_filename(self, paper: Paper) -> str:
        """Generate a safe filename for the paper"""
        # Use first author's last name and year
        if paper.authors:
            first_author = paper.authors[0].last_name or paper.authors[0].name.split()[-1]
        else:
            first_author = "Unknown"

        year = paper.year or "XXXX"

        # Clean title for filename
        title = paper.title[:60] if paper.title else "untitled"
        title_clean = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in title)
        title_clean = "_".join(title_clean.split())

        filename = f"{first_author}_{year}_{title_clean}.pdf"
        return filename

    def _download_from_pmc(self, paper: Paper, filepath: Path) -> bool:
        """Download from PubMed Central"""
        if not paper.pmcid:
            return False

        # PMC provides free PDFs
        pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{paper.pmcid}/pdf/"
        return self._download_url(pdf_url, filepath)

    def _download_from_arxiv(self, paper: Paper, filepath: Path) -> bool:
        """Download from arXiv"""
        if not paper.arxiv_id:
            return False

        # arXiv provides free PDFs
        pdf_url = f"https://arxiv.org/pdf/{paper.arxiv_id}.pdf"
        return self._download_url(pdf_url, filepath)

    def _download_from_url(self, paper: Paper, filepath: Path) -> bool:
        """Download from paper's PDF URL"""
        if not paper.pdf_url:
            return False

        return self._download_url(str(paper.pdf_url), filepath)

    def _download_from_unpaywall(self, paper: Paper, filepath: Path) -> bool:
        """Try to get open access version from Unpaywall"""
        if not paper.doi:
            return False

        # Unpaywall API (free, no key required but email is polite)
        email = Config.CROSSREF_MAILTO or "user@example.com"
        url = f"https://api.unpaywall.org/v2/{paper.doi}?email={email}"

        try:
            self.rate_limiter.wait_if_needed("unpaywall")
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Check for open access PDF
                if data.get("is_oa"):
                    best_location = data.get("best_oa_location")
                    if best_location and best_location.get("url_for_pdf"):
                        pdf_url = best_location["url_for_pdf"]
                        return self._download_url(pdf_url, filepath)
        except:
            pass

        return False

    def _download_from_ucsb_proxy(self, paper: Paper, filepath: Path) -> bool:
        """
        Download paper through UCSB library proxy

        Tries multiple URL strategies through institutional access:
        1. DOI resolution through proxy
        2. Direct publisher URLs through proxy
        3. PubMed links through proxy

        Args:
            paper: Paper to download
            filepath: Path to save file

        Returns:
            True if successful
        """
        proxy_base = "https://proxy.library.ucsb.edu/login?url="
        urls_to_try = []

        # Strategy 1: DOI through proxy (most reliable)
        if paper.doi:
            doi_url = f"https://doi.org/{paper.doi}"
            urls_to_try.append(f"{proxy_base}{doi_url}")

        # Strategy 2: Direct PDF URL through proxy
        if paper.pdf_url:
            urls_to_try.append(f"{proxy_base}{paper.pdf_url}")

        # Strategy 3: Paper URL through proxy
        if paper.url:
            urls_to_try.append(f"{proxy_base}{paper.url}")

        # Strategy 4: Publisher-specific URLs through proxy
        if paper.doi:
            # Common publisher patterns
            doi_parts = paper.doi.split('/')
            if len(doi_parts) >= 2:
                prefix = doi_parts[0]

                # Nature
                if prefix == '10.1038':
                    nature_url = f"https://www.nature.com/articles/{paper.doi}.pdf"
                    urls_to_try.append(f"{proxy_base}{nature_url}")

                # Elsevier/ScienceDirect
                elif prefix == '10.1016':
                    sd_url = f"https://www.sciencedirect.com/science/article/pii/{doi_parts[1]}/pdfft"
                    urls_to_try.append(f"{proxy_base}{sd_url}")

                # Wiley
                elif prefix == '10.1002':
                    wiley_url = f"https://onlinelibrary.wiley.com/doi/pdfdirect/{paper.doi}"
                    urls_to_try.append(f"{proxy_base}{wiley_url}")

                # Springer
                elif prefix == '10.1007':
                    springer_url = f"https://link.springer.com/content/pdf/{paper.doi}.pdf"
                    urls_to_try.append(f"{proxy_base}{springer_url}")

                # ACS
                elif prefix == '10.1021':
                    acs_url = f"https://pubs.acs.org/doi/pdf/{paper.doi}"
                    urls_to_try.append(f"{proxy_base}{acs_url}")

        # Try each URL
        for url in urls_to_try:
            try:
                if self._download_url(url, filepath):
                    return True
            except:
                continue

        return False

    def _download_url(self, url: str, filepath: Path) -> bool:
        """
        Download a file from URL

        Args:
            url: URL to download from
            filepath: Path to save file

        Returns:
            True if successful
        """
        try:
            self.rate_limiter.wait_if_needed("download")
            response = self.session.get(
                url,
                stream=True,
                timeout=30,
                allow_redirects=True
            )

            # Check if it's a PDF
            content_type = response.headers.get('content-type', '').lower()
            if response.status_code == 200:
                # Save file
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Verify it's a PDF
                with open(filepath, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        return True

                # Not a PDF, remove it
                filepath.unlink()

        except Exception as e:
            if filepath.exists():
                filepath.unlink()

        return False