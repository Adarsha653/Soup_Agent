from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from .utils import openai_chat
import re

# Tool 1: Get top news sites for a country using LLM

def get_top_news_sites(country: str) -> List[str]:
    prompt = (
        f"List the top 5 newspaper websites in {country}. "
        "Only return the full URLs (including http or https), separated by commas. "
        "Do not include any text except the URLs."
    )
    response = openai_chat(prompt)
    # Extract URLs from the response (split by comma, strip whitespace)
    urls = re.findall(r'https?://[^,\s]+', response)
    if not urls:
        # fallback: split by comma
        urls = [u.strip() for u in response.split(',') if u.strip().startswith('http')]
    return urls[:5]

# Tool 2: Scrape headlines/content from a news site
def scrape_news_site(url: str) -> List[str]:
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Try to get headlines (h1, h2, h3, or <a> with 'headline' in class)
        headlines = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        # Fallback: get <a> tags with 'headline' in class
        for a in soup.find_all('a', class_=lambda c: bool(c and 'headline' in c)):
            headlines.append(a.get_text(strip=True))
        # Remove duplicates and empty
        headlines = list({h for h in headlines if h})
        return headlines[:10]  # Limit to top 10
    except Exception as e:
        return [f"[Error scraping {url}: {e}]"]

# Tool 3: Summarize articles using OpenAI
def summarize_articles(articles: List[str], country: str) -> str:
    if not articles:
        return "No articles found to summarize."
    prompt = (
        f"Summarize today's top news headlines from {country.title()} as a concise list in English, even if the headlines are in another language:\n"
        + "\n".join(f"- {a}" for a in articles)
    )
    return openai_chat(prompt) 