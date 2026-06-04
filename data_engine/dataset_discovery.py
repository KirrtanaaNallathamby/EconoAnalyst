#data_engine/dataset_discovery.py

import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def discover_dataset_pages(search_url: str) -> dict:
    try:
        response = httpx.get(
            search_url,
            timeout=20,
            follow_redirects=True,
            verify=False
        )

        if response.status_code != 200:
            return {
                "success": False,
                "source": search_url,
                "datasets": [],
                "error": f"Status {response.status_code}"
            }

        soup = BeautifulSoup(response.text, "lxml")

        datasets = []

        for link in soup.find_all("a", href=True):

            href = link.get("href")
            text = link.get_text(" ", strip=True)

            full_url = urljoin(search_url, href)

            text_lower = text.lower()
            url_lower = full_url.lower()

            keywords = [
                "unemployment",
                "employment",
                "labour",
                "lfs",
                "dataset",
                "indicator"
            ]

            if any(word in text_lower for word in keywords) or \
               any(word in url_lower for word in keywords):

                datasets.append({
                    "title": text,
                    "url": full_url
                })

        return {
            "success": True,
            "source": search_url,
            "datasets": datasets[:30],
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "source": search_url,
            "datasets": [],
            "error": str(e)
        }