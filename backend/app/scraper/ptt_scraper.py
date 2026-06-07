import httpx
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
import re
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

HEADERS = settings.PTT_HEADERS
BASE_URL = settings.PTT_BASE_URL


def _parse_push_count(text: str) -> tuple[int, int]:
    """Return (push_count, boo_count) from the push indicator."""
    text = text.strip()
    if text == "爆":
        return 100, 0
    if text.startswith("X"):
        try:
            boos = int(text[1:]) * 10
        except ValueError:
            boos = 10
        return 0, boos
    try:
        val = int(text)
        return (val, 0) if val >= 0 else (0, abs(val))
    except ValueError:
        return 0, 0


def _parse_date(date_str: str) -> Optional[datetime]:
    date_str = date_str.strip()
    current_year = datetime.now().year
    formats = [
        f"{current_year}/{date_str}" if "/" not in date_str else date_str,
        date_str,
    ]
    for fmt_str in [f"{current_year}/{date_str}", date_str]:
        for fmt in ["%Y/%m/%d", "%Y-%m-%d", "%m/%d"]:
            try:
                if fmt == "%m/%d":
                    return datetime.strptime(f"{current_year}/{fmt_str.split('/')[-2]}/{fmt_str.split('/')[-1]}", "%Y/%m/%d")
                return datetime.strptime(fmt_str, fmt)
            except (ValueError, IndexError):
                continue
    return None


async def fetch_article_list(board: str, pages: int = 3) -> List[dict]:
    """Fetch article metadata from board index pages."""
    articles = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        index_url = f"{BASE_URL}/bbs/{board}/index.html"
        try:
            resp = await client.get(index_url)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch {board} index: {e}")
            return articles

        soup = BeautifulSoup(resp.text, "lxml")

        # Find current page number
        prev_link = soup.find("a", string=re.compile("上頁|‹"))
        current_page_num = None
        if prev_link and prev_link.get("href"):
            m = re.search(r"index(\d+)\.html", prev_link["href"])
            if m:
                current_page_num = int(m.group(1)) + 1

        page_urls = [index_url]
        if current_page_num:
            for i in range(1, pages):
                page_num = current_page_num - i
                if page_num > 0:
                    page_urls.append(f"{BASE_URL}/bbs/{board}/index{page_num}.html")

        for page_url in page_urls:
            try:
                if page_url != index_url:
                    resp = await client.get(page_url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "lxml")

                rows = soup.select("div.r-ent")
                for row in rows:
                    title_el = row.select_one("div.title a")
                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if not href:
                        continue

                    push_el = row.select_one("div.nrec span")
                    push_text = push_el.text if push_el else "0"
                    push_count, boo_count = _parse_push_count(push_text)

                    date_el = row.select_one("div.date")
                    date_str = date_el.text.strip() if date_el else ""
                    published_at = _parse_date(date_str)

                    author_el = row.select_one("div.author")
                    author = author_el.text.strip() if author_el else ""

                    articles.append({
                        "board": board,
                        "title": title_el.text.strip(),
                        "url": BASE_URL + href,
                        "author": author,
                        "push_count": push_count,
                        "boo_count": boo_count,
                        "published_at": published_at,
                        "content": "",
                    })

                await asyncio.sleep(0.3)
            except Exception as e:
                logger.warning(f"Failed to fetch page {page_url}: {e}")
                continue

    return articles


async def fetch_article_content(url: str) -> str:
    """Fetch full article content."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            main_content = soup.find("div", id="main-content")
            if not main_content:
                return ""

            # Remove meta info and push sections
            for tag in main_content.select("div.article-metaline, div.article-metaline-right, div.push"):
                tag.decompose()

            text = main_content.get_text(separator="\n").strip()
            # Remove trailing "--" separator and signature
            if "\n--\n" in text:
                text = text.split("\n--\n")[0]
            return text[:3000]  # cap content length
        except Exception as e:
            logger.warning(f"Failed to fetch article content {url}: {e}")
            return ""


async def scrape_board(board: str, pages: int = 3) -> List[dict]:
    """Full scrape: article list + content for top articles."""
    articles = await fetch_article_list(board, pages=pages)
    logger.info(f"Fetched {len(articles)} article stubs from {board}")

    # Fetch content for top articles (by push count), limit to avoid hammering
    top_articles = sorted(articles, key=lambda x: x["push_count"], reverse=True)[:30]
    other_articles = [a for a in articles if a not in top_articles]

    async def enrich(article: dict) -> dict:
        article["content"] = await fetch_article_content(article["url"])
        await asyncio.sleep(0.2)
        return article

    tasks = [enrich(a) for a in top_articles]
    enriched = await asyncio.gather(*tasks, return_exceptions=True)

    result = []
    for item in enriched:
        if isinstance(item, dict):
            result.append(item)
    result.extend(other_articles)
    return result
