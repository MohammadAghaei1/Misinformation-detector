from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(payload: dict):
    # placeholder response (next step: connect LLM)
    return {
        "label": "uncertain",
        "confidence": 50,
        "explanation": "Placeholder response. LLM will be added later."
    }
