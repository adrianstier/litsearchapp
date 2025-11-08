# UCSB Literature Search Agent - Implementation Specification

## Project Overview

An autonomous literature search tool that combines comprehensive discovery (Web of Science, Google Scholar, PubMed) with UCSB institutional library access for PDF retrieval. The system uses Claude Code's MCP server architecture with an intelligent agent that can iteratively refine searches, assess coverage, and synthesize findings.

**Core Capabilities:**
- Multi-source literature discovery (WoS, Scholar, PubMed)
- Intelligent deduplication and cross-referencing
- UCSB library proxy authentication for PDF access
- Agentic search refinement based on quality assessment
- Citation network exploration (forward/backward citations)
- Automated paper synthesis and gap analysis

## Technology Stack

- **Backend**: Python 3.10+
- **MCP Server**: TypeScript/Node.js
- **Database**: SQLite for caching and search history
- **Authentication**: Selenium for UCSB SSO
- **APIs**: 
  - Web of Science API (Clarivate)
  - PubMed E-utilities
  - SerpAPI (Google Scholar)
  - Anthropic API (Claude)
- **PDF Processing**: PyPDF2, pdfplumber
- **CLI**: Click + Rich

## Directory Structure

```
ucsb-literature-agent/
├── README.md
├── pyproject.toml              # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore
│
├── mcp-server/                 # MCP server for Claude Code
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts           # Main MCP server
│   │   ├── tools.ts           # Tool definitions
│   │   └── executor.ts        # Python backend executor
│   └── build/                 # Compiled JS
│
├── src/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── ucsb_auth.py       # UCSB library authentication
│   │   └── session_manager.py # Session persistence
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── orchestrator.py    # Multi-source search coordination
│   │   ├── web_of_science.py  # WoS API client
│   │   ├── google_scholar.py  # Scholar search (SerpAPI + scholarly)
│   │   ├── pubmed.py          # PubMed E-utilities
│   │   └── deduplicator.py    # Cross-reference and deduplicate
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── pdf_retriever.py   # UCSB proxy PDF download
│   │   ├── strategies.py      # Multiple retrieval strategies
│   │   └── citation_network.py # Forward/backward citation search
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── paper_analyzer.py  # Individual paper analysis
│   │   ├── synthesizer.py     # Multi-paper synthesis
│   │   └── gap_finder.py      # Research gap identification
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── literature_agent.py # Autonomous search agent
│   │   ├── quality_assessor.py # Search quality evaluation
│   │   └── refiner.py         # Iterative search refinement
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLite models
│   │   └── cache.py           # Result caching
│   │
│   └── cli/
│       ├── __init__.py
│       └── main.py            # CLI interface
│
├── tests/
│   ├── test_auth.py
│   ├── test_search.py
│   ├── test_retrieval.py
│   └── test_agent.py
│
├── papers/                     # Downloaded PDFs
├── cache/                      # Search cache database
└── output/                     # Generated syntheses
```

## Implementation Steps

### Phase 1: Authentication & Session Management

**File: `src/auth/ucsb_auth.py`**

```python
"""
UCSB Library Authentication Module

Handles:
1. UCSB SSO login via Selenium
2. EZproxy session management
3. Cookie persistence
4. Session validation and refresh
"""

import os
import pickle
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests

class UCSBLibraryAuth:
    """Authenticate and maintain sessions with UCSB library proxy"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        self.session_file = os.path.join(cache_dir, "ucsb_session.pkl")
        self.proxy_url = "https://proxy.library.ucsb.edu/login"
        self.session = requests.Session()
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def authenticate(self, netid: str, password: str, headless: bool = True) -> bool:
        """
        Authenticate through UCSB SSO
        
        Args:
            netid: UCSB NetID
            password: UCSB password
            headless: Run browser in headless mode
            
        Returns:
            bool: Success status
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to proxy login
            driver.get(self.proxy_url)
            
            # Wait for login form
            wait = WebDriverWait(driver, 10)
            
            # Enter credentials (adjust selectors based on actual UCSB SSO page)
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(netid)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Submit form
            submit_button = driver.find_element(By.NAME, "submit")
            submit_button.click()
            
            # Wait for redirect to complete
            time.sleep(3)
            
            # Extract cookies
            cookies = driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # Test session
            if self._validate_session():
                self._save_session()
                return True
            
            return False
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
        finally:
            driver.quit()
    
    def load_session(self) -> bool:
        """Load saved session from disk"""
        if not os.path.exists(self.session_file):
            return False
        
        try:
            with open(self.session_file, 'rb') as f:
                cookies = pickle.load(f)
                self.session.cookies.update(cookies)
            
            return self._validate_session()
        except Exception as e:
            print(f"Session load error: {e}")
            return False
    
    def _validate_session(self) -> bool:
        """Check if current session is valid"""
        try:
            # Test with a known proxied URL
            test_url = f"{self.proxy_url}?url=https://doi.org/10.1038/nature"
            response = self.session.get(test_url, timeout=10)
            
            # Check if we're redirected back to login
            return 'login' not in response.url.lower()
        except:
            return False
    
    def _save_session(self):
        """Persist session cookies to disk"""
        with open(self.session_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)
    
    def get_proxied_url(self, url: str) -> str:
        """Convert a URL to UCSB proxy format"""
        return f"{self.proxy_url}?url={url}"
    
    def get_session(self) -> requests.Session:
        """Get authenticated session for requests"""
        return self.session
```

**File: `src/auth/session_manager.py`**

```python
"""
Session lifecycle management
"""

from datetime import datetime, timedelta
from typing import Optional
import threading

class SessionManager:
    """Manage authentication session lifecycle"""
    
    def __init__(self, auth: 'UCSBLibraryAuth'):
        self.auth = auth
        self.last_validated = None
        self.validation_interval = timedelta(hours=1)
        self._lock = threading.Lock()
    
    def ensure_valid_session(self, netid: Optional[str] = None, 
                           password: Optional[str] = None) -> bool:
        """
        Ensure we have a valid session, re-authenticating if needed
        """
        with self._lock:
            # Try to load existing session
            if self.auth.load_session():
                # Check if we need to revalidate
                if (self.last_validated is None or 
                    datetime.now() - self.last_validated > self.validation_interval):
                    
                    if self.auth._validate_session():
                        self.last_validated = datetime.now()
                        return True
            
            # Need to re-authenticate
            if netid and password:
                if self.auth.authenticate(netid, password):
                    self.last_validated = datetime.now()
                    return True
            
            return False
```

### Phase 2: Multi-Source Search Engine

**File: `src/search/orchestrator.py`**

```python
"""
Search Orchestrator - Coordinates multi-source searches
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchFilters:
    """Search filter parameters"""
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    min_citations: Optional[int] = 0
    article_types: Optional[List[str]] = None
    authors: Optional[List[str]] = None

class SearchOrchestrator:
    """Coordinate searches across multiple sources"""
    
    def __init__(self, session):
        from .web_of_science import WebOfScienceSearch
        from .google_scholar import GoogleScholarSearch
        from .pubmed import PubMedSearch
        from .deduplicator import Deduplicator
        
        self.session = session
        self.wos = WebOfScienceSearch()
        self.scholar = GoogleScholarSearch()
        self.pubmed = PubMedSearch()
        self.dedup = Deduplicator()
    
    def comprehensive_search(
        self,
        query: str,
        sources: List[str] = ['wos', 'scholar', 'pubmed'],
        filters: Optional[SearchFilters] = None,
        max_results_per_source: int = 100
    ) -> Dict:
        """
        Execute parallel searches across multiple sources
        
        Args:
            query: Search query string
            sources: List of sources to search
            filters: Search filters
            max_results_per_source: Max results per source
            
        Returns:
            Dict with merged, deduplicated results and metadata
        """
        print(f"🔍 Searching across {len(sources)} sources...")
        
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {}
            
            if 'wos' in sources:
                futures['wos'] = executor.submit(
                    self.wos.search, query, filters, max_results_per_source
                )
            
            if 'scholar' in sources:
                futures['scholar'] = executor.submit(
                    self.scholar.search, query, filters, max_results_per_source
                )
            
            if 'pubmed' in sources:
                futures['pubmed'] = executor.submit(
                    self.pubmed.search, query, filters, max_results_per_source
                )
            
            # Collect results
            results_by_source = {}
            for source, future in futures.items():
                try:
                    results_by_source[source] = future.result()
                    print(f"  ✓ {source}: {len(results_by_source[source])} papers")
                except Exception as e:
                    print(f"  ✗ {source}: {e}")
                    results_by_source[source] = []
        
        # Deduplicate and merge
        merged_papers = self.dedup.merge_results(results_by_source)
        
        # Rank papers
        ranked_papers = self._rank_papers(merged_papers, query)
        
        return {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'total_unique': len(ranked_papers),
            'by_source': {k: len(v) for k, v in results_by_source.items()},
            'papers': ranked_papers,
            'coverage_analysis': self._analyze_coverage(results_by_source)
        }
    
    def _rank_papers(self, papers: List[Dict], query: str) -> List[Dict]:
        """
        Rank papers by composite relevance score
        
        Score components:
        - Citation count (log scale)
        - Recency
        - Query term matching
        - Multi-source presence
        """
        query_terms = set(query.lower().split())
        current_year = datetime.now().year
        
        for paper in papers:
            score = 0
            
            # Citation score (logarithmic)
            citations = paper.get('citations', 0)
            if citations > 0:
                import math
                score += min(50, 10 * math.log10(citations + 1))
            
            # Recency score
            year = paper.get('year', 2000)
            if year >= current_year - 2:
                score += 30
            elif year >= current_year - 5:
                score += 20
            elif year >= current_year - 10:
                score += 10
            
            # Title relevance
            title = (paper.get('title') or '').lower()
            title_matches = sum(1 for term in query_terms if term in title)
            score += title_matches * 15
            
            # Abstract relevance
            abstract = (paper.get('abstract') or '').lower()
            abstract_matches = sum(1 for term in query_terms if term in abstract)
            score += abstract_matches * 5
            
            # Multi-source bonus
            sources = paper.get('sources', [])
            score += len(sources) * 8
            
            paper['relevance_score'] = score
        
        return sorted(papers, key=lambda x: x['relevance_score'], reverse=True)
    
    def _analyze_coverage(self, results_by_source: Dict) -> Dict:
        """Analyze search coverage across sources"""
        analysis = {
            'unique_to_source': {},
            'total_overlap': 0,
            'recommendation': ''
        }
        
        # Calculate overlaps
        all_dois = {}
        for source, papers in results_by_source.items():
            dois = {p['doi'] for p in papers if p.get('doi')}
            all_dois[source] = dois
        
        # Count unique papers per source
        for source, dois in all_dois.items():
            other_dois = set().union(*[
                all_dois[s] for s in all_dois if s != source
            ])
            unique = dois - other_dois
            analysis['unique_to_source'][source] = len(unique)
        
        # Provide recommendation
        if any(v > 20 for v in analysis['unique_to_source'].values()):
            analysis['recommendation'] = "High unique content per source - search is comprehensive"
        else:
            analysis['recommendation'] = "Consider additional search terms or sources"
        
        return analysis
```

**File: `src/search/web_of_science.py`**

```python
"""
Web of Science API client
"""

import os
import requests
from typing import List, Dict, Optional
import time

class WebOfScienceSearch:
    """Search Web of Science via Clarivate API"""
    
    def __init__(self):
        self.api_key = os.getenv('WOS_API_KEY')
        self.base_url = "https://api.clarivate.com/api/wos"
    
    def search(self, query: str, filters: Optional['SearchFilters'] = None, 
               max_results: int = 100) -> List[Dict]:
        """
        Search Web of Science
        
        Args:
            query: Search query
            filters: Optional filters
            max_results: Maximum results to return
            
        Returns:
            List of paper dictionaries
        """
        if not self.api_key:
            print("⚠️  WoS API key not found, skipping WoS search")
            return []
        
        wos_query = self._build_query(query, filters)
        
        headers = {'X-ApiKey': self.api_key}
        params = {
            'databaseId': 'WOS',
            'usrQuery': wos_query,
            'count': 100,
            'firstRecord': 1
        }
        
        all_papers = []
        
        while len(all_papers) < max_results:
            try:
                response = requests.get(
                    f"{self.base_url}/query",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                records = data.get('Data', {}).get('Records', {}).get('records', {}).get('REC', [])
                
                if not records:
                    break
                
                for record in records:
                    paper = self._parse_record(record)
                    if paper:
                        all_papers.append(paper)
                
                if len(records) < params['count']:
                    break
                
                params['firstRecord'] += params['count']
                time.sleep(0.5)
                
            except Exception as e:
                print(f"WoS search error: {e}")
                break
        
        return all_papers[:max_results]
    
    def _build_query(self, query: str, filters: Optional['SearchFilters']) -> str:
        """Build WoS query syntax"""
        wos_query = f'TS=("{query}")'
        
        if filters:
            if filters.year_start and filters.year_end:
                wos_query += f' AND PY=({filters.year_start}-{filters.year_end})'
            
            if filters.authors:
                author_clauses = [f'AU=({author})' for author in filters.authors]
                wos_query += ' AND (' + ' OR '.join(author_clauses) + ')'
        
        return wos_query
    
    def _parse_record(self, record: Dict) -> Optional[Dict]:
        """Parse WoS record into standard format"""
        try:
            static_data = record.get('static_data', {})
            summary = static_data.get('summary', {})
            
            # Extract title
            titles = summary.get('titles', {}).get('title', [])
            title = next((t.get('content') for t in titles if t.get('type') == 'item'), None)
            
            # Extract authors
            authors_data = static_data.get('fullrecord_metadata', {}).get('authors', {}).get('author', [])
            authors = [a.get('wos_standard', '') for a in authors_data]
            
            # Extract DOI
            ids = static_data.get('fullrecord_metadata', {}).get('normalized_doctypes', {}).get('doctype', [])
            doi = None
            for id_data in summary.get('identifiers', {}).get('identifier', []):
                if id_data.get('type') == 'doi':
                    doi = id_data.get('value')
                    break
            
            # Extract year
            pub_info = summary.get('pub_info', {})
            year = int(pub_info.get('pubyear', 0))
            
            # Extract citations
            citations = record.get('dynamic_data', {}).get('citation_related', {}).get('tc_list', {}).get('silo_tc', {}).get('local_count', 0)
            
            return {
                'title': title,
                'authors': authors,
                'year': year,
                'doi': doi,
                'citations': int(citations) if citations else 0,
                'abstract': None,  # WoS API may not include abstracts in basic query
                'source': 'wos',
                'sources': ['wos']
            }
        except Exception as e:
            print(f"Parse error: {e}")
            return None
```

**File: `src/search/google_scholar.py`**

```python
"""
Google Scholar search client
"""

import os
import requests
from typing import List, Dict, Optional
import time
from scholarly import scholarly

class GoogleScholarSearch:
    """Search Google Scholar via SerpAPI or scholarly library"""
    
    def __init__(self):
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.use_serpapi = bool(self.serpapi_key)
    
    def search(self, query: str, filters: Optional['SearchFilters'] = None,
               max_results: int = 100) -> List[Dict]:
        """Search Google Scholar"""
        if self.use_serpapi:
            return self._search_serpapi(query, filters, max_results)
        else:
            return self._search_scholarly(query, filters, max_results)
    
    def _search_serpapi(self, query: str, filters: Optional['SearchFilters'],
                       max_results: int) -> List[Dict]:
        """Search using SerpAPI (paid, reliable)"""
        url = "https://serpapi.com/search"
        
        params = {
            'engine': 'google_scholar',
            'q': query,
            'api_key': self.serpapi_key,
            'num': 20
        }
        
        if filters:
            if filters.year_start:
                params['as_ylo'] = filters.year_start
            if filters.year_end:
                params['as_yhi'] = filters.year_end
        
        all_papers = []
        start = 0
        
        while len(all_papers) < max_results and start < 500:
            params['start'] = start
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                results = data.get('organic_results', [])
                
                if not results:
                    break
                
                for result in results:
                    paper = self._parse_serpapi_result(result)
                    if paper:
                        all_papers.append(paper)
                
                start += 20
                time.sleep(1)
                
            except Exception as e:
                print(f"SerpAPI error: {e}")
                break
        
        return all_papers[:max_results]
    
    def _search_scholarly(self, query: str, filters: Optional['SearchFilters'],
                         max_results: int) -> List[Dict]:
        """Search using scholarly library (free, slower)"""
        papers = []
        
        try:
            search_query = scholarly.search_pubs(query)
            
            for i, paper in enumerate(search_query):
                if i >= max_results:
                    break
                
                parsed = self._parse_scholarly_result(paper)
                if parsed:
                    papers.append(parsed)
                
                time.sleep(2)  # Rate limiting
                
        except Exception as e:
            print(f"Scholarly search error: {e}")
        
        return papers
    
    def _parse_serpapi_result(self, result: Dict) -> Optional[Dict]:
        """Parse SerpAPI result"""
        try:
            pub_info = result.get('publication_info', {})
            
            return {
                'title': result.get('title'),
                'authors': pub_info.get('authors', []),
                'year': self._extract_year(pub_info.get('summary', '')),
                'citations': result.get('inline_links', {}).get('cited_by', {}).get('total', 0),
                'abstract': result.get('snippet'),
                'link': result.get('link'),
                'pdf_link': result.get('resources', [{}])[0].get('link') if result.get('resources') else None,
                'doi': None,  # Scholar doesn't always have DOI
                'source': 'scholar',
                'sources': ['scholar'],
                'scholar_id': result.get('result_id')
            }
        except:
            return None
    
    def _parse_scholarly_result(self, paper: Dict) -> Optional[Dict]:
        """Parse scholarly library result"""
        try:
            bib = paper.get('bib', {})
            
            return {
                'title': bib.get('title'),
                'authors': bib.get('author', []),
                'year': int(bib.get('pub_year', 0)) if bib.get('pub_year') else None,
                'citations': paper.get('num_citations', 0),
                'abstract': bib.get('abstract'),
                'link': paper.get('pub_url'),
                'pdf_link': paper.get('eprint_url'),
                'doi': None,
                'source': 'scholar',
                'sources': ['scholar']
            }
        except:
            return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        import re
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return int(match.group()) if match else None
```

**File: `src/search/pubmed.py`**

```python
"""
PubMed E-utilities client
"""

import requests
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import time

class PubMedSearch:
    """Search PubMed via E-utilities API"""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def search(self, query: str, filters: Optional['SearchFilters'] = None,
               max_results: int = 100) -> List[Dict]:
        """Search PubMed"""
        
        # Step 1: Search for IDs
        search_url = f"{self.base_url}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': self._build_query(query, filters),
            'retmax': min(max_results, 500),
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            ids = data.get('esearchresult', {}).get('idlist', [])
            
            if not ids:
                return []
            
            # Step 2: Fetch details
            return self._fetch_details(ids)
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    
    def _build_query(self, query: str, filters: Optional['SearchFilters']) -> str:
        """Build PubMed query"""
        pm_query = query
        
        if filters:
            if filters.year_start and filters.year_end:
                pm_query += f' AND {filters.year_start}:{filters.year_end}[pdat]'
            
            if filters.article_types:
                types = ' OR '.join([f'{t}[pt]' for t in filters.article_types])
                pm_query += f' AND ({types})'
        
        return pm_query
    
    def _fetch_details(self, ids: List[str]) -> List[Dict]:
        """Fetch full details for PubMed IDs"""
        fetch_url = f"{self.base_url}efetch.fcgi"
        
        # Fetch in batches of 100
        all_papers = []
        
        for i in range(0, len(ids), 100):
            batch_ids = ids[i:i+100]
            
            params = {
                'db': 'pubmed',
                'id': ','.join(batch_ids),
                'retmode': 'xml'
            }
            
            try:
                response = requests.get(fetch_url, params=params, timeout=30)
                response.raise_for_status()
                
                papers = self._parse_xml(response.text)
                all_papers.extend(papers)
                
                time.sleep(0.5)  # Be nice to NCBI
                
            except Exception as e:
                print(f"Fetch error: {e}")
                continue
        
        return all_papers
    
    def _parse_xml(self, xml_text: str) -> List[Dict]:
        """Parse PubMed XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall('.//PubmedArticle'):
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)
        except Exception as e:
            print(f"XML parse error: {e}")
        
        return papers
    
    def _parse_article(self, article: ET.Element) -> Optional[Dict]:
        """Parse single PubMed article"""
        try:
            medline = article.find('.//MedlineCitation')
            
            # Title
            title_elem = medline.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else None
            
            # Authors
            authors = []
            for author in medline.findall('.//Author'):
                last_name = author.find('LastName')
                fore_name = author.find('ForeName')
                if last_name is not None:
                    name = last_name.text
                    if fore_name is not None:
                        name = f"{fore_name.text} {name}"
                    authors.append(name)
            
            # Year
            pub_date = medline.find('.//PubDate')
            year = None
            if pub_date is not None:
                year_elem = pub_date.find('Year')
                if year_elem is not None:
                    year = int(year_elem.text)
            
            # Abstract
            abstract_elem = medline.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else None
            
            # PMID
            pmid_elem = medline.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # DOI
            doi = None
            for article_id in article.findall('.//ArticleId'):
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break
            
            return {
                'title': title,
                'authors': authors,
                'year': year,
                'doi': doi,
                'pmid': pmid,
                'abstract': abstract,
                'citations': 0,  # PubMed doesn't provide citation counts
                'source': 'pubmed',
                'sources': ['pubmed']
            }
        except Exception as e:
            print(f"Article parse error: {e}")
            return None
```

**File: `src/search/deduplicator.py`**

```python
"""
Cross-reference and deduplicate search results
"""

from typing import List, Dict
from difflib import SequenceMatcher

class Deduplicator:
    """Deduplicate and merge papers from multiple sources"""
    
    def merge_results(self, results_by_source: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Merge results from multiple sources, deduplicating by DOI and title
        
        Args:
            results_by_source: Dict mapping source name to list of papers
            
        Returns:
            List of deduplicated papers with merged metadata
        """
        # First pass: group by DOI
        doi_map = {}
        no_doi = []
        
        for source, papers in results_by_source.items():
            for paper in papers:
                # Ensure sources is a list
                if 'sources' not in paper:
                    paper['sources'] = [source]
                elif source not in paper['sources']:
                    paper['sources'].append(source)
                
                doi = paper.get('doi')
                if doi:
                    if doi in doi_map:
                        doi_map[doi] = self._merge_papers(doi_map[doi], paper)
                    else:
                        doi_map[doi] = paper
                else:
                    no_doi.append(paper)
        
        # Second pass: match papers without DOI by title similarity
        merged = list(doi_map.values())
        
        for paper in no_doi:
            matched = False
            for existing in merged:
                if self._titles_similar(paper.get('title', ''), existing.get('title', '')):
                    existing = self._merge_papers(existing, paper)
                    matched = True
                    break
            
            if not matched:
                merged.append(paper)
        
        return merged
    
    def _merge_papers(self, paper1: Dict, paper2: Dict) -> Dict:
        """
        Merge two paper records, preferring non-null values
        """
        merged = paper1.copy()
        
        # Merge sources
        sources = set(merged.get('sources', []))
        sources.update(paper2.get('sources', []))
        merged['sources'] = list(sources)
        
        # Prefer non-null values
        for key, value in paper2.items():
            if value and not merged.get(key):
                merged[key] = value
            elif key == 'citations':
                # Take max citation count
                merged[key] = max(merged.get(key, 0), value)
            elif key == 'abstract' and value and len(str(value)) > len(str(merged.get(key, ''))):
                # Prefer longer abstract
                merged[key] = value
        
        return merged
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.85) -> bool:
        """
        Check if two titles are similar enough to be the same paper
        """
        if not title1 or not title2:
            return False
        
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        similarity = SequenceMatcher(None, t1, t2).ratio()
        return similarity >= threshold
```

### Phase 3: PDF Retrieval via UCSB Proxy

**File: `src/retrieval/pdf_retriever.py`**

```python
"""
PDF retrieval through UCSB library access
"""

import os
import requests
from typing import Tuple, List, Dict, Optional
from urllib.parse import quote
import time

class PDFRetriever:
    """Download PDFs through UCSB library proxy"""
    
    def __init__(self, auth_session: requests.Session):
        self.session = auth_session
        self.proxy_base = "https://proxy.library.ucsb.edu/login?url="
        
        # Publisher URL patterns
        self.publisher_patterns = {
            '10.1002': 'https://onlinelibrary.wiley.com/doi/pdfdirect/',
            '10.1007': 'https://link.springer.com/content/pdf/',
            '10.1016': 'https://www.sciencedirect.com/science/article/pii/',
            '10.1038': 'https://www.nature.com/articles/',
            '10.1021': 'https://pubs.acs.org/doi/pdf/',
            '10.1080': 'https://www.tandfonline.com/doi/pdf/',
        }
    
    def get_pdf(self, paper: Dict, save_dir: str = './papers') -> Tuple[bool, str]:
        """
        Try multiple strategies to download PDF
        
        Args:
            paper: Paper metadata dict
            save_dir: Directory to save PDFs
            
        Returns:
            (success, filepath_or_error)
        """
        os.makedirs(save_dir, exist_ok=True)
        
        # Create safe filename
        title = paper.get('title', 'unknown')[:100]
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' 
                           for c in title).strip()
        
        # Add first author and year if available
        if paper.get('authors'):
            first_author = paper['authors'][0].split()[-1]  # Last name
            safe_title = f"{first_author}_{paper.get('year', '')}_{safe_title}"
        
        filepath = os.path.join(save_dir, f"{safe_title}.pdf")
        
        # Check if already downloaded
        if os.path.exists(filepath):
            return True, filepath
        
        # Try strategies in order
        strategies = [
            ('DOI', self._try_doi),
            ('PubMed Central', self._try_pmc),
            ('Direct Link', self._try_direct_link),
            ('Publisher', self._try_publisher),
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                if strategy_func(paper, filepath):
                    print(f"  ✓ Downloaded via {strategy_name}")
                    return True, filepath
            except Exception as e:
                print(f"  ✗ {strategy_name} failed: {e}")
                continue
        
        return False, "All retrieval strategies failed"
    
    def _try_doi(self, paper: Dict, filepath: str) -> bool:
        """Try DOI resolution through UCSB proxy"""
        doi = paper.get('doi')
        if not doi:
            return False
        
        doi_url = f"https://doi.org/{doi}"
        proxied_url = f"{self.proxy_base}{quote(doi_url)}"
        
        return self._download(proxied_url, filepath)
    
    def _try_pmc(self, paper: Dict, filepath: str) -> bool:
        """Try PubMed Central (free full text)"""
        pmid = paper.get('pmid')
        pmcid = paper.get('pmcid')
        
        # If we have PMC ID, try direct
        if pmcid:
            pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
            if self._download(pmc_url, filepath):
                return True
        
        # Try to find PMC ID from PMID
        if pmid:
            link_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
            params = {
                'dbfrom': 'pubmed',
                'db': 'pmc',
                'id': pmid,
                'retmode': 'json'
            }
            
            try:
                response = requests.get(link_url, params=params, timeout=10)
                data = response.json()
                
                linksets = data.get('linksets', [])
                if linksets:
                    for linkset in linksets[0].get('linksetdbs', []):
                        if linkset.get('linkname') == 'pubmed_pmc':
                            pmc_id = linkset['links'][0]
                            pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
                            if self._download(pmc_url, filepath):
                                return True
            except:
                pass
        
        return False
    
    def _try_direct_link(self, paper: Dict, filepath: str) -> bool:
        """Try direct PDF link"""
        pdf_link = paper.get('pdf_link')
        if not pdf_link:
            return False
        
        # Try without proxy first (for open access)
        if self._download(pdf_link, filepath):
            return True
        
        # Try with proxy
        proxied_url = f"{self.proxy_base}{quote(pdf_link)}"
        return self._download(proxied_url, filepath)
    
    def _try_publisher(self, paper: Dict, filepath: str) -> bool:
        """Try publisher-specific URL patterns"""
        doi = paper.get('doi')
        if not doi:
            return False
        
        doi_prefix = doi.split('/')[0]
        
        if doi_prefix in self.publisher_patterns:
            base_url = self.publisher_patterns[doi_prefix]
            
            # Construct publisher URL
            if doi_prefix == '10.1016':  # Elsevier
                pii = doi.split('/')[-1]
                url = f"{base_url}{pii}/pdfft"
            elif doi_prefix in ['10.1007', '10.1002']:  # Springer, Wiley
                url = f"{base_url}{doi}.pdf"
            else:
                url = f"{base_url}{doi}"
            
            proxied_url = f"{self.proxy_base}{quote(url)}"
            return self._download(proxied_url, filepath)
        
        return False
    
    def _download(self, url: str, filepath: str) -> bool:
        """
        Download file from URL
        
        Returns True if successfully downloaded a valid PDF
        """
        try:
            response = self.session.get(
                url,
                stream=True,
                timeout=30,
                allow_redirects=True
            )
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/pdf' in content_type or 'application/octet-stream' in content_type:
                # Download file
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify it's a valid PDF
                with open(filepath, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        return True
                
                # Not a valid PDF, remove it
                os.remove(filepath)
        
        except Exception as e:
            pass
        
        return False
    
    def batch_download(self, papers: List[Dict], 
                      max_concurrent: int = 3) -> Dict:
        """
        Download multiple papers with progress tracking
        
        Args:
            papers: List of paper dicts
            max_concurrent: Max concurrent downloads
            
        Returns:
            Dict with download results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {
            'successful': [],
            'failed': [],
            'total': len(papers)
        }
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_paper = {
                executor.submit(self.get_pdf, paper): paper
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
                            'reason': result
                        })
                except Exception as e:
                    results['failed'].append({
                        'paper': paper,
                        'reason': str(e)
                    })
                
                # Progress update
                completed = len(results['successful']) + len(results['failed'])
                print(f"Progress: {completed}/{results['total']} "
                      f"({len(results['successful'])} successful)")
        
        return results
```

### Phase 4: Agentic Search Agent

**File: `src/agent/literature_agent.py`**

```python
"""
Autonomous literature search agent
"""

import os
from typing import List, Dict, Optional
from anthropic import Anthropic
import json

class LiteratureAgent:
    """
    Autonomous agent that can:
    - Conduct iterative literature searches
    - Assess search quality
    - Refine queries
    - Select papers intelligently
    - Synthesize findings
    """
    
    def __init__(self, orchestrator, retriever):
        self.orchestrator = orchestrator
        self.retriever = retriever
        self.claude = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.search_history = []
    
    def comprehensive_review(
        self,
        research_question: str,
        max_papers: int = 50,
        min_quality_score: float = 0.7
    ) -> Dict:
        """
        Autonomously conduct comprehensive literature review
        
        Args:
            research_question: The research question
            max_papers: Maximum papers to download
            min_quality_score: Minimum quality threshold
            
        Returns:
            Complete review results with synthesis
        """
        print(f"\n{'='*70}")
        print(f"🤖 AUTONOMOUS LITERATURE REVIEW")
        print(f"{'='*70}")
        print(f"Research Question: {research_question}")
        print(f"Target Papers: {max_papers}")
        print(f"{'='*70}\n")
        
        # Phase 1: Initial Search
        print("📚 Phase 1: Initial Discovery Search")
        print("-" * 70)
        initial_results = self.orchestrator.comprehensive_search(
            query=research_question,
            sources=['wos', 'scholar', 'pubmed'],
            max_results_per_source=100
        )
        
        print(f"✓ Found {initial_results['total_unique']} unique papers")
        print(f"  Distribution: {initial_results['by_source']}")
        
        self.search_history.append({
            'phase': 'initial',
            'query': research_question,
            'results': initial_results
        })
        
        # Phase 2: Quality Assessment
        print("\n🔍 Phase 2: Search Quality Assessment")
        print("-" * 70)
        assessment = self._assess_search_quality(initial_results, research_question)
        
        print(f"Coverage Score: {assessment['coverage_score']:.2f}")
        print(f"Needs Refinement: {assessment['needs_refinement']}")
        if assessment['potential_gaps']:
            print(f"Potential Gaps: {', '.join(assessment['potential_gaps'][:3])}")
        
        # Phase 3: Refinement if needed
        all_results = initial_results
        
        if assessment['needs_refinement']:
            print(f"\n🎯 Phase 3: Search Refinement")
            print(f"Reason: {assessment['reason']}")
            print("-" * 70)
            
            refined_results = self._refine_search(
                initial_results,
                research_question,
                assessment
            )
            
            if refined_results:
                print(f"✓ Refinement added {refined_results['total_unique']} papers")
                all_results = self._merge_search_results([initial_results, refined_results])
        
        # Phase 4: Paper Selection
        print(f"\n🎓 Phase 4: Intelligent Paper Selection")
        print("-" * 70)
        selected_papers = self._select_papers(
            all_results['papers'],
            research_question,
            max_papers,
            min_quality_score
        )
        
        print(f"✓ Selected {len(selected_papers)} papers for download")
        
        # Phase 5: Download
        print(f"\n⬇️  Phase 5: PDF Download via UCSB Library")
        print("-" * 70)
        download_results = self.retriever.batch_download(selected_papers)
        
        print(f"✓ Successfully downloaded: {len(download_results['successful'])}")
        print(f"✗ Failed: {len(download_results['failed'])}")
        
        # Phase 6: Synthesis
        print(f"\n✍️  Phase 6: Literature Synthesis")
        print("-" * 70)
        
        if download_results['successful']:
            synthesis = self._synthesize_papers(
                download_results['successful'],
                research_question
            )
            print("✓ Synthesis complete")
        else:
            synthesis = "No papers downloaded successfully for synthesis"
        
        # Final summary
        print(f"\n{'='*70}")
        print("REVIEW COMPLETE")
        print(f"{'='*70}")
        
        return {
            'research_question': research_question,
            'summary': {
                'total_found': all_results['total_unique'],
                'selected': len(selected_papers),
                'downloaded': len(download_results['successful']),
                'failed': len(download_results['failed'])
            },
            'papers': download_results['successful'],
            'failed_downloads': download_results['failed'],
            'synthesis': synthesis,
            'search_history': self.search_history
        }
    
    def _assess_search_quality(self, results: Dict, question: str) -> Dict:
        """Use Claude to assess search comprehensiveness"""
        
        top_papers = "\n".join([
            f"{i+1}. {p['title']} ({p.get('year')}, "
            f"{p.get('citations', 0)} citations, "
            f"sources: {', '.join(p.get('sources', []))})"
            for i, p in enumerate(results['papers'][:20])
        ])
        
        prompt = f"""Assess this literature search for comprehensiveness.

Research Question: {question}

Search Results Summary:
- Total unique papers: {results['total_unique']}
- Sources searched: {list(results['by_source'].keys())}
- Papers per source: {results['by_source']}

Top 20 Papers:
{top_papers}

Provide assessment as JSON:
{{
  "needs_refinement": true/false,
  "reason": "brief explanation",
  "coverage_score": 0.0-1.0,
  "recommendations": ["specific suggestion 1", "suggestion 2"],
  "potential_gaps": ["gap 1", "gap 2"]
}}

Consider:
1. Are major subtopics covered?
2. Is there diversity in publication years?
3. Are both foundational and recent papers present?
4. Are different methodological approaches represented?
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            text = response.content[0].text
            # Remove markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
        except:
            return {
                'needs_refinement': False,
                'reason': 'Assessment parse error',
                'coverage_score': 0.7,
                'recommendations': [],
                'potential_gaps': []
            }
    
    def _refine_search(self, initial_results: Dict, question: str, 
                      assessment: Dict) -> Optional[Dict]:
        """Refine search based on assessment"""
        
        if not assessment.get('recommendations'):
            return None
        
        # Use Claude to generate refined query
        prompt = f"""Based on this literature search assessment, suggest 2-3 refined search queries.

Original Question: {question}
Current Coverage: {assessment['coverage_score']}
Gaps: {assessment['potential_gaps']}
Recommendations: {assessment['recommendations']}

Provide 2-3 specific search queries that would fill the gaps.
Return as JSON array: ["query 1", "query 2", "query 3"]
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            text = response.content[0].text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            refined_queries = json.loads(text.strip())
            
            # Execute refined searches
            all_refined = []
            for query in refined_queries[:2]:  # Limit to 2 refinements
                print(f"  Refined query: {query}")
                refined = self.orchestrator.comprehensive_search(
                    query=query,
                    sources=['scholar', 'pubmed'],  # Faster sources
                    max_results_per_source=50
                )
                all_refined.append(refined)
            
            return self._merge_search_results(all_refined)
        
        except:
            return None
    
    def _select_papers(self, papers: List[Dict], question: str,
                      max_papers: int, min_score: float) -> List[Dict]:
        """Intelligently select most relevant papers"""
        
        # Filter by relevance score
        candidates = [p for p in papers 
                     if p.get('relevance_score', 0) >= min_score * 100]
        
        if len(candidates) <= max_papers:
            return candidates[:max_papers]
        
        # Use Claude for selection
        papers_summary = "\n\n".join([
            f"**Paper {i+1}**\n"
            f"Title: {p['title']}\n"
            f"Authors: {', '.join(p.get('authors', [])[:3])}\n"
            f"Year: {p.get('year')}\n"
            f"Citations: {p.get('citations', 0)}\n"
            f"Sources: {', '.join(p.get('sources', []))}\n"
            f"Score: {p.get('relevance_score', 0):.1f}"
            for i, p in enumerate(candidates[:max_papers * 2])
        ])
        
        prompt = f"""Select the {max_papers} most valuable papers for: "{question}"

Prioritize:
1. Direct relevance to research question
2. Methodological soundness (prefer primary research, systematic reviews)
3. High citation impact
4. Recent publication (when appropriate)
5. Diversity (avoid redundancy, cover different aspects)

Papers (choose from first {min(len(candidates), max_papers * 2)}):
{papers_summary}

Return JSON array of paper numbers: [1, 5, 7, 12, ...]
Select exactly {max_papers} papers.
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            text = response.content[0].text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            indices = json.loads(text.strip())
            candidate_pool = candidates[:max_papers * 2]
            
            return [candidate_pool[i-1] for i in indices 
                   if 0 < i <= len(candidate_pool)]
        except:
            # Fallback: top scoring papers
            return candidates[:max_papers]
    
    def _synthesize_papers(self, successful_downloads: List[Dict],
                          question: str) -> str:
        """Synthesize findings from downloaded papers"""
        
        # For now, create summary without full text analysis
        # (Full PDF parsing would be added in production)
        
        papers_list = "\n\n".join([
            f"**{i+1}. {item['paper']['title']}**\n"
            f"Authors: {', '.join(item['paper'].get('authors', [])[:3])}\n"
            f"Year: {item['paper'].get('year')}\n"
            f"Citations: {item['paper'].get('citations', 0)}\n"
            f"Abstract: {item['paper'].get('abstract', 'N/A')[:300]}..."
            for i, item in enumerate(successful_downloads[:20])
        ])
        
        prompt = f"""Synthesize these papers addressing: "{question}"

Provide:
1. **Overview**: Main themes and findings (2-3 paragraphs)
2. **Key Consensus**: What do most papers agree on?
3. **Contradictions**: Where do findings diverge?
4. **Methodological Approaches**: Common methods used
5. **Research Gaps**: What hasn't been adequately studied?
6. **Future Directions**: Promising areas for research

Papers:
{papers_list}

Write in clear academic prose suitable for a literature review.
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _merge_search_results(self, results_list: List[Dict]) -> Dict:
        """Merge multiple search results"""
        from ..search.deduplicator import Deduplicator
        
        dedup = Deduplicator()
        
        # Combine all papers
        all_papers = []
        combined_by_source = {}
        
        for results in results_list:
            all_papers.extend(results['papers'])
            for source, count in results['by_source'].items():
                combined_by_source[source] = combined_by_source.get(source, 0) + count
        
        # Deduplicate
        merged_papers = dedup.merge_results({'combined': all_papers})
        
        return {
            'total_unique': len(merged_papers),
            'by_source': combined_by_source,
            'papers': merged_papers
        }
```

### Phase 5: MCP Server for Claude Code

**File: `mcp-server/package.json`**

```json
{
  "name": "ucsb-literature-mcp",
  "version": "1.0.0",
  "type": "module",
  "main": "build/index.js",
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch",
    "start": "node build/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

**File: `mcp-server/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**File: `mcp-server/src/index.ts`**

```typescript
#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// MCP Server for UCSB Literature Search
const server = new Server(
  {
    name: "ucsb-literature-search",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const tools: Tool[] = [
  {
    name: "search_literature",
    description:
      "Search academic literature across Web of Science, Google Scholar, and PubMed. " +
      "Returns ranked, deduplicated results with metadata including titles, authors, " +
      "citations, abstracts, and DOIs.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "The search query (e.g., 'coral thermal stress gene expression')",
        },
        sources: {
          type: "array",
          items: {
            type: "string",
            enum: ["wos", "scholar", "pubmed"],
          },
          default: ["wos", "scholar", "pubmed"],
          description: "Which databases to search",
        },
        year_start: {
          type: "number",
          description: "Start year for date filter (optional)",
        },
        year_end: {
          type: "number",
          description: "End year for date filter (optional)",
        },
        max_results: {
          type: "number",
          default: 50,
          description: "Maximum total results to return",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "download_papers",
    description:
      "Download PDFs for selected papers through UCSB library proxy authentication. " +
      "Tries multiple retrieval strategies including DOI resolution, PubMed Central, " +
      "direct links, and publisher-specific URLs.",
    inputSchema: {
      type: "object",
      properties: {
        paper_ids: {
          type: "array",
          items: { type: "string" },
          description:
            "Array of paper identifiers (DOIs or titles) to download",
        },
        max_downloads: {
          type: "number",
          default: 50,
          description: "Maximum number of papers to download",
        },
      },
      required: ["paper_ids"],
    },
  },
  {
    name: "autonomous_review",
    description:
      "Conduct a fully autonomous literature review. The agent will: " +
      "(1) Perform initial comprehensive search, " +
      "(2) Assess search quality and identify gaps, " +
      "(3) Refine search if needed, " +
      "(4) Intelligently select most relevant papers, " +
      "(5) Download papers via UCSB access, " +
      "(6) Synthesize findings. " +
      "This is the recommended tool for complex literature research.",
    inputSchema: {
      type: "object",
      properties: {
        research_question: {
          type: "string",
          description:
            "The research question or topic to review (e.g., 'What are the molecular mechanisms of coral bleaching and recovery?')",
        },
        max_papers: {
          type: "number",
          default: 30,
          description: "Target number of papers to download and analyze",
        },
        min_quality_score: {
          type: "number",
          default: 0.7,
          description: "Minimum quality/relevance threshold (0.0-1.0)",
        },
      },
      required: ["research_question"],
    },
  },
  {
    name: "synthesize_papers",
    description:
      "Synthesize findings from previously downloaded papers. " +
      "Provides overview, consensus findings, contradictions, methodological approaches, " +
      "research gaps, and future directions.",
    inputSchema: {
      type: "object",
      properties: {
        paper_paths: {
          type: "array",
          items: { type: "string" },
          description: "File paths to downloaded PDFs",
        },
        focus: {
          type: "string",
          description:
            "Specific aspect to focus synthesis on (e.g., 'methods', 'gene expression patterns')",
        },
      },
      required: ["paper_paths"],
    },
  },
];

// Register tool list handler
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

// Execute Python backend
async function executePythonTool(
  toolName: string,
  args: Record<string, unknown>
): Promise<string> {
  return new Promise((resolve, reject) => {
    // Path to Python CLI
    const pythonScript = path.join(__dirname, "../../src/cli/main.py");

    // Execute Python with arguments
    const pythonProcess = spawn("python", [
      pythonScript,
      "execute-tool",
      toolName,
      JSON.stringify(args),
    ]);

    let output = "";
    let error = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      error += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Python process failed: ${error}`));
      } else {
        resolve(output);
      }
    });
  });
}

// Register tool execution handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const result = await executePythonTool(name, args || {});

    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("UCSB Literature Search MCP Server running");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
```

### Phase 6: CLI Interface

**File: `src/cli/main.py`**

```python
#!/usr/bin/env python3
"""
CLI interface for UCSB Literature Search Agent
"""

import click
import os
import sys
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.auth.ucsb_auth import UCSBLibraryAuth
from src.auth.session_manager import SessionManager
from src.search.orchestrator import SearchOrchestrator
from src.retrieval.pdf_retriever import PDFRetriever
from src.agent.literature_agent import LiteratureAgent

console = Console()

# Load environment variables
load_dotenv()

@click.group()
def cli():
    """UCSB Literature Search Agent - Autonomous academic literature discovery"""
    pass

@cli.command()
@click.option('--netid', prompt='UCSB NetID', help='Your UCSB NetID')
@click.option('--password', prompt='Password', hide_input=True, help='Your UCSB password')
def login(netid, password):
    """Authenticate with UCSB library"""
    console.print("[bold blue]Authenticating with UCSB Library...[/bold blue]")
    
    auth = UCSBLibraryAuth()
    
    with console.status("[bold green]Logging in..."):
        success = auth.authenticate(netid, password)
    
    if success:
        console.print("[bold green]✓ Authentication successful![/bold green]")
        console.print("Session saved. You can now use search commands.")
    else:
        console.print("[bold red]✗ Authentication failed[/bold red]")
        sys.exit(1)

@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--sources', '-s', multiple=True, 
              type=click.Choice(['wos', 'scholar', 'pubmed']),
              default=['wos', 'scholar', 'pubmed'],
              help='Sources to search')
@click.option('--max-results', '-n', default=50, help='Max results')
@click.option('--year-start', type=int, help='Start year')
@click.option('--year-end', type=int, help='End year')
@click.option('--output', '-o', default='search_results.json', help='Output file')
def search(query, sources, max_results, year_start, year_end, output):
    """Search literature across multiple sources"""
    
    # Load session
    auth = UCSBLibraryAuth()
    if not auth.load_session():
        console.print("[yellow]No valid session. Please run 'login' first.[/yellow]")
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = SearchOrchestrator(auth.get_session())
    
    # Build filters
    from src.search.orchestrator import SearchFilters
    filters = SearchFilters(
        year_start=year_start,
        year_end=year_end
    )
    
    console.print(f"[bold]Searching: {query}[/bold]")
    console.print(f"Sources: {', '.join(sources)}")
    
    # Execute search
    with console.status("[bold green]Searching..."):
        results = orchestrator.comprehensive_search(
            query=query,
            sources=list(sources),
            filters=filters if year_start or year_end else None,
            max_results_per_source=max_results
        )
    
    # Display results
    console.print(f"\n[bold green]Found {results['total_unique']} unique papers[/bold green]")
    
    table = Table(title="Top Results")
    table.add_column("Title", style="cyan", width=50)
    table.add_column("Year", style="green")
    table.add_column("Citations", style="yellow")
    table.add_column("Score", style="magenta")
    
    for paper in results['papers'][:20]:
        table.add_row(
            paper['title'][:47] + "..." if len(paper['title']) > 50 else paper['title'],
            str(paper.get('year', 'N/A')),
            str(paper.get('citations', 0)),
            f"{paper.get('relevance_score', 0):.1f}"
        )
    
    console.print(table)
    
    # Save results
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n[green]Results saved to {output}[/green]")

@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--max-downloads', '-n', default=50, help='Max papers to download')
def download(results_file, max_downloads):
    """Download papers from search results"""
    
    # Load session
    auth = UCSBLibraryAuth()
    if not auth.load_session():
        console.print("[yellow]No valid session. Please run 'login' first.[/yellow]")
        sys.exit(1)
    
    # Load results
    with open(results_file) as f:
        results = json.load(f)
    
    papers = results['papers'][:max_downloads]
    
    console.print(f"[bold]Downloading {len(papers)} papers via UCSB library[/bold]")
    
    # Create retriever
    retriever = PDFRetriever(auth.get_session())
    
    # Download
    download_results = retriever.batch_download(papers)
    
    # Summary
    console.print(f"\n[bold green]Download Complete[/bold green]")
    console.print(f"Successful: {len(download_results['successful'])}")
    console.print(f"Failed: {len(download_results['failed'])}")
    
    if download_results['failed']:
        console.print("\n[yellow]Failed downloads:[/yellow]")
        for item in download_results['failed'][:5]:
            console.print(f"  - {item['paper']['title'][:60]}...")

@cli.command()
@click.option('--question', '-q', required=True, help='Research question')
@click.option('--max-papers', '-n', default=30, help='Target number of papers')
@click.option('--min-quality', default=0.7, help='Min quality score (0-1)')
@click.option('--output', '-o', default='review_output.json', help='Output file')
def auto_review(question, max_papers, min_quality, output):
    """Conduct autonomous literature review"""
    
    # Load session
    auth = UCSBLibraryAuth()
    if not auth.load_session():
        console.print("[yellow]No valid session. Please run 'login' first.[/yellow]")
        sys.exit(1)
    
    # Create components
    orchestrator = SearchOrchestrator(auth.get_session())
    retriever = PDFRetriever(auth.get_session())
    agent = LiteratureAgent(orchestrator, retriever)
    
    # Run autonomous review
    results = agent.comprehensive_review(
        research_question=question,
        max_papers=max_papers,
        min_quality_score=min_quality
    )
    
    # Save results
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save synthesis
    synthesis_file = output.replace('.json', '_synthesis.md')
    with open(synthesis_file, 'w') as f:
        f.write(f"# Literature Review: {question}\n\n")
        f.write(results['synthesis'])
    
    console.print(f"\n[bold green]Review complete![/bold green]")
    console.print(f"Results saved to: {output}")
    console.print(f"Synthesis saved to: {synthesis_file}")

@cli.command()
@click.argument('tool_name')
@click.argument('args_json')
def execute_tool(tool_name, args_json):
    """Execute tool from MCP server (internal use)"""
    args = json.loads(args_json)
    
    # Load auth
    auth = UCSBLibraryAuth()
    auth.load_session()
    
    if tool_name == 'search_literature':
        from src.search.orchestrator import SearchOrchestrator, SearchFilters
        
        orchestrator = SearchOrchestrator(auth.get_session())
        filters = SearchFilters(
            year_start=args.get('year_start'),
            year_end=args.get('year_end')
        )
        
        results = orchestrator.comprehensive_search(
            query=args['query'],
            sources=args.get('sources', ['wos', 'scholar', 'pubmed']),
            filters=filters,
            max_results_per_source=args.get('max_results', 50)
        )
        
        print(json.dumps(results, indent=2))
    
    elif tool_name == 'download_papers':
        # Implementation here
        pass
    
    elif tool_name == 'autonomous_review':
        orchestrator = SearchOrchestrator(auth.get_session())
        retriever = PDFRetriever(auth.get_session())
        agent = LiteratureAgent(orchestrator, retriever)
        
        results = agent.comprehensive_review(
            research_question=args['research_question'],
            max_papers=args.get('max_papers', 30),
            min_quality_score=args.get('min_quality_score', 0.7)
        )
        
        print(json.dumps(results, indent=2))

if __name__ == '__main__':
    cli()
```

### Configuration Files

**File: `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ucsb-literature-agent"
version = "1.0.0"
description = "Autonomous literature search tool with UCSB library access"
requires-python = ">=3.10"
dependencies = [
    "anthropic>=0.40.0",
    "requests>=2.31.0",
    "selenium>=4.15.0",
    "click>=8.1.0",
    "rich>=13.7.0",
    "python-dotenv>=1.0.0",
    "PyPDF2>=3.0.0",
    "pdfplumber>=0.11.0",
    "scholarly>=1.7.0",
]

[project.scripts]
ucsb-lit = "src.cli.main:cli"
```

**File: `.env.example`**

```bash
# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_key_here

# Web of Science API (get from Clarivate)
WOS_API_KEY=your_wos_key_here

# SerpAPI (optional, for reliable Google Scholar access)
SERPAPI_KEY=your_serpapi_key_here

# UCSB Credentials (or provide at runtime)
UCSB_NETID=your_netid
UCSB_PASSWORD=your_password
```

**File: `.gitignore`**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.venv

# Environment
.env
.env.local

# Cache
cache/
*.pkl
*.db

# Papers
papers/
output/

# Node
mcp-server/node_modules/
mcp-server/build/
mcp-server/package-lock.json

# IDE
.vscode/
.idea/
*.swp
```

## Setup Instructions

### 1. Initial Setup

```bash
# Clone/create project directory
mkdir ucsb-literature-agent
cd ucsb-literature-agent

# Copy all files from this spec into the directory structure

# Install Python dependencies
pip install -e .

# Install Node dependencies for MCP server
cd mcp-server
npm install
npm run build
cd ..

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configure Claude Code

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ucsb-literature": {
      "command": "node",
      "args": ["/absolute/path/to/ucsb-literature-agent/mcp-server/build/index.js"]
    }
  }
}
```

### 3. Initial Authentication

```bash
# Authenticate with UCSB
ucsb-lit login
```

### 4. Test the System

```bash
# Test search
ucsb-lit search --query "coral bleaching mechanisms" --max-results 20

# Test autonomous review
ucsb-lit auto-review --question "What are the molecular responses of corals to thermal stress?"
```

## Usage with Claude Code

Once configured, you can use natural language with Claude Code:

```
"Use the UCSB literature search tool to find the top 30 papers on 
Acropora pulchra wound healing and thermal stress, download all 
available PDFs, and synthesize the findings focusing on gene 
expression patterns."
```

Claude Code will autonomously:
1. Search across multiple databases
2. Assess coverage and refine if needed
3. Select the most relevant papers
4. Download PDFs via UCSB library access
5. Synthesize findings

## Next Steps for Implementation

1. **Start with authentication**: Get UCSB login working first
2. **Build search layer**: Implement one source at a time (PubMed is easiest to start)
3. **Add PDF retrieval**: Test with known DOIs
4. **Integrate Claude**: Add synthesis capabilities
5. **Build MCP server**: Connect to Claude Code
6. **Test end-to-end**: Run full autonomous reviews

## Notes

- Some API keys (WoS, SerpAPI) require subscriptions
- PubMed is free and doesn't require authentication
- UCSB library access requires valid institutional credentials
- Rate limiting is important to avoid blocks
- Session management ensures you don't need to re-authenticate frequently

This specification should give Claude Code everything needed to build the system. Let me know if you need any clarification on specific components!
