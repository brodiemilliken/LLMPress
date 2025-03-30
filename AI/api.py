from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
from typing import List, Tuple, Any
import uvicorn
import datetime
from ChatGPT2 import GPT2
from llm_tokenize import encode_text
from llm_detokenize import decode_tokens

# Initialize model - loaded once and shared across requests
model = None
model_loaded = False

app = FastAPI(
    title="LLMPress AI API", 
    description="API for GPT-2 text operations",
    version="1.0.0"
)

# Pydantic models for request/response validation
class TokenizeRequest(BaseModel):
    text: str

class DetokenizeRequest(BaseModel):
    tokens: List[List[Any]]  # Changed from List[int] to accept [type, value] format

class ListRankTokensRequest(BaseModel):
    tokens: List[int]
    k: int = 5

class PredictionRequest(BaseModel):
    text: str
    k: int = 5

# Startup event to load model once when the server starts
@app.on_event("startup")
async def startup_event():
    global model, model_loaded
    print("Loading GPT-2 model...")
    try:
        model = GPT2()
        model_loaded = True
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        model_loaded = False

@app.get("/", status_code=200)
async def root():
    """Health check endpoint"""
    global model_loaded
    if not model_loaded:
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="LLMPress API is starting up - model not yet loaded"
        )
    return {"status": "LLMPress API is running", "model_loaded": True}

# Check model is loaded middleware
@app.middleware("http")
async def check_model_loaded(request, call_next):
    global model_loaded
    # Skip check for root endpoint to allow health checks
    if request.url.path != "/":
        if not model_loaded:
            return Response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content="LLMPress API is starting up - model not yet loaded"
            )
    response = await call_next(request)
    return response

@app.post("/tokenize", response_model=List[Tuple[str, int]])
async def api_tokenize(request: TokenizeRequest):
    print("Tokenizing text...")
    try:
        return encode_text(request.text, model, k=64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detokenize", response_model=str)
async def api_detokenize(request: DetokenizeRequest):
    try:
        return decode_tokens(request.tokens, model, k=64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify hot reloading"""
    return {"message": "Hot reloading is working!", "timestamp": str(datetime.datetime.now())}

if __name__ == "__main__":
    uvicorn.run("AI.api:app", host="0.0.0.0", port=8000, workers=1)