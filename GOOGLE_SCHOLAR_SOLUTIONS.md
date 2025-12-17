# Google Scholar Rate Limiting - Solutions & Alternatives

**Problem:** Google Scholar blocks automated requests with 429 "Too Many Requests" errors
**Status:** Expected behavior - Google Scholar has no official API and actively blocks scrapers

---

## Understanding the Problem

### Why Google Scholar Blocks Requests

1. **No Official API** - Google Scholar does not provide an official API for programmatic access
2. **robots.txt** - Google Scholar's robots.txt forbids web scrapers from scraping most pages
3. **Anti-Bot Detection** - Google uses sophisticated detection to identify automated requests
4. **Rate Limiting** - IP-based tracking limits requests within timeframes
5. **CAPTCHA Challenges** - Suspected bots must solve CAPTCHAs

### Current Error
```
429 Client Error: Too Many Requests for url: https://www.google.com/sorry/index?...
```

---

## Solution Options (Ranked by Recommendation)

### ✅ Option 1: Switch to Semantic Scholar API (RECOMMENDED)

**Pros:**
- ✅ **Official free API** with 214M papers
- ✅ No rate limiting issues (within reasonable limits)
- ✅ AI-powered search and paper summaries
- ✅ 60% open access content (no paywalls)
- ✅ API documentation available
- ✅ Better for programmatic access
- ✅ Identifies hidden connections between research topics

**Cons:**
- Smaller than Google Scholar
- May not have all papers

**Implementation:**
```python
# Install: pip install semanticscholar
from semanticscholar import SemanticScholar

sch = SemanticScholar()
results = sch.search_paper('machine learning', limit=10)
```

**API Endpoint:**
```
https://api.semanticscholar.org/v1/paper/search?query=QUERY
```

**Cost:** FREE with rate limits (100 requests/5 minutes)

---

### ⚠️ Option 2: Use scholarly Python Library

**Pros:**
- Specifically designed for Google Scholar scraping
- Handles pagination and parsing
- Active maintenance

**Cons:**
- Still subject to rate limiting
- Requires careful rate limiting and proxy rotation
- May break if Google Scholar changes HTML structure

**Implementation:**
```python
# Install: pip install scholarly
from scholarly import scholarly

search_query = scholarly.search_pubs('machine learning')
papers = []
for i in range(5):
    try:
        papers.append(next(search_query))
    except StopIteration:
        break
```

**Improvements needed:**
- Add exponential backoff
- Implement proxy rotation
- Add CAPTCHA solving (if necessary)

---

### ⚠️ Option 3: Implement Advanced Anti-Detection Measures

**Required Changes:**

#### 1. Exponential Backoff
```python
import time
from requests.exceptions import HTTPError

def search_with_backoff(self, query, max_retries=5):
    for attempt in range(max_retries):
        try:
            self.rate_limiter.wait_if_needed()
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            return self._parse_results(response.text)
        except HTTPError as e:
            if e.response.status_code == 429:
                # Check Retry-After header
                retry_after = e.response.headers.get('Retry-After', 2 ** attempt)
                wait_time = int(retry_after) if isinstance(retry_after, str) else retry_after
                print(f"⚠ Rate limited. Waiting {wait_time}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
    return []
```

#### 2. Enhanced User-Agent Rotation
```python
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
]

import random
self.session.headers['User-Agent'] = random.choice(user_agents)
```

#### 3. Proxy Rotation
```python
# Requires proxy service (costs money)
proxies = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    # ... more proxies
]

response = self.session.get(
    search_url,
    params=params,
    proxies={'http': random.choice(proxies)},
    timeout=15
)
```

#### 4. Request Throttling (Already Implemented)
```python
# Current implementation (already good)
self.rate_limiter = RateLimiter(0.5)  # 0.5 requests per second
```

**Pros:**
- Stays with Google Scholar
- Potentially works with enough effort

**Cons:**
- 🚫 Violates Google Scholar's Terms of Service
- 🚫 Requires proxy service (costs money)
- 🚫 Brittle - breaks when Google changes detection
- 🚫 Ethical concerns
- 🚫 May still get blocked

---

### 💰 Option 4: Use Third-Party Scraping APIs

#### SerpAPI (Google Scholar API)
```python
# Install: pip install google-search-results
from serpapi import GoogleSearch

params = {
    "engine": "google_scholar",
    "q": "machine learning",
    "api_key": "YOUR_API_KEY"
}

search = GoogleSearch(params)
results = search.get_dict()
```

**Pricing:**
- Free tier: 100 searches/month
- Paid: $50/month for 5,000 searches

#### ScraperAPI
**Pricing:**
- Free tier: 1,000 API calls
- Paid: $49/month for 100,000 calls

#### Apify Google Scholar Scraper
**Pricing:**
- Pay per use: ~$0.25 per 1,000 results

**Pros:**
- ✅ Handles all anti-detection
- ✅ Manages proxies and CAPTCHAs
- ✅ Reliable and maintained

**Cons:**
- 💰 Costs money
- Depends on third-party service

---

### 🔬 Option 5: Alternative Free Academic Search APIs

#### 1. **CORE API** (Highly Recommended)
- 412 million open access articles
- Free API with generous limits
- Official API documentation

```bash
curl "https://api.core.ac.uk/v3/search/works?q=machine learning&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### 2. **Europe PMC API**
- Focus on life sciences
- Free API access
- Official and reliable

```python
import requests
response = requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',
    params={'query': 'machine learning', 'format': 'json'})
```

#### 3. **BASE (Bielefeld Academic Search Engine)**
- 400M+ records
- 60% open access
- OAI-PMH protocol support

#### 4. **OpenAlex API**
- 250M+ works indexed
- Free and open
- Excellent for bibliometrics

```python
import requests
response = requests.get('https://api.openalex.org/works?search=machine learning')
```

---

## Recommended Implementation Strategy

### Phase 1: Immediate (Keep Current System Working) ✅
- ✅ Fix rate limiter calls (DONE)
- ✅ Add graceful degradation (DONE - returns 0 papers)
- ✅ Document expected behavior (DONE)

### Phase 2: Short Term (1-2 weeks)
1. **Implement Semantic Scholar API** as primary alternative
   - Add new provider: `src/search/semantic_scholar.py`
   - Update UI to include "Semantic Scholar" as source option
   - Provides 214M papers with official API

2. **Add exponential backoff** to existing Google Scholar code
   - Retry with increasing delays
   - Check Retry-After header
   - Maximum 3-5 retries

3. **Improve rate limiting**
   - Increase delay to 2-3 seconds between Scholar requests
   - Add randomized delays (jitter)

### Phase 3: Medium Term (1-2 months)
1. **Add CORE API** for open access content
2. **Add OpenAlex API** for comprehensive coverage
3. **Consider SerpAPI** if budget allows (paid service)

### Phase 4: Long Term (3+ months)
1. Implement caching layer to reduce duplicate requests
2. Add user session management for Scholar (cookies)
3. Consider Selenium with stealth mode for Scholar
4. Build comprehensive fallback system

---

## Immediate Action Items

### 1. Add Semantic Scholar Provider

Create `/Users/adrianstiermbp2023/litsearchapp/src/search/semantic_scholar_provider.py`:

```python
"""Semantic Scholar search provider with official API"""

import requests
from typing import List, Optional
from src.models import Paper, SearchQuery, Source, Author, PaperType
from src.search.base import BaseSearchProvider

class SemanticScholarProvider(BaseSearchProvider):
    """Search provider for Semantic Scholar with official API"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(rate_limit=2.0)  # 2 requests per second
        self.source = Source.SEMANTIC_SCHOLAR
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.api_key = api_key

    def search(self, query: SearchQuery) -> List[Paper]:
        """Search Semantic Scholar using official API"""
        papers = []

        try:
            self.rate_limiter.wait_if_needed()

            # Build query parameters
            params = {
                'query': query.query,
                'limit': min(query.max_results, 100),
                'fields': 'paperId,title,abstract,authors,year,citationCount,url,openAccessPdf'
            }

            # Add year filter if specified
            if query.year_start or query.year_end:
                year_filter = f"year:{query.year_start or 1900}-{query.year_end or 2024}"
                params['query'] = f"{query.query} {year_filter}"

            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key

            response = requests.get(
                f"{self.base_url}/paper/search",
                params=params,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()

            for item in data.get('data', []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            print(f"✓ Semantic Scholar: Found {len(papers)} papers")

        except Exception as e:
            print(f"✗ Semantic Scholar search failed: {e}")

        return papers

    def _parse_paper(self, item: dict) -> Optional[Paper]:
        """Parse Semantic Scholar API response"""
        try:
            # Extract authors
            authors = []
            for author_data in item.get('authors', []):
                authors.append(Author(name=author_data.get('name', 'Unknown')))

            # Extract PDF URL
            pdf_url = None
            if item.get('openAccessPdf'):
                pdf_url = item['openAccessPdf'].get('url')

            return Paper(
                title=item.get('title', ''),
                authors=authors,
                year=item.get('year'),
                abstract=item.get('abstract'),
                citations=item.get('citationCount', 0),
                url=item.get('url'),
                pdf_url=pdf_url,
                sources=[Source.SEMANTIC_SCHOLAR],
                paper_type=PaperType.ARTICLE
            )
        except Exception as e:
            print(f"⚠ Failed to parse Semantic Scholar paper: {e}")
            return None

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """Get paper by Semantic Scholar ID"""
        try:
            self.rate_limiter.wait_if_needed()

            response = requests.get(
                f"{self.base_url}/paper/{paper_id}",
                params={'fields': 'paperId,title,abstract,authors,year,citationCount,url,openAccessPdf'},
                timeout=15
            )
            response.raise_for_status()

            return self._parse_paper(response.json())
        except Exception as e:
            print(f"✗ Failed to get paper {paper_id}: {e}")
            return None
```

### 2. Update models.py

Add to Source enum:
```python
class Source(str, Enum):
    PUBMED = "pubmed"
    ARXIV = "arxiv"
    CROSSREF = "crossref"
    GOOGLE_SCHOLAR = "scholar"
    WEB_OF_SCIENCE = "wos"
    SEMANTIC_SCHOLAR = "semantic_scholar"  # ADD THIS
    PMC = "pmc"
```

### 3. Update orchestrator.py

Add Semantic Scholar provider:
```python
from src.search.semantic_scholar_provider import SemanticScholarProvider

self.providers = {
    Source.PUBMED: PubMedSearch(),
    Source.ARXIV: ArxivSearch(),
    Source.CROSSREF: CrossrefSearch(),
    Source.GOOGLE_SCHOLAR: GoogleScholarProvider(ucsb_session=ucsb_session),
    Source.WEB_OF_SCIENCE: WebOfScienceProvider(ucsb_session=ucsb_session),
    Source.SEMANTIC_SCHOLAR: SemanticScholarProvider(),  # ADD THIS
}
```

---

## Comparison Matrix

| Solution | Cost | Reliability | Coverage | Implementation | Ethical |
|----------|------|-------------|----------|----------------|---------|
| **Semantic Scholar API** | Free | ⭐⭐⭐⭐⭐ | 214M papers | Easy | ✅ |
| **CORE API** | Free | ⭐⭐⭐⭐⭐ | 412M papers | Easy | ✅ |
| **OpenAlex API** | Free | ⭐⭐⭐⭐⭐ | 250M papers | Easy | ✅ |
| **scholarly Library** | Free | ⭐⭐ | All of Scholar | Medium | ⚠️ |
| **SerpAPI** | $50/mo | ⭐⭐⭐⭐⭐ | All of Scholar | Easy | ✅ |
| **Advanced Anti-Detection** | Free | ⭐⭐ | All of Scholar | Hard | ❌ |
| **Proxy Rotation** | $20+/mo | ⭐⭐⭐ | All of Scholar | Hard | ⚠️ |

---

## Final Recommendation

### ✅ Best Solution: Semantic Scholar API

**Why:**
1. Official free API - no scraping issues
2. 214 million papers - excellent coverage
3. AI-powered features - added value
4. No rate limiting headaches
5. Ethically sound
6. Easy to implement
7. Better for programmatic access than Scholar

**Implementation Time:** 2-3 hours

**With This Change:**
- Remove Google Scholar rate limiting issues entirely
- Get access to 214M papers with better metadata
- AI-generated summaries for 60M papers
- Official API support and documentation
- No CAPTCHA or proxy issues

### 🎯 Action Plan:
1. ✅ Keep current sources working (PubMed, arXiv, Crossref)
2. 🔄 Add Semantic Scholar API (replaces problematic Scholar scraping)
3. 📊 Add CORE API for open access content
4. 💰 Reserve SerpAPI as paid backup if needed

---

## Conclusion

**Don't fight Google Scholar's anti-bot measures.** Instead, use official APIs that provide similar or better coverage:

- **Semantic Scholar**: Best Google Scholar alternative with official API
- **CORE**: Largest open access database
- **OpenAlex**: Excellent for bibliometrics
- **Current sources** (PubMed, arXiv, Crossref): Keep these - they work great!

**Result:** Better reliability, faster searches, no ethical concerns, and often better metadata quality than scraping Google Scholar.
