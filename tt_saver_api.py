# tiktok_downloader_best.py
import asyncio
import os
import re
import subprocess
import aiohttp
from datetime import datetime

DOWNLOAD_FOLDER = "videos"

# Các dịch vụ đang hoạt động tốt hơn (cập nhật 2026)
SERVICES = [
    # {
        # "name": "SSSTik",
        # "url": "https://ssstik.io/abc?url=dl",
        # "referer": "https://ssstik.io/"
    # },
    # {
        # "name": "SnapTik",
        # "url": "https://snaptik.app/en2",
        # "referer": "https://snaptik.app/"
    # },
    {
        "name": "TikWM",
        "url": "https://tikwm.com/api/",
        "referer": "https://tikwm.com/"
    },
]

async def get_video_url(tiktok_link: str):
    headers_base = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    }

    for service in SERVICES:
        print(f"Đang thử {service['name']}...")

        try:
            async with aiohttp.ClientSession() as session:
                if "tikwm" in service['url'].lower():
                    # TikWM dùng API GET
                    params = {"url": tiktok_link, "hd": "1"}
                    async with session.get(service['url'], params=params, headers=headers_base) as resp:
                        data = await resp.json()
                        if data.get("code") == 0:
                            video_url = data.get("data", {}).get("play")
                            if video_url:
                                print(f"✅ {service['name']} thành công!")
                                return video_url
                else:
                    # SSSTik và SnapTik dùng POST
                    async with session.post(
                        service['url'],
                        data={"url": tiktok_link},
                        headers={**headers_base, "Referer": service['referer']}
                    ) as resp:
                        html = await resp.text()

                        # Tìm link mp4 không watermark
                        matches = re.findall(r'href="(https?://[^"]+\.mp4[^"]*)"', html, re.IGNORECASE)
                        if matches:
                            # Ưu tiên link không chứa "watermark"
                            for link in matches:
                                if "watermark" not in link.lower():
                                    print(f"✅ {service['name']} thành công!")
                                    return link
                            print(f"✅ {service['name']} thành công (dùng link đầu tiên)")
                            return matches[0]

        except Exception as e:
            print(f"{service['name']} lỗi: {e}")

    print("❌ Tất cả dịch vụ đều thất bại.")
    return None


async def download_video(video_url: str, filename: str):
    print(f"Đang tải: {filename}")
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }) as resp:
                if resp.status != 200:
                    print(f"Tải thất bại (Status: {resp.status})")
                    return False

                with open(filepath, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)
                print("✅ Tải video thành công!")
                return True
    except Exception as e:
        print(f"Lỗi tải: {e}")
        return False


async def remove_watermark(input_path: str):
    output_path = input_path.replace('_water.mp4', '_nowater.mp4')
    print("Đang cắt watermark bằng ffmpeg (nếu cần)...")

    command = ['ffmpeg', '-i', input_path, '-vf', 'crop=in_w:in_h-185:0:0', 
               '-c:a', 'copy', '-y', output_path]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if result.returncode == 0:
            os.remove(input_path)
            print(f"✅ Cắt watermark thành công → {output_path}")
            return output_path
        else:
            return input_path
    except Exception:
        return input_path


async def main():
    print("=== TikTok Downloader (SSSTik + SnapTik + TikWM) ===\n")

    link = input("Dán link TikTok: ").strip()
    if not link:
        return

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    timestamp = int(datetime.now().timestamp())
    filename = f"tiktok_{timestamp}_water.mp4"

    video_url = await get_video_url(link)
    if not video_url:
        print("\n❌ Không dịch vụ nào hoạt động.")
        print("   Gợi ý: Thử lại sau 5-10 phút hoặc dùng trình duyệt thủ công (ssstik.io / snaptik.gd).")
        return

    success = await download_video(video_url, filename)
    if not success:
        return

    final_path = await remove_watermark(os.path.join(DOWNLOAD_FOLDER, filename))

    print("\n🎉 HOÀN TẤT!")
    print(f"File: {final_path}")


if __name__ == "__main__":
    asyncio.run(main())