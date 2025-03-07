import os

import pytest
import requests
import xml.etree.ElementTree as ET
from collections import deque

from dotenv import load_dotenv


load_dotenv()


@pytest.fixture
def get_sitemap_links() -> list[str]:
    """Загружает sitemap.xml и получает все ссылки, включая вложенные карты."""

    urls = []
    queue = deque([os.getenv("SITEMAP_INDEX_URL")])

    headers = {"User-Agent": os.getenv("SITEMAP_USER_AGENT")}

    while queue:
        current_sitemap = queue.popleft()

        try:
            response = requests.get(current_sitemap, headers=headers)
            response.raise_for_status()
            content = ET.fromstring(response.content)
            namespace = {"ns": os.getenv("SITEMAP_NS_URL")}

            for element in content.findall(".//ns:loc", namespace):
                link = element.text
                if "sitemap" in link:
                    queue.append(link)
                else:
                    urls.append(link)

        except requests.exceptions.RequestException:
            continue

    return urls
