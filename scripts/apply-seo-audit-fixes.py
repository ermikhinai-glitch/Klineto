#!/usr/bin/env python3
"""Apply SEO audit fixes that do not need customer data. Run from repo root."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CONTRACTS = Path(
    "/cursor/stores/bc-e08c4f03-1659-48ba-97ac-640db5817c0c/docs/contracts.md"
)
BASE = "https://klineto.ru"

EXTRA_NOINDEX = {
    "/generalnaya-uborka",
    "/uborka-posle-remonta",
    "/ezhednevnaya-uborka",
    "/podderzhivayushchaya-uborka",
    "/regulyarnaya-uborka",
    "/uborka-ofisov/pered-vizitom",
    "/kalkulyator",
    "/tarify",
    "/kontakty",
    "/korporativnym",
    "/o-kompanii",
    "/zayavka-prinyata",
}

# Internal footer / catalog data-path → real core URL (not socials).
DATA_PATH_HREFS = {
    "politika-konfidentsialnosti": "/privacy",
    "politika-konfidencialnosti": "/privacy",
    "kvartiry": "/uborka-kvartir",
    "doma-i-kottedzhi": "/uborka-domov",
    "khimchistka": "/himchistka-mebeli",
    "ofisy": "/uborka-ofisov",
    "korporativnym-klientam": "/korporativnym",
    "kvartiry-generalnaya": "/uborka-kvartir/generalnaya",
    "kvartiry-podderzhivayushchaya": "/uborka-kvartir/podderzhivayushchaya",
    "kvartiry-posle-remonta": "/uborka-kvartir/posle-remonta",
    "kvartiry-okna": "/uborka-kvartir/mojka-okon",
    "uborka-kottedzhej": "/uborka-domov/kottedzhi",
    "uborka-zagorodnogo-doma": "/uborka-domov/zagorodnyj",
    "generalnaya-uborka-doma": "/uborka-domov/generalnaya",
    "uborka-doma-posle-remonta": "/uborka-domov/posle-remonta",
    "himchistka-v-dome": "/uborka-domov/himchistka-mebeli",
    "poslestroitelny-klining": "/uborka-kvartir/posle-remonta",
    "fasady-i-osteklenie": "/uborka-ofisov/mojka-okon",
}


def parse_contracts(text: str) -> dict[str, dict[str, str]]:
    pages: dict[str, dict[str, str]] = {}
    for block in re.split(r"\n## ", text)[1:]:
        path = block.split("\n", 1)[0].strip()
        if not path.startswith("/"):
            path = "/" + path
        meta: dict[str, str] = {}
        for line in block.split("\n"):
            m = re.match(r"- ([^:]+):\s*(.*)", line)
            if m:
                meta[m.group(1).strip()] = m.group(2).strip()
        pages[path] = meta
    return pages


def path_to_file(url_path: str) -> Path:
    if url_path == "/":
        return SITE / "index.html"
    return SITE / url_path.lstrip("/") / "index.html"


def upsert_head_meta(html: str, *, title: str | None, description: str | None,
                     canonical: str | None, robots: str | None) -> str:
    # Ensure </head> exists
    if "</head>" not in html:
        return html

    def set_or_replace(pattern: str, replacement: str, present_test: str) -> None:
        nonlocal html
        if re.search(present_test, html, flags=re.I):
            html = re.sub(pattern, replacement, html, count=1, flags=re.I | re.S)
        else:
            html = html.replace("</head>", replacement + "</head>", 1)

    if title is not None:
        if re.search(r"<title\b", html, flags=re.I):
            html = re.sub(
                r"<title\b[^>]*>.*?</title>",
                f"<title>{title}</title>",
                html,
                count=1,
                flags=re.I | re.S,
            )
        else:
            html = html.replace("</head>", f"<title>{title}</title></head>", 1)

    if description is not None:
        set_or_replace(
            r'<meta\s+name=["\']description["\'][^>]*>',
            f'<meta name="description" content="{description}"/>',
            r'<meta\s+name=["\']description["\']',
        )

    if canonical is not None:
        set_or_replace(
            r'<link\s+rel=["\']canonical["\'][^>]*>',
            f'<link rel="canonical" href="{canonical}"/>',
            r'<link\s+rel=["\']canonical["\']',
        )

    if robots is not None:
        set_or_replace(
            r'<meta\s+name=["\']robots["\'][^>]*>',
            f'<meta name="robots" content="{robots}"/>',
            r'<meta\s+name=["\']robots["\']',
        )

    return html


def demote_extra_h1(html: str, contract_h1: str) -> str:
    """Keep one H1 with contract text (prefer #seo-title); demote others to h2."""
    h1_iter = list(re.finditer(r"<h1\b([^>]*)>(.*?)</h1>", html, flags=re.I | re.S))
    if not h1_iter:
        # Inject SEO H1 before </main> if missing
        inject = (
            f'<section class="w-full bg-surface" id="seo-block" aria-labelledby="seo-title">'
            f'<div class="max-w-[1360px] mx-auto px-6 lg:px-12 py-space-lg">'
            f'<h1 id="seo-title" class="font-headline-lg text-headline-lg text-on-surface tracking-tight">'
            f"{contract_h1}</h1></div></section>"
        )
        if "</main>" in html:
            html = html.replace("</main>", inject + "</main>", 1)
        return html

    seo_idx = None
    for i, m in enumerate(h1_iter):
        attrs = m.group(1)
        if re.search(r'\bid=["\']seo-title["\']', attrs, flags=re.I):
            seo_idx = i
            break
    keep_idx = seo_idx if seo_idx is not None else len(h1_iter) - 1

    # Rebuild from the end so offsets stay valid
    parts = []
    last = len(html)
    for i in range(len(h1_iter) - 1, -1, -1):
        m = h1_iter[i]
        attrs = m.group(1)
        inner = m.group(2)
        if i == keep_idx:
            # Ensure id=seo-title and contract text
            if not re.search(r'\bid=["\']seo-title["\']', attrs, flags=re.I):
                attrs = attrs + ' id="seo-title"'
            new = f"<h1{attrs}>{contract_h1}</h1>"
        else:
            # Demote hero / secondary H1 → h2, preserve classes
            new = f"<h2{attrs}>{inner}</h2>"
        parts.append((m.start(), m.end(), new))

    for start, end, new in parts:
        html = html[:start] + new + html[end:]
    return html


def upsert_json_ld(html: str, schema_type: str, path: str, name: str) -> str:
    # Remove existing Organization/Service JSON-LD we may have added
    html = re.sub(
        r'<script\s+type=["\']application/ld\+json["\']>\s*\{[^<]*"@type"\s*:\s*"(Organization|Service)"[^<]*\}\s*</script>\s*',
        "",
        html,
        flags=re.I | re.S,
    )
    if schema_type == "Organization":
        data = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Klineto",
            "url": f"{BASE}/",
        }
    else:
        data = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": name,
            "url": f"{BASE}{path if path != '/' else '/'}",
            "provider": {
                "@type": "Organization",
                "name": "Klineto",
                "url": f"{BASE}/",
            },
            "areaServed": "Москва и Московская область",
        }
    block = (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    return html.replace("</head>", block + "</head>", 1)


def fix_footer_and_internal_hashes(html: str) -> str:
    # data-path based
    def repl_data(m: re.Match) -> str:
        full = m.group(0)
        path = m.group(1)
        target = DATA_PATH_HREFS.get(path)
        if not target:
            return full
        return re.sub(r'href="#"', f'href="{target}"', full, count=1)

    html = re.sub(
        r'<a\b[^>]*\bdata-path="([^"]+)"[^>]*>',
        repl_data,
        html,
        flags=re.I,
    )

    # Text-based privacy link without data-path
    html = re.sub(
        r'(<a\b[^>]*href="#"[^>]*>)\s*Политика конфиденциальности\s*(</a>)',
        r'<a class="hover:text-on-surface transition-colors" href="/privacy">Политика конфиденциальности</a>',
        html,
        flags=re.I,
    )

    # Remove fake street address in footers / contact strips (keep ООО untouched)
    html = re.sub(
        r'<span class="font-body-sm text-body-sm text-on-surface-variant">Москва, Пресненская наб\., 12</span>',
        '<span class="font-body-sm text-body-sm text-on-surface-variant">Москва и Московская область — оставьте заявку на сайте</span>',
        html,
    )
    return html


def strip_fake_emails(html: str) -> str:
    # mailto stubs → CTA without inventing addresses
    html = re.sub(
        r'<a\b([^>]*?)href="mailto:(?:corp|b2b|tender)@klineto\.ru"([^>]*)>(?:corp|b2b|tender)@klineto\.ru</a>',
        r'<a\1href="#booking-form"\2>Оставить заявку</a>',
        html,
        flags=re.I,
    )
    # bare text email stubs
    html = re.sub(
        r'(?<![/\w@.])(?:corp|b2b|tender)@klineto\.ru(?![/\w@.])',
        "оставьте заявку на сайте",
        html,
        flags=re.I,
    )
    return html


def fix_kontakty(html: str) -> str:
    # Replace B2B email card primary line
    html = re.sub(
        r'<a class="block font-headline-sm text-headline-sm text-on-surface hover:text-primary transition-colors my-space-xs" href="mailto:b2b@klineto\.ru">b2b@klineto\.ru</a>',
        '<a class="block font-headline-sm text-headline-sm text-on-surface hover:text-primary transition-colors my-space-xs" href="/#booking-form">Оставить заявку</a>',
        html,
        count=1,
    )
    # HQ address card
    html = re.sub(
        r'<div class="font-headline-sm text-headline-sm text-on-surface my-space-xs leading-snug">Пресненская наб\., 12</div>'
        r'<p class="font-body-sm text-body-sm text-on-surface-variant">Башня Федерация Восток, 31 этаж\. Прием и визиты: Пн–Пт с 09:00 до 19:00 \(по согласованию\)\.</p>',
        '<div class="font-headline-sm text-headline-sm text-on-surface my-space-xs leading-snug">Москва и Московская область</div>'
        '<p class="font-body-sm text-body-sm text-on-surface-variant">Адрес офиса уточним после заявки. Оставьте контакты — менеджер свяжется и согласует визит.</p>',
        html,
        count=1,
    )
    # Map caption with Presnenskaya
    html = html.replace(
        "Центральный пункт: Пресненская наб., 12, Москва-Сити",
        "Работаем по Москве и Московской области",
    )
    html = re.sub(
        r'data-location="Moscow, Presnenskaya Embankment, 12, Federation Tower"',
        'data-location="Moscow"',
        html,
    )
    html = html.replace("Хаб диспетчеризации: Сити", "Зона обслуживания")
    return html


BOOKING_FORM_SECTION = r'''
<!-- Lead Form Section -->
<section class="w-full bg-surface-container-low py-space-xl" id="booking-form">
<div class="max-w-[1360px] mx-auto px-6 lg:px-12"><div class="bg-surface-container-lowest rounded-xl shadow-md p-space-xl grid grid-cols-1 lg:grid-cols-12 gap-6"><div class="lg:col-span-5 flex flex-col justify-between gap-space-lg"><div class="flex flex-col gap-space-xs"><span class="font-label-md text-label-md uppercase tracking-wider text-tertiary">Бронирование мобильного экипажа</span><h2 class="font-headline-lg text-headline-lg text-on-surface font-semibold tracking-tight">Заявка на генеральную уборку коттеджа</h2><p class="font-body-md text-body-md text-on-surface-variant leading-relaxed">Опишите этажность и площадь — технолог свяжется, уточнит детали и закрепит дату выезда бригады.</p></div><div class="flex flex-col gap-space-sm bg-surface-container-low p-space-md rounded-xl"><div class="flex items-center gap-space-xs text-on-surface font-headline-sm text-sm font-semibold"><span class="material-symbols-outlined text-tertiary text-[20px]">security</span><span class="">Гарантия конфиденциальности NDA</span></div><p class="font-body-sm text-body-sm text-on-surface-variant">Персонал проходит проверку и подписывает соглашение о неразглашении.</p></div><div class="flex items-center gap-space-md font-body-sm text-body-sm text-on-surface-variant"><div class="flex items-center gap-1.5"><span class="material-symbols-outlined text-tertiary text-[18px]">done</span><span class="">Без предоплаты</span></div><div class="flex items-center gap-1.5"><span class="material-symbols-outlined text-tertiary text-[18px]">done</span><span class="">Оплата по факту</span></div><div class="flex items-center gap-1.5"><span class="material-symbols-outlined text-tertiary text-[18px]">done</span><span class="">Безнал / Карты</span></div></div></div><div class="lg:col-span-7 flex flex-col gap-space-md"><form class="grid grid-cols-1 sm:grid-cols-2 gap-6 lead-form" method="post" action="#" novalidate data-goal-event="lead_submit"><div class="sm:col-span-2 flex flex-col gap-1.5"><label class="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Тип объекта</label><div class="w-full h-[52px] px-space-md bg-surface-container-low rounded flex items-center justify-between text-on-surface font-body-md text-body-md"><span class="font-semibold flex items-center gap-space-xs"><span class="material-symbols-outlined text-tertiary text-[20px]">cottage</span>Дом / Коттедж / Таунхаус</span><span class="font-label-sm text-label-sm px-space-xs py-0.5 rounded bg-surface-container text-on-surface-variant">Фиксировано</span></div></div><div class="flex flex-col gap-1.5"><label class="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold" for="name">Ваше имя</label><input id="name" name="name" class="w-full h-[52px] px-space-md bg-surface-container-lowest rounded text-on-surface font-body-md text-body-md placeholder-outline-variant focus:outline-none focus:ring-1 focus:ring-primary shadow-sm" placeholder="Имя" required type="text"></div><div class="flex flex-col gap-1.5"><label class="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold" for="phone">Контактный телефон</label><input id="phone" name="phone" class="w-full h-[52px] px-space-md bg-surface-container-lowest rounded text-on-surface font-body-md text-body-md placeholder-outline-variant focus:outline-none focus:ring-1 focus:ring-primary shadow-sm" placeholder="+7 (___) ___-__-__" required type="tel"></div><div class="flex flex-col gap-1.5"><label class="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold" for="object-type">Этажность / тип</label><input id="object-type" name="object-type" class="w-full h-[52px] px-space-md bg-surface-container-lowest rounded text-on-surface font-body-md text-body-md placeholder-outline-variant focus:outline-none focus:ring-1 focus:ring-primary shadow-sm" placeholder="Например: 2 этажа" required type="text"></div><div class="flex flex-col gap-1.5"><label class="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Площадь дома (м²)</label><input class="w-full h-[52px] px-space-md bg-surface-container-lowest rounded text-on-surface font-body-md text-body-md placeholder-outline-variant focus:outline-none focus:ring-1 focus:ring-primary shadow-sm" min="50" placeholder="280" type="number"></div><div class="sm:col-span-2 flex flex-col gap-1.5"><label class="font-label-sm text-label-sm uppercase tracking-wider text-outline font-semibold">Пожелания</label><textarea class="w-full p-space-md bg-surface-container-lowest rounded text-on-surface font-body-md text-body-md placeholder-outline-variant focus:outline-none focus:ring-1 focus:ring-primary shadow-sm resize-none" placeholder="Кратко опишите дом и задачу" rows="3"></textarea></div><p class="sm:col-span-2 form-error font-body-sm text-body-sm text-error" hidden></p><p class="sm:col-span-2 form-success font-body-sm text-body-sm text-tertiary" hidden tabindex="-1"></p><div class="sm:col-span-2 flex flex-col gap-space-xs mt-space-xs"><button class="w-full h-[54px] bg-primary-container text-on-primary font-body-sm text-body-sm font-semibold rounded hover:bg-primary transition-colors flex items-center justify-center gap-space-xs shadow-md" type="submit"><span class="">Оставить заявку</span><span class="material-symbols-outlined text-[18px]">done_all</span></button><p class="font-label-sm text-label-sm text-outline text-center">Нажимая кнопку, вы подтверждаете согласие на обработку данных.</p></div></form></div></div></div>
</section>
'''


def ensure_dom_generalnaya_form(html: str) -> str:
    if 'id="booking-form"' in html and "lead-form" in html and 'data-goal-event="lead_submit"' in html:
        return html
    # Insert before </main>
    if "</main>" in html:
        return html.replace("</main>", BOOKING_FORM_SECTION + "</main>", 1)
    return html


def write_robots_and_sitemap(index_paths: list[str]) -> None:
    (SITE / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://klineto.ru/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = []
    for path in index_paths:
        loc = BASE + ("/" if path == "/" else path)
        urls.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            "  </url>"
        )
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n",
        encoding="utf-8",
    )


def main() -> None:
    contracts = parse_contracts(CONTRACTS.read_text(encoding="utf-8"))
    index_yes = sorted(
        [p for p, m in contracts.items() if m.get("index") == "yes"],
        key=lambda p: (p != "/", p),
    )
    write_robots_and_sitemap(index_yes)

    changed = []

    for path, meta in contracts.items():
        f = path_to_file(path)
        if not f.exists():
            print("MISSING", path)
            continue
        html = f.read_text(encoding="utf-8")
        orig = html

        if meta.get("index") == "no":
            html = upsert_head_meta(
                html,
                title=meta.get("title") or None,
                description=None,
                canonical=None,
                robots="noindex, nofollow",
            )
        elif meta.get("index") == "yes":
            canon = BASE + ("/" if path == "/" else path)
            html = upsert_head_meta(
                html,
                title=meta.get("title"),
                description=meta.get("description"),
                canonical=canon,
                robots=None,
            )
            # Remove accidental noindex on indexable pages
            html = re.sub(
                r'<meta\s+name=["\']robots["\']\s+content=["\']noindex[^"\']*["\']\s*/?>',
                "",
                html,
                flags=re.I,
            )
            h1 = meta.get("h1") or ""
            if h1:
                html = demote_extra_h1(html, h1)
            schema = meta.get("schema") or ""
            if schema == "Organization":
                html = upsert_json_ld(html, "Organization", path, "Klineto")
            elif schema == "Service":
                html = upsert_json_ld(html, "Service", path, h1 or "Klineto")

        if path == "/uborka-domov/generalnaya":
            html = ensure_dom_generalnaya_form(html)
        if path == "/kontakty":
            html = fix_kontakty(html)

        html = fix_footer_and_internal_hashes(html)
        html = strip_fake_emails(html)

        if html != orig:
            f.write_text(html, encoding="utf-8")
            changed.append(path)

    # Extra / noindex pages not fully listed as index:no in contracts
    for path in EXTRA_NOINDEX:
        f = path_to_file(path)
        if not f.exists():
            print("MISSING_EXTRA", path)
            continue
        html = f.read_text(encoding="utf-8")
        orig = html
        title_m = re.search(r"<title\b[^>]*>(.*?)</title>", html, flags=re.I | re.S)
        title = title_m.group(1).strip() if title_m else None
        html = upsert_head_meta(
            html,
            title=title,
            description=None,
            canonical=None,
            robots="noindex, nofollow",
        )
        if path == "/kontakty":
            html = fix_kontakty(html)
        html = fix_footer_and_internal_hashes(html)
        html = strip_fake_emails(html)
        if html != orig:
            f.write_text(html, encoding="utf-8")
            changed.append(path + " (noindex)")

    # Remaining HTML pages: footer/email sweeps
    for f in SITE.rglob("*.html"):
        rel = "/" + str(f.relative_to(SITE).parent).replace("\\", "/")
        if rel.endswith("/."):
            rel = "/"
        if f.name != "index.html":
            continue
        html = f.read_text(encoding="utf-8")
        orig = html
        html = fix_footer_and_internal_hashes(html)
        html = strip_fake_emails(html)
        if html != orig:
            f.write_text(html, encoding="utf-8")
            if str(f) not in changed:
                changed.append(str(f.relative_to(SITE)))

    print("INDEX_YES", len(index_yes))
    print("CHANGED", len(changed))
    for c in changed[:80]:
        print(" -", c)


if __name__ == "__main__":
    main()
