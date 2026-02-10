from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from urllib.parse import urljoin, urlparse
from collections import deque
import httpx
from bs4 import BeautifulSoup
import re
import asyncio
import time
import urllib.robotparser as robotparser

app = FastAPI(title="Crawler API", version="0.1.0")

SKIP_EXT = re.compile(
    r".*\.(jpg|jpeg|png|gif|svg|ico|css|js|pdf|zip|rar|7z|mp3|mp4|mov|avi|webm)$",
    re.IGNORECASE,
)

class CrawlReq(BaseModel):
    start_url: HttpUrl
    max_pages: int = 30
    max_depth: int = 2
    same_domain: bool = True
    throttle_ms: int = 500
    user_agent: str = "LeverageCrawler/0.1 (+https://example.com)"

class Page(BaseModel):
    url: str
    title: str | None = None
    description: str | None = None
    content: str | None = None
    links: list[str] = []

class CrawlResp(BaseModel):
    ok: bool
    pages: list[Page]
    elapsed_ms: int

def is_same_domain(seed: str, url: str) -> bool:
    a = urlparse(seed)
    b = urlparse(url)
    return (a.hostname or "") == (b.hostname or "")

def clean_text(text: str) -> str:
    # collapse spaces/newlines
    return re.sub(r"\s+", " ", (text or "").strip())

def extract_text(html: str) -> tuple[str|None, str|None, str]:
    soup = BeautifulSoup(html, "lxml")

    # title / meta description
    title = soup.title.text.strip() if soup.title else None
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if (desc_tag and desc_tag.has_attr("content")) else None

    # main content: simple approach = join headings + paragraphs
    blocks = []
    for tag in soup.select("h1,h2,h3,p,li"):
        text = tag.get_text(" ", strip=True)
        if text:
            blocks.append(text)
    content = clean_text(" ".join(blocks))
    return title, description, content

def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        abs_url = urljoin(base_url, href)
        if SKIP_EXT.match(abs_url):
            continue
        out.append(abs_url.split("#")[0])  # drop anchors
    # dedupe but preserve order
    seen = set()
    res = []
    for u in out:
        if u not in seen:
            seen.add(u)
            res.append(u)
    return res

@app.post("/crawl", response_model=CrawlResp)
async def crawl(req: CrawlReq):
    t0 = time.time()

    # robots.txt
    rp = robotparser.RobotFileParser()
    parsed = urlparse(str(req.start_url))
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        # if robots not reachable, be conservative later (still crawl)
        pass

    headers = {"User-Agent": req.user_agent, "Accept": "text/html,*/*;q=0.8"}
    pages: list[Page] = []
    visited: set[str] = set()
    q = deque([(str(req.start_url), 0)])

    async with httpx.AsyncClient(timeout=20.0, headers=headers, follow_redirects=True) as client:
        while q and len(pages) < req.max_pages:
            url, depth = q.popleft()
            if url in visited:
                continue
            visited.add(url)

            # robots check
            try:
                allowed = rp.can_fetch(req.user_agent, url)
            except Exception:
                allowed = True
            if allowed is False:
                continue

            # throttle
            if req.throttle_ms > 0:
                await asyncio.sleep(req.throttle_ms / 1000.0)

            try:
                r = await client.get(url)
            except Exception as e:
                # skip fetch errors
                continue

            ctype = r.headers.get("content-type", "")
            if "text/html" not in ctype.lower():
                continue

            html = r.text
            title, description, content = extract_text(html)
            links = extract_links(url, html)

            # filter links
            next_links = []
            for link in links:
                if not link.startswith(("http://", "https://")):
                    continue
                if req.same_domain and not is_same_domain(str(req.start_url), link):
                    continue
                next_links.append(link)

            pages.append(Page(url=url, title=title, description=description, content=content, links=next_links))

            # queue next depth
            if depth < req.max_depth:
                for link in next_links:
                    if link not in visited:
                        q.append((link, depth + 1))

    return CrawlResp(ok=True, pages=pages, elapsed_ms=int((time.time() - t0) * 1000))
