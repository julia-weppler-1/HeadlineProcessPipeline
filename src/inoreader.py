import os
import time
import logging
import urllib.parse
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from playwright.sync_api import sync_playwright
from newspaper import Article
import requests
import camelot
import fitz
import pandas as pd
import trafilatura
from src.read_json import parse_inoreader_feed

import io
import re
import tempfile
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CLIENT_ID = os.getenv("INOREADER_CLIENT_ID")
APP_KEY = os.getenv("INOREADER_KEY")
ALLOW_PDF = True
CAMELOT_PRIMARY_FLAVOR = "lattice"
CAMELOT_FALLBACK_FLAVOR = "stream"
CAMELOT_MIN_ROWS = 2
CAMELOT_MIN_COLS = 2

def _clean_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def _looks_like_pdf_path(url: str) -> bool:
    try:
        return urlparse(url).path.lower().endswith(".pdf")
    except Exception:
        return False

def _response_is_pdf(resp) -> bool:
    ctype = (resp.headers.get("content-type") or "").split(";")[0].strip().lower()
    if ctype == "application/pdf":
        return True
    dispo = (resp.headers.get("content-disposition") or "").lower()
    return ".pdf" in dispo

def _wayback_resolve_latest(url: str, sess: requests.Session, timeout: int = 15) -> str:
    try:
        pr = urlparse(url)
        if pr.netloc != "web.archive.org":
            return url
        parts = pr.path.split("/", 3)
        # already timestamped (/web/YYYY.../https://...)
        if len(parts) >= 3 and parts[2] and parts[2][0].isdigit():
            return url
        # timestampless wrapper (/web/https://original)
        if len(parts) >= 3 and (parts[2].startswith("http://") or parts[2].startswith("https://")):
            original = parts[2]
        else:
            return url
        api = f"https://web.archive.org/wayback/available?url={quote(original, safe='')}"
        r = sess.get(api, timeout=timeout)
        closest = r.json().get("archived_snapshots", {}).get("closest", {})
        return closest.get("url") or url
    except Exception:
        return url

def _wayback_follow_iframe(html: str, sess: requests.Session, timeout: int = 15) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")
        iframe = soup.find("iframe", src=lambda s: s and "/web/" in s)
        if not iframe:
            return html
        src = iframe.get("src", "")
        frame_url = urljoin("https://web.archive.org", src)
        r = sess.get(frame_url, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
        return r.text or html
    except Exception:
        return html

# -------------------- HTML table extraction --------------------
def _nearest_caption_text(node: BeautifulSoup):
    cap = node.find("caption")
    if cap:
        t = cap.get_text(" ", strip=True)
        if t:
            return t
    fig = node.find_parent("figure")
    if fig:
        fc = fig.find("figcaption")
        if fc:
            t = fc.get_text(" ", strip=True)
            if t:
                return t
    pattern = re.compile(r"^\s*(Table|TABLE)\s*\d+[:.\s-]", re.IGNORECASE)
    prev = node.find_previous_sibling()
    hops = 0
    while prev and hops < 3:
        if prev.name in {"p", "h1", "h2", "h3", "h4", "h5"}:
            txt = _clean_ws(prev.get_text(" ", strip=True))
            if pattern.match(txt):
                return txt
        prev = prev.find_previous_sibling()
        hops += 1
    return ""

def _table_to_tsv_bs(tbl: BeautifulSoup):
    html_str = str(tbl)
    if pd is not None:
        try:
            dfs = pd.read_html(html_str)
            if dfs:
                df = max(dfs, key=lambda d: (d.shape[0] * d.shape[1]))
                df.columns = [str(c) for c in df.columns]
                return df.to_csv(index=False, sep="\t")
        except Exception:
            pass
    rows_out = []
    for tr in tbl.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        row = [c.get_text(" ", strip=True) for c in cells]
        if any(row):
            rows_out.append(row)
    if not rows_out or len(rows_out) < 2 or max(len(r) for r in rows_out) < 2:
        return None
    return "\n".join("\t".join(c or "" for c in r) for r in rows_out)

def _aria_table_to_tsv(node: BeautifulSoup):
    rows_out = []
    for r in node.find_all(attrs={"role": "row"}, recursive=True):
        cells = r.find_all(attrs={"role": ["cell", "columnheader", "rowheader"]}, recursive=False) \
                or r.find_all(attrs={"role": ["cell", "columnheader", "rowheader"]}, recursive=True)
        row = [c.get_text(" ", strip=True) for c in cells]
        if any(row):
            rows_out.append(row)
    if not rows_out or len(rows_out) < 2 or max(len(r) for r in rows_out) < 2:
        return None
    return "\n".join("\t".join(c or "" for c in r) for r in rows_out)

def _extract_tables_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "form", "iframe"]):
        tag.decompose()

    out = []
    for tbl in soup.find_all("table"):
        tsv = _table_to_tsv_bs(tbl)
        if tsv:
            out.append({"caption": _nearest_caption_text(tbl), "tsv": tsv})
    for node in soup.find_all(attrs={"role": "table"}):
        tsv = _aria_table_to_tsv(node)
        if tsv:
            out.append({"caption": _nearest_caption_text(node), "tsv": tsv})

    # de-dupe and filter tiny
    seen, deduped = set(), []
    for rec in out:
        key = (rec["caption"], rec["tsv"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rec)

    def _real(tsv: str) -> bool:
        rows = [r for r in tsv.splitlines() if r.strip()]
        return len(rows) >= 2 and max(len(r.split("\t")) for r in rows) >= 2

    deduped = [r for r in deduped if _real(r["tsv"])]
    if not deduped:
        return ""

    parts = []
    for i, rec in enumerate(deduped, 1):
        cap = f"[Caption] {rec['caption']}\n" if rec["caption"] else ""
        parts.append(f"Table {i}:\n{cap}{rec['tsv']}".strip())
    return "\n\n".join(parts)

# -------------------- PDF helpers (Camelot + text) --------------------
def _extract_text_from_pdf_bytes(pdf_bytes: bytes, tmp_path: str) -> str:
    if fitz is not None:
        try:
            with fitz.open(tmp_path) as pdf:
                parts = []
                for page in pdf:
                    t = page.get_text() or ""
                    if t:
                        parts.append(t)
                if parts:
                    return _clean_ws("\n\n".join(parts))
        except Exception:
            pass
    try:
        from pdfminer.high_level import extract_text as pdf_extract_text
        with io.BytesIO(pdf_bytes) as f:
            txt = pdf_extract_text(f) or ""
        if txt:
            return _clean_ws(txt)
    except Exception:
        pass
    try:
        import PyPDF2
        with io.BytesIO(pdf_bytes) as f:
            reader = PyPDF2.PdfReader(f)
            pages = [page.extract_text() or "" for page in reader.pages]
        return _clean_ws("\n\n".join(pages))
    except Exception:
        return ""

def _camelot_tables_to_tsv_list(pdf_path: str):
    if camelot is None:
        return []
    def _run(flavor: str):
        try:
            tb = camelot.read_pdf(pdf_path, pages="all", flavor=flavor)
        except Exception:
            return []
        out = []
        for t in tb:
            try:
                df = t.df
                if df.shape[0] >= CAMELOT_MIN_ROWS and df.shape[1] >= CAMELOT_MIN_COLS:
                    out.append(df.to_csv(index=False, header=False).strip())
            except Exception:
                continue
        return out
    tables = _run(CAMELOT_PRIMARY_FLAVOR)
    if not tables:
        tables = _run(CAMELOT_FALLBACK_FLAVOR)
    return tables

def _pdf_bytes_to_text_plus_tables(pdf_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        text = _extract_text_from_pdf_bytes(pdf_bytes, tmp_path)
        tables_list = _camelot_tables_to_tsv_list(tmp_path)
        combined = text or ""
        if tables_list:
            combined = (combined + "\n\nTABLES:\n" + "\n\n".join(tables_list)).strip()
        return combined
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

def fetch_inoreader_articles(folder_name, access_token):
    """
    Fetch all articles from a given folder (label) that were published in the past week.
    This function uses pagination (via the continuation token) and query parameters:
      - n: max number of items per request (100)
      - r: order ("o" for oldest first so that we can use the ot parameter)
      - ot: start time (Unix timestamp) from which to return items
    """
    if not access_token:
        logger.error("No valid access token provided.")
        return []
    
    # Compute the Unix timestamp for one week ago.
    one_week_ago = int(time.time()) - 7 * 24 * 60 * 60
    
    articles = []
    n = 100
    continuation = None
    # Build the stream URL.
    stream_id = urllib.parse.quote(f"user/-/label/{folder_name}", safe='')
    base_url = f"https://www.inoreader.com/reader/api/0/stream/contents/{stream_id}"
    headers = {
        "Authorization": f"GoogleLogin auth={access_token}",
        "AppId": CLIENT_ID,  # Add the AppId header
        "appKey": APP_KEY
    }
    # Loop until no continuation token is returned.
    while True:
        # Set parameters: using r="o" (oldest first) and ot with the start time.
        params = {
                "n": n,
                "r": "n",  # newest first: 'ot' now acts as the end time (cutoff).
                "ot": one_week_ago,
                "output": "json"
            }
        if continuation:
            params["c"] = continuation
        
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            json_data = response.json()
            items = json_data.get("items", [])
            if not items:
                logger.info("No more items returned; stopping pagination.")
                # break
            articles.extend(items)
            
            continuation = json_data.get("continuation")
            if not continuation:
                logger.info("No continuation token found; reached end of stream.")
                break
        else:
            logger.error("Failed to fetch articles: %s", response.text)
            break
            
    logger.info("Total items fetched: %d", len(articles))
    return articles


def build_df_for_folder(folder_name, access_token):
    response = fetch_inoreader_articles(folder_name, access_token)
    df = parse_inoreader_feed(response)
    return df

# -------------------- Playwright URL resolver --------------------
def resolve_with_playwright(url):
    logging.info("Resolving URL via Playwright: %s", url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        def block_resource(route, request):
            if request.resource_type in ["image", "stylesheet", "font"]:
                return route.abort()
            return route.continue_()
        page.route("**/*", block_resource)
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1000)
        except Exception as e:
            logging.error("Error during page.goto: %s", e)
        final_url = page.url
        browser.close()
        return final_url

# -------------------- Main fetcher (HTML + PDF + tables) --------------------
def fetch_full_article_text(row):
    """
    Returns main text plus a TABLES: block (TSV) when any tables are found.
    Handles HTML pages + PDFs (Camelot).
    """
    real_url = row.get("url", "")
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching article text for URL: {real_url}")

    sess = requests.Session()
    headers = {
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.7",
    }

    # If Wayback wrapper without timestamp, resolve to a concrete snapshot
    if "web.archive.org" in real_url:
        real_url = _wayback_resolve_latest(real_url, sess, timeout=10)

    # Fast path: explicit .pdf
    if ALLOW_PDF and _looks_like_pdf_path(real_url):
        try:
            r = sess.get(real_url, headers=headers, timeout=20, allow_redirects=True)
            r.raise_for_status()
            return _pdf_bytes_to_text_plus_tables(r.content)
        except Exception as e:
            logger.error(f"PDF fetch failed for {real_url}: {e}")
            return ""

    # 1) Try a plain HTTP GET
    try:
        resp = sess.get(real_url, headers=headers, timeout=20, allow_redirects=True)
    except Exception as e:
        logger.error(f"Error fetching {real_url}: {e}")
        return ""

    # 2) If blocked, retry via Archive.org
    if resp.status_code == 403:
        archive_url = f"http://web.archive.org/web/{real_url}"
        logger.info(f"403 detected—retrying via Archive.org: {archive_url}")
        try:
            resp = sess.get(archive_url, headers=headers, timeout=20, allow_redirects=True)
        except Exception as e:
            logger.error(f"Error fetching archive URL {archive_url}: {e}")
            return ""

    # 3) Ensure OK
    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Final fetch failed ({resp.status_code}): {e}")
        return ""

    # If server actually served a PDF, route to PDF pipeline
    if ALLOW_PDF and _response_is_pdf(resp):
        try:
            return _pdf_bytes_to_text_plus_tables(resp.content)
        except Exception as e:
            logger.error(f"PDF parse failed for {resp.url}: {e}")
            return ""

    # 4) HTML path
    html = resp.text or ""
    # Wayback pages sometimes iframe the real content
    if "web.archive.org" in (resp.url or real_url):
        html = _wayback_follow_iframe(html, sess, timeout=10)

    # Main text (trafilatura → newspaper3k → soup.get_text)
    main_txt = ""
    if trafilatura:
        try:
            extracted = trafilatura.extract(html, url=resp.url, include_tables=False,
                                            no_fallback=False, favor_recall=True)
            if extracted:
                main_txt = extracted.strip()
        except Exception:
            pass
    if not main_txt:
        try:
            art = Article(resp.url)
            art.set_html(html)
            art.parse()
            main_txt = (art.text or "").strip()
        except Exception:
            main_txt = ""
    if not main_txt:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "form", "iframe"]):
            tag.decompose()
        article = soup.find("article")
        main_txt = _clean_ws(article.get_text(" ", strip=True) if article else soup.get_text(" ", strip=True))

    # Tables from HTML
    tables_block = _extract_tables_from_html(html)
    if tables_block:
        return (main_txt + "\n\nTABLES:\n" + tables_block).strip()
    return main_txt
    real_url = row.get("url", "")
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching article text for URL: {real_url}")

    # 1) Try a plain HTTP GET to check status
    try:
        resp = requests.get(real_url, timeout=15)
    except Exception as e:
        logger.error(f"Error fetching {real_url}: {e}")
        return ""

    # 2) If we got blocked, retry via Archive.org
    if resp.status_code == 403:
        archive_url = f"http://web.archive.org/web/{real_url}"
        logger.info(f"403 detected—retrying via Archive.org: {archive_url}")
        try:
            resp = requests.get(archive_url, timeout=15)
        except Exception as e:
            logger.error(f"Error fetching archive URL {archive_url}: {e}")
            return ""

    # 3) Make sure we now have a 200
    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Final fetch failed ({resp.status_code}): {e}")
        return ""

    # 4) Parse whatever HTML we got back
    html = resp.text
    article = Article(real_url)        # keeps metadata tied to original URL
    article.set_html(html)
    article.parse()

    text = (article.text or "").strip()
    if not text:
        logger.warning("No text extracted after parsing HTML from %s", resp.url)
    return text
