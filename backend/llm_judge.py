import os
from huggingface_hub import InferenceClient

def _get_client() -> InferenceClient:
    # Load token from .env file
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is missing. Put it in .env")
    return InferenceClient(token=token)


def judge_news(text: str) -> dict:
    model = os.getenv("HF_MODEL", "meta-llama/Llama-3.3-70B-Instruct")
    client = _get_client()

    prompt = (
        "You are a misinformation detector. Analyze the news text and output ONLY a JSON object with keys:\n"
        'label (one of "fake", "real", "uncertain"), confidence (0-100 integer), explanation (short string).\n\n'
        f"News:\n{text}\n"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON. No extra text."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=250,
        temperature=0.2,
    )

    print(f"Model response: {resp}")  

    try:
        model_output = resp.choices[0].message.content.strip()  
        print(f"Parsed model output: {model_output}")  
        model_output = eval(model_output)  

        label = model_output.get("label", "uncertain")
        confidence = model_output.get("confidence", 0)
        explanation = model_output.get("explanation", "")
    except Exception as e:
        print(f"Error parsing model output: {e}")
        label = "uncertain"
        confidence = 0
        explanation = "Unable to parse the explanation"

    return {
        "label": label,
        "confidence": confidence,
        "explanation": explanation
    }
