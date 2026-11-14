
import re
from urllib.parse import quote

PLATFORMS = {
    "Telegram": "https://t.me/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "X": "https://x.com/{}",
    "GitHub": "https://github.com/{}",
    "YouTube": "https://www.youtube.com/@{}"
}


def valid_username(username):
    username = username.strip().lstrip("@")

    if not 1 <= len(username) <= 64:
        return False

    return bool(re.fullmatch(r"[a-zA-Z0-9_.]+", username))


def search_username(username):
    username = username.strip().lstrip("@")

    if not valid_username(username):
        return None

    results = []

    for platform, url in PLATFORMS.items():
        results.append({
            "platform": platform,
            "url": url.format(quote(username))
        })

    return results


def format_results(username):
    results = search_username(username)

    if results is None:
        return "❌ Некорректный username."

    text = (
        "🕵️ <b>DEPANOV SHERLOCK</b>\n\n"
        f"🔎 Запрос: <code>@{username.lstrip('@')}</code>\n\n"
        "🌐 <b>Публичные страницы:</b>\n\n"
    )

    for result in results:
        text += (
            f"• {result['platform']}: "
            f"<a href='{result['url']}'>Открыть</a>\n"
        )

    text += (
        "\n<i>Наличие и принадлежность аккаунтов "
        "не подтверждены. Проверьте ссылки самостоятельно.</i>"
    )

    return text
  
