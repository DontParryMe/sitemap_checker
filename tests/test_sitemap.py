import pytest

from ..helpers import check_links


@pytest.mark.asyncio
async def test_sitemap(get_sitemap_links):
    """Загружает все ссылки с карты сайта и проверяет на статус код 200 и на canonical"""
    # Для примера добавил ссылку отвечающую кодом 500
    get_sitemap_links.append("https://shazoo.ru/hubs")
    # Для примера добавил ссылки где отсутствует canonical
    get_sitemap_links += [
        "https://www.mozilla.org/2006/addons-blocklist",
        "https://www.mozilla.org/ja/products/vpn/pricing/",
        "https://www.mozilla.org/en-US/MPL/2.0/differences/",
        "https://www.mozilla.org/es-ES/products/vpn/pricing/",
    ]
    bad_canonicals_count = await check_links(get_sitemap_links)
    assert bad_canonicals_count == 0, "Найдены несовпадения canonical url"
