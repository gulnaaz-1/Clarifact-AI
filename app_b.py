from fastapi import FastAPI
from pydantic import BaseModel
from scorer import compute_risk
from utils.geo import detect_geolocation

app = FastAPI()

class Post(BaseModel):
    title: str
    text: str = ""
    url: str = ""
    image: str = ""

@app.post("/analyze")
async def analyze(post: Post):
    risk = compute_risk(post.dict())
    geo = detect_geolocation(post.url)

    return {
        "risk": risk,
        "geolocation": geo,
        "image": post.image,
        "title": post.title,
        "text": post.text
    }
