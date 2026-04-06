import aiohttp
import re

SERVICES = [
    {
        "name": "TikWM",
        "url": "https://tikwm.com/api/",
        "referer": "https://tikwm.com/"
    },
]

async def get_video_url(tiktok_link: str):
    headers_base = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    }

    for service in SERVICES:
        try:
            async with aiohttp.ClientSession() as session:
                if "tikwm" in service['url'].lower():
                    params = {"url": tiktok_link, "hd": "1"}
                    async with session.get(service['url'], params=params, headers=headers_base) as resp:
                        data = await resp.json()
                        if data.get("code") == 0:
                            video_url = data.get("data", {}).get("play")
                            if video_url:
                                return video_url
                # (Có thể thêm lại SSSTik, SnapTik nếu muốn)
        except Exception:
            continue
    return None
