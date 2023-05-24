# preco: .tablet\:text-lg
# titulo: .small\:line-clamp-2

import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from time import sleep


pesquisa = 'bolsa'.replace(' ', '+').lower()
url_pesquisa = f"https://www.decathlon.com.br/pesquisa?q={pesquisa}&sort=score_desc&page=0"

# Use sync version of Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url_pesquisa)
    page_content = page.content()
    soup = BeautifulSoup(page_content)
    print(soup.prettify())
    browser.close()