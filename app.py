from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def home():
    return {"ok": True, "message": "Python API is running on Vercel"}

@app.post("/run")
def run(data: dict):
    text = data.get("text", "")
    return {
        "ok": True,
        "original": text,
        "upper": text.upper()
    }