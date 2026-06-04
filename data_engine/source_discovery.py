#data_engine/source_discovery.py

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote

from data_engine.dataset_classifier import classify_link


def discover_sources(homepage_url: str, search_keywords: list, max_links: int = 20) -> dict:
    try:
        headers = {
            "User-Agent": "EcoResearchBot/1.0 Academic Project"
        }

        response = httpx.get(
            homepage_url,
            headers=headers,
            timeout=20,
            follow_redirects=True,
            verify=False
        )

        if response.status_code != 200:
            return {
                "success": False,
                "source": homepage_url,
                "error": f"Status code {response.status_code}",
                "candidates": []
            }

        soup = BeautifulSoup(response.text, "lxml")

        discovered = []

        if "data.gov.my" in homepage_url:
            discovered.extend(generate_data_gov_my_candidates(search_keywords))

        for link in soup.find_all("a", href=True):
            href = link.get("href")
            text = link.get_text(" ", strip=True)

            full_url = urljoin(homepage_url, href)

            if not is_valid_http_url(full_url):
                continue

            if not is_same_domain_or_known_data_source(homepage_url, full_url):
                continue

            combined = f"{full_url} {text}".lower()

            if is_relevant_link(combined, search_keywords):
                classified = classify_link(full_url, text)
                discovered.append(classified)

        discovered = deduplicate_candidates(discovered)

        discovered = sorted(
            discovered,
            key=lambda item: item["score"],
            reverse=True
        )

        return {
            "success": True,
            "source": homepage_url,
            "error": None,
            "candidates": discovered[:max_links]
        }

    except Exception as e:
        return {
            "success": False,
            "source": homepage_url,
            "error": str(e),
            "candidates": []
        }


def is_valid_http_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def is_same_domain_or_known_data_source(original_url: str, candidate_url: str) -> bool:
    original_domain = urlparse(original_url).netloc.replace("www.", "")
    candidate_domain = urlparse(candidate_url).netloc.replace("www.", "")

    if original_domain in candidate_domain:
        return True

    known_related_domains = [
        "storage.dosm.gov.my",
        "open.dosm.gov.my",
        "api.data.gov.my",
        "data.gov.my"
    ]

    return candidate_domain in known_related_domains


def is_relevant_link(combined_text: str, search_keywords: list) -> bool:
    discovery_words = [
        "data",
        "dataset",
        "api",
        "catalogue",
        "download",
        "csv",
        "json",
        "parquet",
        "table",
        "indicator"
    ]

    has_discovery_word = any(word in combined_text for word in discovery_words)
    has_task_keyword = any(keyword.lower() in combined_text for keyword in search_keywords)

    return has_discovery_word or has_task_keyword

def deduplicate_candidates(candidates: list) -> list:
    seen = set()
    unique = []

    for candidate in candidates:
        url = candidate.get("url")

        if url in seen:
            continue

        seen.add(url)
        unique.append(candidate)

    return unique

def generate_data_gov_my_candidates(search_keywords: list) -> list:
    candidates = []

    important_keywords = []

    for keyword in search_keywords:
        important_keywords.append(keyword)

    important_keywords.extend([
        "unemployment",
        "labour force",
        "employment",
        "lfs"
    ])

    for keyword in important_keywords:
        search_url = f"https://data.gov.my/data-catalogue?search={quote(keyword)}"

        candidates.append({
            "url": search_url,
            "domain": "data.gov.my",
            "is_structured_file": False,
            "is_api": False,
            "is_dataset_page": True,
            "score": 20
        })

    return candidates