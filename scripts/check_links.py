#!/usr/bin/env python3
"""Проверяет, что открываются все http(s)-ссылки в Markdown-файле.

Пример:
    python3 check_links.py ~/courses/ux-research/_course/sources.md

Код выхода 1, если есть мёртвые ссылки. Ответы 401, 403, 405 и 429 — не мёртвые:
сайт не пустил робота или не принимает такой запрос, ссылку надо открыть вручную.
"""
import concurrent.futures
import re
import sys
import urllib.error
import urllib.request

URL = re.compile(r"https?://[^\s|<>`\"')\]]+")
MANUAL = {401, 403, 405, 429}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; course-builder-linkcheck/1.0)",
    "Accept": "text/html,application/pdf,*/*",
}


def check(url):
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return url, response.status, ""
    except urllib.error.HTTPError as e:
        return url, e.code, ""
    except Exception as e:
        return url, None, type(e).__name__


def main():
    if len(sys.argv) != 2:
        sys.exit("Использование: check_links.py <файл.md>")
    text = open(sys.argv[1], encoding="utf-8").read()
    urls = sorted({u.rstrip(".,;:") for u in URL.findall(text)})
    if not urls:
        print("Ссылок не найдено.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check, urls))

    dead, manual = [], []
    for url, status, error in results:
        if status is not None and status < 400:
            continue
        (manual if status in MANUAL else dead).append((url, status or error))

    print(f"Проверено ссылок: {len(urls)}. Мёртвых: {len(dead)}. Открыть вручную: {len(manual)}.")
    for title, rows in (("Мёртвые", dead), ("Открыть вручную", manual)):
        if rows:
            print(f"\n{title}:")
            for url, why in rows:
                print(f"  {why}  {url}")
    sys.exit(1 if dead else 0)


if __name__ == "__main__":
    main()
