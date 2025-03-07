import pytest

from ..helpers import check_links


@pytest.mark.asyncio
async def test_sitemap(get_sitemap_links):
    """Загружает все ссылки с карты сайта и проверяет на статус код 200 и на canonical"""
    get_sitemap_links.append("https://shazoo.ru/hubs")  # Для примера добавил ссылку отвечающую кодом 500
    bad_canonicals_count = await check_links(get_sitemap_links)
    assert bad_canonicals_count == 0, "Найдены несовпадения canonical url"
