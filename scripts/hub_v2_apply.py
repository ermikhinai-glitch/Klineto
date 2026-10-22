#!/usr/bin/env python3
"""Publish Klineto hub v2 screens, inject SEO, fix links, normalize lead forms."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
V2 = Path("/tmp/stitch_v2/stitch_klineto_cleaning_service_hub")

# New screens from hub v2 → URL (None SEO if not in site-content)
NEW_SCREENS = {
    "klineto_1": {
        "url": "/",
        "title": "Клининг в Москве и области — Klineto",
        "description": "Клининг квартир, домов и офисов в Москве и Московской области. Оставьте заявку на сайте.",
        "seo_h1": "Клининг в Москве и Московской области",
        "seo_paragraphs": [
            "Klineto работает с частными заказчиками и с организациями. Квартиру и дом убирают для человека, который там живёт или готовит жильё к заезду. Офис убирают для компании, которой нужно открыть помещение для сотрудников.",
            "В квартире это комнаты, кухня и санузел. В доме к ним добавляются этажи, лестница и вход, через который носят уличную грязь. В офисе важны рабочие места, переговорные, кухня и санузел. Объём каждый раз свой: разовый визит, тщательная уборка или повторяющийся график.",
            "География одна — Москва и Московская область. В заявке напишите тип объекта и своими словами, что должно быть готово. Этого хватает, чтобы понять задачу до выезда.",
        ],
        "schema": "Organization",
        "index": True,
    },
    "b2b_klineto": {
        "url": "/korporativnym",
        "title": "Корпоративный клининг — Klineto",
        "description": "Корпоративный клининг офисов в Москве и Московской области. Оставьте заявку на сайте.",
        "seo_h1": None,
        "seo_paragraphs": None,
        "schema": None,
        "index": False,
    },
    "klineto_2": {
        "url": "/o-kompanii",
        "title": "О компании — Klineto",
        "description": "О клининговой компании Klineto в Москве и Московской области.",
        "seo_h1": None,
        "seo_paragraphs": None,
        "schema": None,
        "index": False,
    },
    "klineto_3": {
        "url": "/kontakty",
        "title": "Контакты — Klineto",
        "description": "Контакты Klineto. Оставьте заявку: имя, телефон, тип объекта, комментарий.",
        "seo_h1": None,
        "seo_paragraphs": None,
        "schema": None,
        "index": False,
    },
    "klineto_4": {
        "url": "/kalkulyator",
        "title": "Калькулятор и бронирование — Klineto",
        "description": "Рассчитайте уборку и оставьте заявку в Klineto.",
        "seo_h1": None,
        "seo_paragraphs": None,
        "schema": None,
        "index": False,
    },
    "klineto_5": {
        "url": "/tarify",
        "title": "Тарифы — Klineto",
        "description": "Тарифы на клининг Klineto в Москве и Московской области.",
        "seo_h1": None,
        "seo_paragraphs": None,
        "schema": None,
        "index": False,
    },
    "klineto_6": {
        "url": "/zayavka-prinyata",
        "title": "Заявка принята — Klineto",
        "description": "Ваша заявка в Klineto принята.",
        "seo_h1": None,
        "seo_paragraphs": None,
        "schema": None,
        "index": False,
    },
}

# Exact link text → URL (longest keys preferred via sort)
TEXT_LINKS: dict[str, str] = {
    "Главная": "/",
    "Квартиры": "/uborka-kvartir",
    "Квартиры и пентхаусы": "/uborka-kvartir",
    "Квартиры и апартаменты": "/uborka-kvartir",
    "Уборка апартаментов и квартир": "/uborka-kvartir",
    "Каталог услуг квартир": "/uborka-kvartir",
    "Дома и коттеджи": "/uborka-domov",
    "Дома": "/uborka-domov",
    "Загородные дома и коттеджи": "/uborka-domov",
    "Загородные дома": "/uborka-domov/zagorodnyj",
    "Загородные резиденции": "/uborka-domov/zagorodnyj",
    "Обслуживание загородных домов": "/uborka-domov/zagorodnyj",
    "Каталог услуг домов": "/uborka-domov",
    "Офисы": "/uborka-ofisov",
    "Офисы и БЦ": "/uborka-ofisov",
    "Офисы и бизнес-центры": "/uborka-ofisov",
    "Офисные пространства": "/uborka-ofisov",
    "Офисы класса A/B+": "/uborka-ofisov",
    "Каталог услуг офисов": "/uborka-ofisov",
    "Корпоративным клиентам": "/korporativnym",
    "Корпоративным клиентам (B2B)": "/korporativnym",
    "Корпоративный клининг": "/korporativnym",
    "Управление объектами коммерции": "/korporativnym",
    "Контакты": "/kontakty",
    "Химчистка": "/uborka-kvartir/himchistka-mebeli",
    "Премиальная химчистка": "/uborka-kvartir/himchistka-mebeli",
    "Премиальная эко-химчистка мебели": "/uborka-kvartir/himchistka-mebeli",
    "Выездная химчистка мебели и ковров": "/uborka-domov/himchistka-mebeli",
    "Химчистка ковролина и офисной мебели": "/uborka-ofisov/himchistka-mebeli",
    "Генеральная": "/uborka-kvartir/generalnaya",
    "Генеральная уборка": "/uborka-kvartir/generalnaya",
    "Комплексная генеральная уборка": "/uborka-domov/generalnaya",
    "Генеральный клининг": "/uborka-domov/generalnaya",
    "Генеральный клининг офисов": "/uborka-ofisov/generalnaya",
    "После ремонта": "/uborka-kvartir/posle-remonta",
    "Уборка после ремонта": "/uborka-kvartir/posle-remonta",
    "Уборка после строительных работ": "/uborka-domov/posle-remonta",
    "Послестроительная уборка": "/uborka-domov/posle-remonta",
    "Послестроительный клининг": "/uborka-ofisov/posle-remonta",
    "После аренды": "/uborka-kvartir/posle-arendy",
    "Поддерживающая": "/uborka-kvartir/podderzhivayushchaya",
    "Поддерживающая уборка": "/uborka-kvartir/podderzhivayushchaya",
    "Поддерживающий клининг": "/uborka-domov/podderzhivayushchaya",
    "Поддерживающая уборка в течение дня": "/uborka-ofisov/podderzhivayushchaya",
    "Мойка окон и балконов": "/uborka-kvartir/mojka-okon",
    "Мойка окон и стеклянных перегородок": "/uborka-ofisov/mojka-okon",
    "Мойка фасадов и остекления": "/uborka-domov/mojka-okon",
    "Мойка панорамного остекления": "/uborka-domov/mojka-okon",
    "Сезонная мойка остекления": "/uborka-domov/mojka-okon",
    "Фасады и витражи": "/uborka-domov/mojka-okon",
    "Коттеджи и резиденции": "/uborka-domov/kottedzhi",
    "Уборка коттеджей": "/uborka-domov/kottedzhi",
    "VIP-сопровождение резиденций": "/uborka-domov/kottedzhi",
    "VIP-обслуживание": "/uborka-domov/kottedzhi",
    "Персональный консьерж-клининг": "/uborka-domov",
    "Ежедневная уборка": "/uborka-ofisov/ezhednevnaya",
    "Постоянное обслуживание": "/uborka-ofisov/postoyannaya",
    "Разовый клининг мероприятий": "/uborka-ofisov/razovaya",
    "Комплексный клининг офисов": "/uborka-ofisov",
    "Аутсорсинг клинингового персонала": "/uborka-ofisov/postoyannaya",
    "Политика конфиденциальности": "/privacy",
    "Прайс-лист для резидентов": "/tarify",
    "Гарантии": "/o-kompanii",
    "Страхование и гарантии": "/o-kompanii",
}

DATA_PATH_LINKS: dict[str, str] = {
    "glavnaya": "/",
    "/": "/",
    "kvartiry": "/uborka-kvartir",
    "apartments": "/uborka-kvartir",
    "doma": "/uborka-domov",
    "doma-i-kottedzhi": "/uborka-domov",
    "houses-and-cottages": "/uborka-domov",
    "ofisy": "/uborka-ofisov",
    "offices": "/uborka-ofisov",
    "himchistka": "/uborka-kvartir/himchistka-mebeli",
    "dry-cleaning": "/uborka-kvartir/himchistka-mebeli",
    "himchistka-mebeli": "/uborka-kvartir/himchistka-mebeli",
    "himchistka-v-dome": "/uborka-domov/himchistka-mebeli",
    "kvartiry-generalnaya": "/uborka-kvartir/generalnaya",
    "kvartiry-posle-remonta": "/uborka-kvartir/posle-remonta",
    "kvartiry-podderzhivayushchaya": "/uborka-kvartir/podderzhivayushchaya",
    "kvartiry-okna": "/uborka-kvartir/mojka-okon",
    "kvartiry-vip": "/uborka-kvartir",
    "uborka-kottedzhej": "/uborka-domov/kottedzhi",
    "uborka-zagorodnogo-doma": "/uborka-domov/zagorodnyj",
    "generalnaya-uborka-doma": "/uborka-domov/generalnaya",
    "uborka-doma-posle-remonta": "/uborka-domov/posle-remonta",
    "podderzhivayushchaya-uborka": "/uborka-domov/podderzhivayushchaya",
    "moyka-okon-i-fasadov": "/uborka-domov/mojka-okon",
    "mojka-okon-v-dome": "/uborka-domov/mojka-okon",
    "moyka-okon-i-peregorodok": "/uborka-ofisov/mojka-okon",
    "generalnaya-uborka-ofisa": "/uborka-ofisov/generalnaya",
    "uborka-posle-remonta": "/uborka-ofisov/posle-remonta",
    "korporativnym-klientam": "/korporativnym",
    "corporate-clients": "/korporativnym",
    "kontakty": "/kontakty",
    "contacts": "/kontakty",
    "politika-konfidencialnosti": "/privacy",
    "garantii": "/o-kompanii",
    "reglament-obsluzhivaniya": "/o-kompanii",
    "garantijnye-obyazatelstva": "/o-kompanii",
    "doma/kottedzhi": "/uborka-domov/kottedzhi",
    "doma/zagorodnyj-dom": "/uborka-domov/zagorodnyj",
    "doma/generalnaya": "/uborka-domov/generalnaya",
    "doma/posle-remonta": "/uborka-domov/posle-remonta",
    "doma/podderzhivayushchaya": "/uborka-domov/podderzhivayushchaya",
    "doma/ezhednevnaya": "/uborka-domov/ezhednevnaya",
    "doma/okna": "/uborka-domov/mojka-okon",
    "doma/himchistka": "/uborka-domov/himchistka-mebeli",
    "ofisy/generalnaya": "/uborka-ofisov/generalnaya",
    "ofisy/ezhednevnaya": "/uborka-ofisov/ezhednevnaya",
    "ofisy/posle-remonta": "/uborka-ofisov/posle-remonta",
    "ofisy/postoyanno": "/uborka-ofisov/postoyannaya",
    "ofisy/podderzhivayushchaya": "/uborka-ofisov/podderzhivayushchaya",
    "ofisy/okna": "/uborka-ofisov/mojka-okon",
    "ofisy/razovaya": "/uborka-ofisov/razovaya",
    "ofisy/himchistka": "/uborka-ofisov/himchistka-mebeli",
}

PATH_REWRITES = {
    "/kvartiry": "/uborka-kvartir",
    "/kvartiry/generalnaya": "/uborka-kvartir/generalnaya",
    "/kvartiry/kompleksnaya": "/uborka-kvartir/kompleksnaya",
    "/kvartiry/posle-arendy": "/uborka-kvartir/posle-arendy",
    "/kvartiry/novostrojka": "/uborka-kvartir/novostrojka",
    "/kvartiry/podderzhivayushchaya": "/uborka-kvartir/podderzhivayushchaya",
    "/kvartiry/posle-remonta": "/uborka-kvartir/posle-remonta",
    "/kvartiry/okna": "/uborka-kvartir/mojka-okon",
    "/kvartiry/himchistka": "/uborka-kvartir/himchistka-mebeli",
}

SEO_BLOCK = """
<!-- SEO -->
<section class="w-full bg-surface px-6 lg:px-12" id="seo-block" aria-labelledby="seo-title">
<div class="max-w-7xl mx-auto border-t border-surface-container-high pt-12 pb-4">
<div class="max-w-3xl space-y-5">
<h1 id="seo-title" class="font-headline-lg text-headline-lg text-on-surface tracking-tight">{h1}</h1>
<div class="space-y-4 font-body-lg text-body-lg text-on-surface">
{paragraphs}
</div>
</div>
</div>
</section>
"""

LEAD_FORM_INNER = """
<div class="space-y-4">
<div class="field">
<label class="block font-label-sm text-label-sm uppercase text-on-surface-variant mb-2" for="name">Имя</label>
<input class="w-full h-12 px-4 rounded-lg bg-surface-container-lowest border border-surface-container-high text-on-surface font-body-md focus:outline-none focus:ring-2 focus:ring-primary" id="name" name="name" type="text" autocomplete="name"/>
</div>
<div class="field">
<label class="block font-label-sm text-label-sm uppercase text-on-surface-variant mb-2" for="phone">Телефон</label>
<input class="w-full h-12 px-4 rounded-lg bg-surface-container-lowest border border-surface-container-high text-on-surface font-body-md focus:outline-none focus:ring-2 focus:ring-primary" id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel"/>
</div>
<div class="field">
<label class="block font-label-sm text-label-sm uppercase text-on-surface-variant mb-2" for="object-type">Тип объекта</label>
<select class="w-full h-12 px-4 rounded-lg bg-surface-container-lowest border border-surface-container-high text-on-surface font-body-md focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer" id="object-type" name="object-type">
<option value="">Выберите тип</option>
<option>Квартира</option>
<option>Дом</option>
<option>Офис</option>
<option>Коммерческое помещение</option>
</select>
</div>
<div class="field">
<label class="block font-label-sm text-label-sm uppercase text-on-surface-variant mb-2" for="comment">Комментарий</label>
<textarea class="w-full min-h-[6rem] px-4 py-3 rounded-lg bg-surface-container-lowest border border-surface-container-high text-on-surface font-body-md focus:outline-none focus:ring-2 focus:ring-primary" id="comment" name="comment" rows="4"></textarea>
</div>
<p class="form-error font-body-sm text-body-sm text-error" hidden></p>
<p class="form-success font-body-sm text-body-sm text-primary" hidden tabindex="-1"></p>
<button class="inline-flex items-center justify-center w-full h-13 px-8 rounded-lg bg-primary-container hover:bg-tertiary text-on-primary font-label-md text-label-md uppercase tracking-wider transition-colors" type="submit">Оставить заявку</button>
</div>
"""


def url_to_path(url: str) -> Path:
    if url == "/":
        return SITE / "index.html"
    return SITE / url.lstrip("/") / "index.html"


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def inject_head_meta(html: str, meta: dict) -> str:
    robots = "index, follow" if meta.get("index") else "noindex, follow"
    head_extra = f'<meta name="description" content="{meta["description"]}"/>'
    head_extra += f'<meta name="robots" content="{robots}"/>'
    if meta.get("schema") == "Organization":
        head_extra += (
            '<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"Organization","name":"Klineto",'
            '"url":"https://klineto.ru/","description":"Клининг квартир, домов и офисов в Москве и Московской области."}'
            "</script>"
        )
    if re.search(r"<title>[^<]*</title>", html):
        html = re.sub(r"<title>[^<]*</title>", f"<title>{meta['title']}</title>", html, count=1)
    else:
        html = html.replace("<head>", f"<head><title>{meta['title']}</title>", 1)
    # drop existing description/robots if any, then inject before </head>
    html = re.sub(r'<meta\s+name="description"[^>]*>', "", html, flags=re.I)
    html = re.sub(r'<meta\s+name="robots"[^>]*>', "", html, flags=re.I)
    html = html.replace("</head>", head_extra + "</head>", 1)
    return html


def inject_seo(html: str, meta: dict) -> str:
    if not meta.get("seo_h1"):
        return html
    paragraphs = "\n".join(f"<p>{p}</p>" for p in meta["seo_paragraphs"])
    block = SEO_BLOCK.format(h1=meta["seo_h1"], paragraphs=paragraphs)
    # Insert after first </section> inside <main>
    main = re.search(r"<main\b[^>]*>", html, re.I)
    if not main:
        return html
    start = main.end()
    first_section_end = html.find("</section>", start)
    if first_section_end == -1:
        return html
    insert_at = first_section_end + len("</section>")
    return html[:insert_at] + block + html[insert_at:]


def ensure_form_js(html: str) -> str:
    if "/js/form.js" in html:
        return html
    tag = '<script src="/js/form.js" defer></script>'
    if "</body>" in html:
        return html.replace("</body>", tag + "</body>", 1)
    return html + tag


def normalize_forms(html: str) -> str:
    """Replace each <form>...</form> body with KPI fields; keep form tag attrs cleaned."""

    def repl(match: re.Match) -> str:
        open_tag = match.group(1)
        # keep id if present for in-page anchors
        form_id = re.search(r'\bid=["\']([^"\']+)["\']', open_tag)
        fid = form_id.group(1) if form_id else "lead-form"
        new_open = (
            f'<form class="lead-form space-y-6" id="{fid}" method="post" action="#" '
            f'novalidate data-goal-event="lead_submit">'
        )
        return new_open + LEAD_FORM_INNER + "</form>"

    return re.sub(r"(<form\b[^>]*>).*?</form>", repl, html, flags=re.S | re.I)


def resolve_link(text: str, data_path: str | None, href: str) -> str | None:
    text_clean = strip_tags(text)
    # Keep real tel/mailto/http and in-page anchors that are not bare #
    if href.startswith(("tel:", "mailto:", "http://", "https://")):
        return None
    if href.startswith("#") and href != "#":
        return None  # keep #calculator, #booking-form, etc.

    if data_path and data_path in DATA_PATH_LINKS:
        return DATA_PATH_LINKS[data_path]

    # Exact text match (prefer longer keys)
    for key in sorted(TEXT_LINKS.keys(), key=len, reverse=True):
        if text_clean == key or text_clean.startswith(key + " "):
            return TEXT_LINKS[key]

    # Partial for long card texts
    for key, url in sorted(TEXT_LINKS.items(), key=lambda kv: len(kv[0]), reverse=True):
        if key in text_clean and len(key) >= 8:
            return url

    # Card patterns with service names embedded
    card_map = [
        (r"Коттеджи", "/uborka-domov/kottedzhi"),
        (r"Загородный дом", "/uborka-domov/zagorodnyj"),
        (r"Генеральная уборка офиса", "/uborka-ofisov/generalnaya"),
        (r"Ежедневная утренняя", "/uborka-ofisov/ezhednevnaya"),
        (r"после ремонта и переезда", "/uborka-ofisov/posle-remonta"),
        (r"Постоянное сервисное", "/uborka-ofisov/postoyannaya"),
        (r"Поддерживающая чистота", "/uborka-ofisov/podderzhivayushchaya"),
        (r"Мойка окон, перегородок", "/uborka-ofisov/mojka-okon"),
        (r"Генеральная уборка", "/uborka-kvartir/generalnaya"),
        (r"После ремонта", "/uborka-kvartir/posle-remonta"),
        (r"Поддерживающая", "/uborka-domov/podderzhivayushchaya"),
        (r"Ежедневная", "/uborka-domov/ezhednevnaya"),
        (r"Мойка окон", "/uborka-domov/mojka-okon"),
        (r"Химчистка", "/uborka-domov/himchistka-mebeli"),
        (r"Жилой фонд|Квартиры и апартаменты", "/uborka-kvartir"),
        (r"Загородная жизнь|Дома и коттеджи", "/uborka-domov"),
        (r"Корпоративный B2B|Офисы и БЦ", "/uborka-ofisov"),
    ]
    for pat, url in card_map:
        if re.search(pat, text_clean, re.I):
            return url

    # Brand / logo
    if "KLINETO" in text_clean.upper() or text_clean.lower().startswith("klineto"):
        return "/"

    if href in PATH_REWRITES:
        return PATH_REWRITES[href]

    if href == "#":
        # leftover utility links without a clear target → home sections or privacy
        if "оферт" in text_clean.lower() or "соглашен" in text_clean.lower():
            return "/privacy"
        if "регламент" in text_clean.lower() or "гарант" in text_clean.lower():
            return "/o-kompanii"
        if "telegram" in text_clean.lower() or text_clean.upper() in {"TG", "VK", "WHATSAPP", "WHATSAPP VIP", "TELEGRAM BOT", "VKONTAKTE", "INSTAGRAM"}:
            return None  # leave social placeholders as in template
        return None

    return None


def fix_links(html: str) -> str:
    def repl(match: re.Match) -> str:
        full = match.group(0)
        attrs = match.group(1)
        inner = match.group(2)
        href_m = re.search(r'\bhref=(["\'])([^"\']*)\1', attrs)
        if not href_m:
            return full
        quote, href = href_m.group(1), href_m.group(2)
        dp_m = re.search(r'\bdata-path=(["\'])([^"\']*)\1', attrs)
        data_path = dp_m.group(2) if dp_m else None
        new_href = resolve_link(inner, data_path, href)
        if not new_href or new_href == href:
            # still rewrite known wrong paths
            if href in PATH_REWRITES:
                new_href = PATH_REWRITES[href]
            else:
                return full
        new_attrs = re.sub(r'\bhref=(["\'])[^"\']*\1', f"href={quote}{new_href}{quote}", attrs, count=1)
        return f"<a{new_attrs}>{inner}</a>"

    return re.sub(r"<a(\b[^>]*)>(.*?)</a>", repl, html, flags=re.S | re.I)


def process_html(html: str, meta: dict | None = None) -> str:
    if meta:
        html = inject_head_meta(html, meta)
        html = inject_seo(html, meta)
    html = normalize_forms(html)
    html = fix_links(html)
    html = ensure_form_js(html)
    return html


def publish_new_screens() -> list[str]:
    added = []
    for folder, meta in NEW_SCREENS.items():
        src = V2 / folder / "code.html"
        if not src.is_file():
            print(f"skip missing {folder}")
            continue
        html = src.read_text(encoding="utf-8")
        html = process_html(html, meta)
        dest = url_to_path(meta["url"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        added.append(meta["url"])
        print(f"published {folder} -> {meta['url']} ({dest})")
    return added


def fix_existing_stitch_pages() -> int:
    count = 0
    for path in SITE.rglob("index.html"):
        html = path.read_text(encoding="utf-8")
        if "cdn.tailwindcss.com" not in html:
            continue
        # Skip if this path was just published from v2 in this run — still re-fix is fine
        updated = process_html(html, meta=None)
        # Avoid double SEO injection: process_html without meta won't inject SEO
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            count += 1
            print(f"fixed {path.relative_to(SITE)}")
    return count


def main() -> None:
    added = publish_new_screens()
    fixed = fix_existing_stitch_pages()
    # Count remaining bare href="#"
    bare = 0
    samples = []
    for path in SITE.rglob("*.html"):
        html = path.read_text(encoding="utf-8")
        if "cdn.tailwindcss.com" not in html:
            continue
        for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', html, re.S | re.I):
            href_m = re.search(r'\bhref=(["\'])#\1', m.group(1))
            if href_m:
                bare += 1
                if len(samples) < 25:
                    samples.append((str(path.relative_to(SITE)), strip_tags(m.group(2))[:60]))
    print(f"added={added}")
    print(f"fixed_pages={fixed}")
    print(f"remaining_href_hash={bare}")
    for s in samples:
        print("  #", s)


if __name__ == "__main__":
    main()
