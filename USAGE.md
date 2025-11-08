# Usage Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Basic Usage

### Quick Search

The fastest way to search:

```bash
python -m src.cli.main quick "your search query"
```

This searches PubMed and arXiv with default settings and shows top 10 results.

### Full Search

For more control:

```bash
python -m src.cli.main search "machine learning healthcare" \
    --sources pubmed arxiv crossref \
    --max-results 50 \
    --year-start 2020 \
    --output results.json
```

### Search with PDF Download

Automatically download open-access PDFs:

```bash
python -m src.cli.main search "CRISPR gene editing" \
    --sources pubmed arxiv \
    --max-results 20 \
    --download
```

### Get Specific Paper

Retrieve a paper by its identifier:

```bash
# By DOI
python -m src.cli.main get "10.1038/nature12373"

# By PubMed ID
python -m src.cli.main get "35360497" --source pubmed

# By arXiv ID
python -m src.cli.main get "2301.08727" --source arxiv
```

## Advanced Features

### Save and Load Results

Save search results for later:

```bash
# Save results
python -m src.cli.main search "quantum computing" \
    --output quantum_results.json

# Download PDFs from saved results
python -m src.cli.main download quantum_results.json --max-papers 30
```

### Filter by Year

```bash
python -m src.cli.main search "climate change" \
    --year-start 2022 \
    --year-end 2024
```

### Choose Specific Sources

```bash
# Only PubMed (biomedical)
python -m src.cli.main search "protein folding" --sources pubmed

# Only arXiv (preprints)
python -m src.cli.main search "neural networks" --sources arxiv

# Multiple sources
python -m src.cli.main search "materials science" \
    --sources pubmed --sources arxiv --sources crossref
```

## Configuration

View current configuration:

```bash
python -m src.cli.main config
```

Create a `.env` file to customize:

```bash
# Copy example
cp .env.example .env

# Edit with your settings
nano .env
```

## Working with Results

### JSON Output Structure

```json
{
  "query": {
    "query": "machine learning",
    "sources": ["pubmed", "arxiv"],
    "max_results": 50
  },
  "statistics": {
    "total_papers": 45,
    "search_time": 2.34,
    "avg_citations": 18.5
  },
  "papers": [
    {
      "title": "Paper Title",
      "authors": [{"name": "John Doe"}],
      "year": 2023,
      "doi": "10.1234/example",
      "abstract": "Abstract text...",
      "citations": 42
    }
  ]
}
```

### Process Results in Python

```python
import json
from pathlib import Path

# Load results
with open('results.json') as f:
    data = json.load(f)

# Access papers
papers = data['papers']
for paper in papers:
    print(f"{paper['title']} ({paper['year']})")
    print(f"Citations: {paper['citations']}")
    print()
```

## Tips and Best Practices

### 1. Start Broad, Then Narrow

```bash
# First, see what's available
python -m src.cli.main quick "gene therapy"

# Then refine with filters
python -m src.cli.main search "gene therapy" \
    --year-start 2022 \
    --sources pubmed \
    --max-results 100
```

### 2. Use Multiple Sources

Different databases have different coverage:
- **PubMed**: Biomedical and life sciences
- **arXiv**: Physics, math, CS, and preprints
- **Crossref**: Broad coverage across all fields

```bash
# Good for biomedical topics
python -m src.cli.main search "cancer immunotherapy" --sources pubmed

# Good for CS/physics
python -m src.cli.main search "quantum algorithms" --sources arxiv

# Good for general academic topics
python -m src.cli.main search "climate policy" --sources crossref
```

### 3. Filter by Recency

For cutting-edge research:

```bash
python -m src.cli.main search "large language models" \
    --year-start 2023 \
    --sources arxiv
```

### 4. Save Everything

Always save your searches:

```bash
python -m src.cli.main search "my topic" \
    --output "$(date +%Y%m%d)_my_topic.json"
```

## Troubleshooting

### Rate Limiting

If you get rate limit errors, adjust in `.env`:

```bash
PUBMED_RATE_LIMIT=2  # Slower requests
```

### No Results

Try:
1. Simplify your query
2. Remove year filters
3. Try different sources
4. Check for typos

### Download Failures

Most papers are behind paywalls. The app can only download:
- Open access papers
- PubMed Central papers
- arXiv preprints
- Unpaywall-indexed papers

For institutional access, you'd need to configure proxy authentication.

## Examples

### Systematic Review Workflow

```bash
# 1. Initial broad search
python -m src.cli.main search "systematic review methodology" \
    --sources pubmed crossref \
    --year-start 2020 \
    --output initial_search.json

# 2. Review results and refine
python -m src.cli.main search "systematic review methodology healthcare" \
    --sources pubmed \
    --year-start 2022 \
    --max-results 100 \
    --output refined_search.json

# 3. Download available PDFs
python -m src.cli.main download refined_search.json \
    --max-papers 50

# 4. Get specific highly-cited paper
python -m src.cli.main get "10.1136/bmj.n71"
```

### Literature Monitoring

```bash
# Weekly search for new papers
python -m src.cli.main search "COVID-19 vaccine efficacy" \
    --year-start $(date -d '7 days ago' +%Y) \
    --output "covid_$(date +%Y%m%d).json"
```

### Cross-disciplinary Research

```bash
# Search multiple fields
python -m src.cli.main search "artificial intelligence climate change" \
    --sources pubmed arxiv crossref \
    --max-results 100 \
    --output ai_climate.json
```

## Next Steps

For more advanced features, check out:
- Python API for programmatic access
- Batch processing scripts
- Integration with reference managers
- Custom export formats