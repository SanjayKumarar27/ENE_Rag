from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from middleware import RateLimitMiddleware
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo

app = FastAPI()

# Add RateLimitMiddleware with proper configuration
app.add_middleware(RateLimitMiddleware, max_requests=15, window=900)

class WordRequest(BaseModel):
    word: str

@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=15, period=900)
@app.post("/similar_words")
async def get_similar_words(request: WordRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://word_similarity_service:8001/similar_words", json=request.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
