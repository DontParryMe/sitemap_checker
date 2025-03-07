import asyncio
import os
import ssl
import random

import aiohttp
from http import HTTPStatus
from bs4 import BeautifulSoup


async def fetch(
    session: aiohttp.ClientSession, url: str, ssl_context: ssl.SSLContext
) -> tuple[str, str | None, str | None]:
    """Делает GET-запрос и проверяет статус и canonical URL"""
    try:
        headers = {
            "User-Agent": random.choice(os.getenv('USER_AGENTS'))
        }
        async with session.get(url, ssl=ssl_context, headers=headers) as response:
            status_code = response.status
            text = await response.text()

            if status_code != HTTPStatus.OK:
                return url, f"Статус-код: {status_code}", None

            soup = BeautifulSoup(text, "html.parser")
            canonical = soup.find("link", rel="canonical")
            canonical_url = canonical.get("href") if canonical else None

            if canonical_url and canonical_url.rstrip("/") != url.rstrip("/"):
                return url, None, canonical_url

            if not canonical:
                return url, None, "canonical отсутствует"

    except aiohttp.ClientError as e:
        return url, f"Ошибка сети: {str(e)}", None

    except asyncio.TimeoutError:
        return url, "Ошибка: Тайм-аут запроса", None

    except Exception as e:
        return url, f"Неизвестная ошибка: {str(e)}", None

    return url, None, None


async def check_links(
    urls: list[str],
    bad_links_file: str = "bad_links.txt",
    canonical_mismatch_file: str = "canonical_mismatch.txt",
) -> int:
    """Проверяет список URL на статус-коды и canonical URL"""
    bad_canonicals_counter = 0
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context, limit_per_host=int(os.getenv("LIMIT_PER_HOST")))
    async with aiohttp.ClientSession(
            connector=connector, timeout=aiohttp.ClientTimeout(total=int(os.getenv('CLIENT_TIMEOUT')))
    ) as session:
        random.shuffle(urls)
        tasks = [fetch(session, url, ssl_context) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    with (
        open(bad_links_file, "w", encoding="utf-8") as bad_links_file,
        open(canonical_mismatch_file, "w", encoding="utf-8") as bad_canonicals_file,
    ):
        for url, bad_status, bad_canonical in results:
            if bad_status:
                bad_links_file.write(f"{url} - {bad_status}\n")
            if bad_canonical:
                bad_canonicals_counter += 1
                bad_canonicals_file.write(f"{url} - {bad_canonical}\n")

    return bad_canonicals_counter
