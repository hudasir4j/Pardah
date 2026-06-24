from __future__ import annotations

import asyncio
import re
from typing import Optional
from urllib.parse import urlparse

from app.config import Settings, get_settings
from app.services.verification import detect_platform

_OG_TITLE = re.compile(
  r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
  re.IGNORECASE,
)
_OG_TITLE_REV = re.compile(
  r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
  re.IGNORECASE,
)
_TITLE_TAG = re.compile(r"<title[^>]*>([^<]+)</title>", re.IGNORECASE)
_PUBLISHED = re.compile(
  r'<meta[^>]+(?:property|name)=["\'](?:article:published_time|datePublished|pubdate|publishdate)["\'][^>]+content=["\']([^"\']+)["\']',
  re.IGNORECASE,
)
_MODIFIED = re.compile(
  r'<meta[^>]+(?:property|name)=["\'](?:article:modified_time|dateModified|last-modified)["\'][^>]+content=["\']([^"\']+)["\']',
  re.IGNORECASE,
)


class PageMetadata:
  def __init__(
    self,
    page_title: Optional[str] = None,
    date_published: Optional[str] = None,
    platform: Optional[str] = None,
    scraped: bool = False,
    context_snippet: Optional[str] = None,
  ) -> None:
    self.page_title = page_title
    self.date_published = date_published
    self.platform = platform
    self.scraped = scraped
    self.context_snippet = context_snippet


async def enrich_url(url: str, settings: Optional[Settings] = None) -> PageMetadata:
  settings = settings or get_settings()
  fallback_platform = detect_platform(url)
  host = urlparse(url).hostname or fallback_platform

  if not settings.scraper_enabled or not url.startswith("http"):
    return PageMetadata(
      page_title=None,
      platform=fallback_platform,
      scraped=False,
      context_snippet=f"Found on {host}",
    )

  try:
    return await asyncio.to_thread(_scrape_sync, url, settings.scraper_timeout_ms, fallback_platform)
  except Exception:
    return PageMetadata(
      page_title=None,
      platform=fallback_platform,
      scraped=False,
      context_snippet=f"Found on {host}",
    )


def _scrape_sync(url: str, timeout_ms: int, fallback_platform: str) -> PageMetadata:
  from playwright.sync_api import sync_playwright

  html = ""
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
      page = browser.new_page(
        user_agent=(
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
      )
      page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
      html = page.content()
    finally:
      browser.close()

  title = _extract_title(html)
  published = _extract_date(html)
  platform = detect_platform(url)
  snippet = title or f"Page on {fallback_platform}"

  return PageMetadata(
    page_title=title,
    date_published=published,
    platform=platform,
    scraped=True,
    context_snippet=snippet[:180] if snippet else None,
  )


def _extract_title(html: str) -> Optional[str]:
  for pattern in (_OG_TITLE, _OG_TITLE_REV, _TITLE_TAG):
    m = pattern.search(html)
    if m:
      return _clean(m.group(1))
  return None


def _extract_date(html: str) -> Optional[str]:
  for pattern in (_PUBLISHED, _MODIFIED):
    m = pattern.search(html)
    if m:
      return _clean(m.group(1))
  return None


def _clean(value: str) -> str:
  return re.sub(r"\s+", " ", value).strip()
