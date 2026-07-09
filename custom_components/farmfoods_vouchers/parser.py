import hashlib

from bs4 import BeautifulSoup


def parse_vouchers(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    active_section = soup.find(id="active_vouchers")
    if not active_section:
        return []

    vouchers = []
    for well in active_section.find_all("div", class_="well"):
        h3_tag = well.find("h3")
        if not h3_tag:
            continue

        code = h3_tag.get_text(strip=True)
        discount = ""
        valid_from = ""
        expires = ""

        for h4 in well.find_all("h4"):
            style = h4.get("style", "")
            text = h4.get_text(strip=True)
            if "color:red" in style:
                discount = text
            elif text.startswith("Valid From:"):
                valid_from = text.removeprefix("Valid From:").strip()
            elif text.startswith("Expires:"):
                expires = text.removeprefix("Expires:").strip()

        voucher_id = hashlib.sha256(code.encode()).hexdigest()[:16]

        vouchers.append({
            "id": voucher_id,
            "code": code,
            "discount": discount,
            "valid_from": valid_from,
            "expires": expires,
        })

    return vouchers


def active_vouchers_section_exists(html: str) -> bool:
    return len(parse_vouchers(html)) > 0
