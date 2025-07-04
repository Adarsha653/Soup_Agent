from .tools import get_top_news_sites, scrape_news_site, summarize_articles
from typing import Dict, Any

def news_summary_agent(country: str) -> Dict[str, Any]:
    trace = []
    # Tool 1: Get top news sites
    sites = get_top_news_sites(country)
    trace.append({
        "tool": "get_top_news_sites",
        "input": country,
        "output": sites
    })
    all_headlines = []
    for site in sites:
        headlines = scrape_news_site(site)
        trace.append({
            "tool": "scrape_news_site",
            "input": site,
            "output": headlines
        })
        all_headlines.extend(headlines)
    # Tool 3: Summarize
    summary = summarize_articles(all_headlines, country)
    trace.append({
        "tool": "summarize_articles",
        "input": all_headlines,
        "output": summary
    })
    return {
        "summary": summary,
        "trace": trace,
        "sources": sites
    } 