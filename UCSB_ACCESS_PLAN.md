# UCSB Library Access Integration Plan

## Current Status

✅ **Working**: Open access papers (arXiv, PMC, Unpaywall)
❌ **Not Working**: Paywalled papers (most journal articles)

## Goal

Enable download of paywalled papers through UCSB library institutional access.

## UCSB Authentication System

### Technical Details
- **Proxy URL**: `https://proxy.library.ucsb.edu/login`
- **Authentication**: UCSB NetID + Password + DUO (2FA)
- **Type**: EZproxy hosted system
- **Session**: Cookie-based after authentication

### Challenge: DUO Two-Factor Authentication

⚠️ **Important**: UCSB requires DUO 2FA, which means:
- Cannot fully automate (requires user interaction)
- Need to handle DUO push/code/SMS prompt
- Session cookies expire periodically

## Proposed Solutions

### Option 1: Manual Cookie Export (Easiest, Most Secure) ⭐ RECOMMENDED

**How it works:**
1. User logs into UCSB library manually in browser
2. User exports cookies using browser extension
3. App uses exported cookies for requests
4. Cookies work until they expire (~session or hours)

**Pros:**
- ✅ Most secure (no credentials stored)
- ✅ Works with DUO 2FA
- ✅ No automation violations
- ✅ Quick to implement
- ✅ User controls when to refresh

**Cons:**
- ❌ Manual cookie refresh needed
- ❌ Requires browser extension

**Implementation:**
```python
# User exports cookies.txt from browser
# App loads cookies and uses them
session.cookies = load_cookies_from_file('ucsb_cookies.txt')
```

### Option 2: Interactive Browser Login (Best UX)

**How it works:**
1. App opens browser window
2. User logs in manually (including DUO)
3. App captures session cookies
4. App saves cookies for reuse

**Pros:**
- ✅ Better UX than manual export
- ✅ Works with DUO
- ✅ No credential storage
- ✅ Clear what's happening

**Cons:**
- ❌ Requires Selenium/Playwright
- ❌ More complex
- ❌ Browser dependency

**Implementation:**
```python
# Open browser, wait for login, capture cookies
from playwright import sync_playwright
# User completes login, we grab cookies
```

### Option 3: Credential Storage + Playwright (Most Automated)

**How it works:**
1. Store encrypted credentials
2. Use Playwright to automate login
3. Handle DUO programmatically where possible
4. Cache session cookies

**Pros:**
- ✅ Most automated
- ✅ Can reuse credentials

**Cons:**
- ❌ DUO automation problematic
- ❌ Security concerns with stored credentials
- ❌ May violate terms of service
- ❌ Brittle (breaks if UCSB changes login flow)

### Option 4: Hybrid Approach (Good Balance)

**How it works:**
1. First time: Interactive browser login (Option 2)
2. App saves session cookies
3. Reuse cookies until expired
4. When expired, prompt for new login

**Pros:**
- ✅ Secure (no credentials stored)
- ✅ Convenient (cookies last hours)
- ✅ Works with DUO
- ✅ User-friendly

**Cons:**
- ❌ Requires Playwright
- ❌ Occasional re-login needed

## Recommended Approach

### Phase 1: Manual Cookie Import ⭐

**Start with this** - it's secure, simple, and works immediately.

```bash
# User workflow:
1. Install "Get cookies.txt LOCALLY" extension
2. Log into library.ucsb.edu
3. Export cookies to file
4. Run: python -m src.cli.main auth import-cookies cookies.txt
5. Search and download work transparently
```

### Phase 2: Interactive Login

Add Playwright-based login flow for better UX:

```bash
# User workflow:
1. Run: python -m src.cli.main auth login
2. Browser opens to UCSB login
3. User logs in (including DUO)
4. App captures and saves cookies
5. Done!
```

## Security Considerations

### DO ✅
- Store cookies in `~/.config/litsearch/` (not in git)
- Use file permissions (chmod 600)
- Add `.gitignore` entries
- Encrypt cookies at rest (optional)
- Clear instructions in docs
- Support cookie expiration handling

### DON'T ❌
- **Never store NetID password in code**
- **Never commit credentials/cookies to git**
- **Never violate UCSB terms of service**
- **Never share session between users**

## Implementation Plan

### Phase 1: Cookie-Based Authentication

#### 1.1 Update Configuration
```python
# src/utils/config.py
UCSB_COOKIES_FILE = Path.home() / ".config" / "litsearch" / "ucsb_cookies.txt"
UCSB_SESSION_FILE = Path.home() / ".config" / "litsearch" / "ucsb_session.pkl"
```

#### 1.2 Cookie Management
```python
# src/auth/ucsb_auth.py
class UCSBAuth:
    def import_cookies(self, cookies_file: Path):
        """Import cookies from Netscape format"""

    def load_session(self) -> bool:
        """Load saved session cookies"""

    def get_session(self) -> requests.Session:
        """Get authenticated session"""

    def test_session(self) -> bool:
        """Test if session is still valid"""
```

#### 1.3 Update PDF Retriever
```python
# src/retrieval/pdf_retriever.py
def __init__(self, session: Optional[requests.Session] = None):
    self.session = session or requests.Session()

def _try_institutional_proxy(self, paper, filepath):
    """Try download through UCSB proxy"""
    if paper.doi:
        proxied_url = f"https://proxy.library.ucsb.edu/login?url=https://doi.org/{paper.doi}"
        return self._download_url(proxied_url, filepath)
```

#### 1.4 CLI Commands
```bash
# New commands
python -m src.cli.main auth import-cookies <file>
python -m src.cli.main auth status
python -m src.cli.main auth clear

# Enhanced search
python -m src.cli.main search "topic" --use-institutional-access
```

### Phase 2: Interactive Login (Future)

```python
# src/auth/interactive_login.py
from playwright.sync_api import sync_playwright

def interactive_login():
    """Open browser for user to log in"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://proxy.library.ucsb.edu/login')

        # Wait for user to complete login
        print("Please log in to UCSB library...")
        page.wait_for_url("**/login?auth=success**", timeout=300000)

        # Extract cookies
        cookies = page.context.cookies()
        browser.close()
        return cookies
```

## Testing Strategy

### Without Credentials (Open Access Only)
```bash
# Current functionality still works
python -m src.cli.main search "topic" --sources arxiv
```

### With UCSB Access (After Cookie Import)
```bash
# Should now download paywalled papers
python -m src.cli.main search "topic" --sources pubmed --download
```

### Validation
1. Test with known paywalled paper
2. Verify proxy URL in requests
3. Check cookie headers
4. Confirm PDF download success
5. Test cookie expiration handling

## User Documentation

### Quick Start

**Step 1: Get Your Cookies**
```
1. Install browser extension: "Get cookies.txt LOCALLY"
2. Go to library.ucsb.edu
3. Log in with your NetID and DUO
4. Click the extension icon
5. Download cookies.txt
```

**Step 2: Import to App**
```bash
python -m src.cli.main auth import-cookies ~/Downloads/cookies.txt
```

**Step 3: Search with Institutional Access**
```bash
python -m src.cli.main search "your topic" --download
```

### Troubleshooting

**Cookies Expired**
```bash
# Check status
python -m src.cli.main auth status

# Re-import fresh cookies
python -m src.cli.main auth import-cookies new_cookies.txt
```

**Downloads Still Failing**
```bash
# Clear cache and try again
python -m src.cli.main auth clear
python -m src.cli.main auth import-cookies cookies.txt
```

## Proxy URL Patterns

UCSB proxy wraps URLs in this format:
```
https://proxy.library.ucsb.edu/login?url={original_url}
```

For DOIs:
```
Original: https://doi.org/10.1038/nature12373
Proxied:  https://proxy.library.ucsb.edu/login?url=https://doi.org/10.1038/nature12373
```

## Success Metrics

### Before UCSB Access
- Open access only: ~10-30% success rate
- arXiv: 100% success
- PMC: ~80% success
- Other journals: ~5% success

### After UCSB Access
- Should reach: ~70-80% success rate
- arXiv: 100% (unchanged)
- PMC: 100% (unchanged)
- Paywalled journals: 70-80% (HUGE improvement)

## Limitations

### Will Still Fail For:
1. **Papers not in UCSB subscriptions**
2. **Embargoed recent papers**
3. **Books** (different access system)
4. **Some publisher technical issues**

### Cookie Lifetime
- Sessions expire after inactivity (~hours)
- DUO tokens expire periodically
- User needs to re-import occasionally

## Next Steps

1. ✅ Get user approval for approach
2. ⏳ Implement cookie import system
3. ⏳ Update PDF retriever to use proxy
4. ⏳ Add auth CLI commands
5. ⏳ Test with real UCSB credentials
6. ⏳ Document workflow
7. ⏳ (Optional) Add interactive login

## Privacy & Security Notes

### What Gets Stored
- Session cookies (temporary credentials)
- Cookie expiration timestamps
- Nothing else

### What Does NOT Get Stored
- ❌ Your NetID password
- ❌ Your DUO keys
- ❌ Any permanent credentials

### Where It's Stored
- `~/.config/litsearch/ucsb_cookies.txt` (local only)
- Never in git repository
- Never in cloud

### When to Clear
```bash
# Clear when:
# - Sharing computer
# - Changing accounts
# - Testing
python -m src.cli.main auth clear
```

## Compliance

This approach:
- ✅ Complies with UCSB policies (manual login)
- ✅ No credential storage
- ✅ User controls authentication
- ✅ Respects DUO 2FA requirement
- ✅ Session-based (like using browser)

## Questions for You

Before implementing, I need to know:

1. **Which approach do you prefer?**
   - Option 1: Manual cookie export (simple, secure)
   - Option 4: Interactive browser login (better UX)

2. **How often will you use this?**
   - Daily → invest in better UX
   - Occasionally → simple is fine

3. **Comfortable with browser extensions?**
   - Yes → Option 1 is quick
   - No → Need Option 4

4. **Want me to implement now?**
   - I can build Option 1 in ~30 minutes
   - Option 4 needs ~2 hours

Let me know your preferences and I'll implement the solution!