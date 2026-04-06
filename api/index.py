from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .tt_saver_api import get_video_url   # import tương đối

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ttsaver.blogspot.com",
        "https://www.ttsaver.blogspot.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TikTokRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"ok": True, "message": "Python API is running on Vercel"}

@app.post("/download")
async def download_tiktok(req: TikTokRequest):
    tiktok_url = req.url.strip()
    if not tiktok_url:
        raise HTTPException(status_code=400, detail="Missing url")
    
    video_url = await get_video_url(tiktok_url)
    if not video_url:
        raise HTTPException(status_code=404, detail="Cannot fetch video URL")
    
    return {"ok": True, "video_url": video_url}