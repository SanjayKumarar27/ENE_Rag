from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import fasttext
import os
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo

app = FastAPI()

# Load pre-trained FastText model from a relative path
# Use a relative path inside the Docker container
model_path = "/app/models/custom_fasttext_model.bin"

# Ensure the model file is present
if not os.path.isfile(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

model = fasttext.load_model(model_path)

FIFTEEN_MINUTES = 900

class WordRequest(BaseModel):
    word: str

@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=15, period=FIFTEEN_MINUTES)
@app.post("/similar_words")
async def get_similar_words(request: WordRequest):
    word = request.word
    try:
        similar_words = model.get_nearest_neighbors(word, k=10)
        return {"similar_words": [similar_word for _, similar_word in similar_words]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
