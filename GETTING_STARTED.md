# Getting Started

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
pip install -q requests click rich python-dotenv pydantic arxiv
```

### 2. Try Your First Search

```bash
# Quick search
python -m src.cli.main quick "your research topic"

# Example
python -m src.cli.main quick "machine learning"
```

### 3. See What You Can Do

```bash
python -m src.cli.main --help
```

## Your First Real Search

Let's search for papers on CRISPR gene editing:

```bash
python -m src.cli.main search "CRISPR gene editing" \
    --sources pubmed arxiv \
    --max-results 20 \
    --year-start 2022 \
    --output crispr_results.json
```

This will:
- Search PubMed and arXiv
- Find up to 20 papers from each
- Filter for papers from 2022 onwards
- Save results to `crispr_results.json`

## Download Papers

```bash
python -m src.cli.main download crispr_results.json --max-papers 10
```

This downloads the first 10 papers (if available as open access).

## Get a Specific Paper

If you know a DOI or PubMed ID:

```bash
# By DOI
python -m src.cli.main get "10.1126/science.1258096"

# By PubMed ID
python -m src.cli.main get "25430774" --source pubmed
```

## Configuration

For better results, create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` to add:
- Email for polite API usage
- API keys (optional)
- Rate limits
- Directory preferences

## Common Use Cases

### 1. Literature Review Preparation

```bash
# Broad search
python -m src.cli.main search "systematic review healthcare" \
    --sources pubmed crossref \
    --max-results 100 \
    --output lit_review.json

# Download papers
python -m src.cli.main download lit_review.json
```

### 2. Staying Current

```bash
# Recent papers only
python -m src.cli.main search "quantum computing" \
    --sources arxiv \
    --year-start 2024 \
    --output quantum_2024.json
```

### 3. Finding Seminal Papers

```bash
# Older foundational papers
python -m src.cli.main search "deep learning" \
    --year-end 2015 \
    --sources arxiv \
    --output dl_foundations.json
```

### 4. Cross-Disciplinary Research

```bash
# Multiple fields
python -m src.cli.main search "AI climate science" \
    --sources pubmed arxiv crossref \
    --max-results 50 \
    --output ai_climate.json
```

## Available Databases

### PubMed
- **Best for**: Biomedical and life sciences
- **Coverage**: 35M+ citations
- **Free**: Yes
- **Full text**: PMC articles

```bash
python -m src.cli.main search "cancer immunotherapy" --sources pubmed
```

### arXiv
- **Best for**: Physics, math, CS, preprints
- **Coverage**: 2M+ preprints
- **Free**: Yes
- **Full text**: All papers

```bash
python -m src.cli.main search "neural networks" --sources arxiv
```

### Crossref
- **Best for**: DOI resolution, broad coverage
- **Coverage**: 150M+ records
- **Free**: Yes
- **Full text**: When open access

```bash
python -m src.cli.main search "climate policy" --sources crossref
```

## Tips for Better Results

### 1. Use Specific Terms

❌ Bad: "AI"
✅ Good: "artificial intelligence healthcare diagnosis"

### 2. Combine Sources

```bash
python -m src.cli.main search "protein folding" \
    --sources pubmed arxiv crossref
```

### 3. Filter Wisely

```bash
# Recent review papers only
python -m src.cli.main search "machine learning review" \
    --year-start 2023 \
    --sources pubmed
```

### 4. Save Everything

```bash
# Date-stamped filename
python -m src.cli.main search "my topic" \
    --output "$(date +%Y%m%d)_my_topic.json"
```

## Understanding Results

### Result Ranking

Papers are ranked by:
1. **Title relevance**: Query terms in title (highest weight)
2. **Abstract relevance**: Query terms in abstract
3. **Citations**: More citations = higher rank
4. **Recency**: Newer papers ranked higher
5. **Multi-source**: Papers in multiple databases ranked higher

### Deduplication

The system automatically:
- Merges papers with same DOI
- Merges papers with same PMID
- Detects similar titles (85%+ similarity)
- Combines metadata from all sources

## Next Steps

1. **Read the full README**: [README.md](README.md)
2. **Check usage examples**: [USAGE.md](USAGE.md)
3. **See improvements made**: [IMPROVEMENTS.md](IMPROVEMENTS.md)
4. **Run tests**: `python test_basic.py`

## Troubleshooting

### No results found

Try:
- Simplify query
- Remove year filters
- Try different sources

### Rate limiting errors

Adjust in `.env`:
```bash
PUBMED_RATE_LIMIT=1
```

### PDF downloads failing

Most papers are paywalled. We can only access:
- Open access papers
- arXiv preprints
- PubMed Central papers

## Getting Help

1. Check error messages
2. Review configuration: `python -m src.cli.main config`
3. Try with different parameters
4. Check API status (PubMed, arXiv, Crossref)

## What's Next?

The current implementation provides:
- ✅ Multi-source search
- ✅ Intelligent deduplication
- ✅ Smart ranking
- ✅ PDF download
- ✅ Rich CLI

Coming soon:
- 🔄 Google Scholar integration
- 🔄 AI-powered synthesis
- 🔄 Citation network analysis
- 🔄 Web interface
- 🔄 MCP server for Claude Code

Happy researching! 📚