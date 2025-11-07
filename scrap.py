import asyncio, json, os, re, time, csv
from pathlib import Path
from urllib.parse import urljoin, urlparse
import httpx
from slugify import slugify
from playwright.async_api import async_playwright

# ---- Config ----
TARGET_URL = "https://www.linkedin.com/ad-library/search?accountOwner=Simplilearn"
OUT_DIR    = Path("output_simplilearn_ads")
IMG_DIR    = OUT_DIR / "images"
CSV_PATH   = OUT_DIR / "ads.csv"
JSONL_PATH = OUT_DIR / "ads.jsonl"

# Heuristics to ignore logos/avatars
BAD_IMG_PATTERNS = re.compile(r"(logo|avatar|icon|emoji|sprite)", re.I)

# CSS selectors (robust fallbacks)
AD_CARD_SELECTORS = [
    "[data-test-ad-card]",        # preferred if present
    "article",                    # common card container
    "div:has(img):has-text('Sponsored')",  # heuristic: contains images + “Sponsored”
]

AD_TEXT_WITHIN = [
    "[data-test-ad-headline]",
    "[data-test-ad-description]",
    "[data-test-ad-primary-text]",
    "h1, h2, h3, h4, p, span, div"
]

AD_LINK_SELECTORS = [
    "a[data-test-ad-destination]",
    "a[rel*=noopener]",
    "a[target=_blank]",
    "a"
]

COOKIE_ACCEPT_SELECTORS = [
    "button:has-text('Accept')",
    "button:has-text('I Accept')",
    "button:has-text('Agree')",
    "button:has-text('Allow all')",
]

LOAD_MORE_SELECTORS = [
    "button:has-text('Load more')",
    "button:has-text('Show more')",
]

def text_clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s

async def click_if_present(page, selectors, timeout=1500):
    for sel in selectors:
        try:
            btn = page.locator(sel)
            if await btn.first.is_visible(timeout=timeout):
                await btn.first.click()
                return True
        except Exception:
            pass
    return False

async def auto_load_all(page, max_rounds=30, settle_wait=1200):
    """Scrolls to bottom repeatedly and clicks any 'Load more' buttons until content no longer grows."""
    last_height = 0
    stable_hits = 0
    for i in range(max_rounds):
        # try load more buttons if visible
        await click_if_present(page, LOAD_MORE_SELECTORS)
        # scroll to bottom a few times to trigger lazy-load
        for _ in range(6):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(300)
        # check growth
        height = await page.evaluate("() => document.body.scrollHeight")
        if height <= last_height:
            stable_hits += 1
        else:
            stable_hits = 0
        last_height = height
        await page.wait_for_timeout(settle_wait)
        if stable_hits >= 2:
            break

def resolve_images(img_elems):
    """Extract plausible creative image URLs from <img> nodes."""
    urls = set()
    for img in img_elems:
        for attr in ("src", "data-src", "srcset"):
            val = img.get(attr) or ""
            if "data:image" in val:
                continue
            if attr == "srcset" and val:
                # take highest-res candidate
                parts = [p.strip() for p in val.split(",") if p.strip()]
                if parts:
                    last_url = parts[-1].split(" ")[0]
                    val = last_url
            if val and not BAD_IMG_PATTERNS.search(val):
                urls.add(val)
    return list(urls)

async def extract_cards(page):
    # collect candidate ad cards using multiple selectors
    handles = []
    for sel in AD_CARD_SELECTORS:
        items = await page.query_selector_all(sel)
        handles.extend(items)
    # dedupe
    seen = set()
    uniq = []
    for h in handles:
        box = await h.bounding_box() or {}
        key = (box.get("x"), box.get("y"), box.get("width"), box.get("height"))
        if key not in seen:
            seen.add(key)
            uniq.append(h)
    results = []
    for idx, card in enumerate(uniq, 1):
        try:
            # text
            texts = []
            for sel in AD_TEXT_WITHIN:
                parts = await card.query_selector_all(sel)
                for p in parts:
                    t = text_clean(await p.inner_text())
                    if t and t not in texts:
                        texts.append(t)

            visible_text = text_clean(" ".join(texts))[:4000]

            # destination link
            dest = ""
            for lsel in AD_LINK_SELECTORS:
                a = await card.query_selector(lsel)
                if a:
                    href = (await a.get_attribute("href")) or ""
                    if href and not href.startswith("#"):
                        dest = href
                        break

            # images
            imgs = await card.query_selector_all("img")
            img_attrs = []
            for img in imgs:
                attrs = {}
                for k in ("src", "data-src", "srcset", "alt"):
                    attrs[k] = await img.get_attribute(k)
                img_attrs.append(attrs)

            img_urls = resolve_images(img_attrs)

            # basic ID
            ad_id = slugify((visible_text[:120] or "ad") + f"-{idx}")

            results.append({
                "ad_id": ad_id,
                "text": visible_text,
                "destination": dest,
                "image_urls": img_urls
            })
        except Exception:
            continue
    return results

async def download_images(items):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        for item in items:
            saved = []
            for i, url in enumerate(item["image_urls"], 1):
                try:
                    # some URLs are protocol-relative
                    if url.startswith("//"):
                        url = "https:" + url
                    fn_base = slugify(item["ad_id"]) + f"-{i}"
                    ext = os.path.splitext(urlparse(url).path)[1] or ".jpg"
                    out_path = IMG_DIR / f"{fn_base}{ext}"
                    r = await client.get(url)
                    if r.status_code == 200 and r.content:
                        out_path.write_bytes(r.content)
                        saved.append(str(out_path))
                except Exception:
                    continue
            item["image_files"] = saved

def write_outputs(items):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # CSV
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ad_id", "text", "destination", "image_files"])
        for it in items:
            w.writerow([it["ad_id"], it["text"], it["destination"], ";".join(it.get("image_files", []))])
    # JSONL
    with JSONL_PATH.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
        page = await ctx.new_page()
        await page.goto(TARGET_URL, wait_until="networkidle")

        # deal with cookie banner if present
        await click_if_present(page, COOKIE_ACCEPT_SELECTORS)

        # auto load all ads
        await auto_load_all(page)

        # extract
        items = await extract_cards(page)

        # download images
        await download_images(items)

        # outputs
        write_outputs(items)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
