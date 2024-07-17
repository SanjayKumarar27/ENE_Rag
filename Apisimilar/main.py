from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import fasttext
import os

app = FastAPI()

# Load pre-trained FastText model
model_path = os.getenv("custom_fasttext_model.bin", "custom_fasttext_model.bin")
model = fasttext.load_model(model_path)

class WordRequest(BaseModel):
    word: str

@app.post("/similar_words")
async def get_similar_words(request: WordRequest):
    word = request.word
    similar_words = model.get_nearest_neighbors(word, k=10)
    return {"similar_words": [similar_word for _, similar_word in similar_words]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
