import config
import llm
import scrape
import extract

PROMPT = """Sprinto sells compliance automation (SOC 2, ISO 27001, GDPR) to SaaS
companies at Series A-C that are preparing for an audit or pressed by enterprise
customers. Score this company's fit and say if more information is needed.
Return JSON: score (0-100), reason, needs_more (bool).

COMPANY: {company}"""


EXTRA_PAGES = ["about"]  # pages to try, one per round, beyond the home page


def qualify(domain, company):
    result = llm.ask("qualify", domain, PROMPT.format(company=company))
    rounds = 0
    while result.get("needs_more") and rounds < min(config.MAX_ROUNDS, len(EXTRA_PAGES)):
        more = scrape.fetch(domain, EXTRA_PAGES[rounds])  # a new page each round
        rounds += 1
        if not more:  # fetch failed or page empty: more rounds would learn nothing
            break
        found = extract.extract(domain, more)
        # keep what we already know; only fill in fields the new page actually states
        company = {**company, **{k: v for k, v in found.items() if v is not None}}
        result = llm.ask("qualify_more", domain, PROMPT.format(company=company))
    result["rounds"] = rounds
    result["incomplete"] = bool(result.get("needs_more"))  # still wanted more info when we stopped
    result["qualified"] = result["score"] >= config.QUALIFY_THRESHOLD
    return result
