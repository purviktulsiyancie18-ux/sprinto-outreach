import logging
import time
from pathlib import Path
import requests
import config

log = logging.getLogger(__name__)
PAGES = Path(__file__).parent / "fixtures" / "pages"
RETRY_STATUS = {429, 500, 502, 503, 504}  # transient: worth another attempt


def fetch(domain, path="home"):
    """Return cleaned page text for a domain (home or about page).

    Live mode retries transient failures (timeouts, connection errors, 429/5xx)
    up to config.SCRAPE_ATTEMPTS times with exponential backoff. Permanent
    failures (404 etc.) are not retried. Returns "" if the page cannot be fetched.
    """
    if config.OFFLINE:
        try:
            return (PAGES / f"{domain}_{path}.txt").read_text()
        except FileNotFoundError:
            log.warning("no cached page for %s/%s", domain, path)
            return ""

    url = f"https://{domain}/" + ("" if path == "home" else path)
    for attempt in range(1, config.SCRAPE_ATTEMPTS + 1):
        try:
            resp = requests.get(url, timeout=10)
        except requests.RequestException as e:
            reason = f"{type(e).__name__}"
        else:
            if resp.status_code == 200:
                return clean(resp.text)
            if resp.status_code not in RETRY_STATUS:
                log.warning("%s returned %s, not retrying", url, resp.status_code)
                return ""
            reason = f"HTTP {resp.status_code}"
        if attempt < config.SCRAPE_ATTEMPTS:
            wait = config.SCRAPE_BACKOFF * 2 ** (attempt - 1)
            log.warning("%s failed (%s), retry %d/%d in %.1fs",
                        url, reason, attempt, config.SCRAPE_ATTEMPTS - 1, wait)
            time.sleep(wait)
        else:
            log.error("%s failed after %d attempts (%s)", url, attempt, reason)
    return ""


def clean(html):
    lines = [l.strip() for l in html.splitlines() if len(l.split()) >= 8]
    seen, out = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return "\n".join(out)[:8000]
