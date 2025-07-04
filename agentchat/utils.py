import os
import requests
from dotenv import load_dotenv
import logging
import openai
import json

load_dotenv()

HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentchat.utils")

# OpenAI chat utility
def openai_chat(prompt: str, model: str = "gpt-3.5-turbo"):
    openai.api_key = OPENAI_API_KEY
    try:
        logger.info(f"Calling OpenAI Chat API: model={model}, prompt={prompt}")
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512,
        )
        logger.info(f"OpenAI response: {response}")
        content = response.choices[0].message.content
        if content is not None:
            return content.strip()
        else:
            return "[Agent Error] No content returned from OpenAI."
    except Exception as e:
        logger.error(f"OpenAI chat error: {e}")
        return f"[Agent Error] {e}"

# General function to call Hugging Face Inference API
def hf_inference(model: str, inputs: dict):
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    logger.info(f"Calling HF API: {url} with inputs: {inputs}")
    try:
        response = requests.post(url, headers=headers, json=inputs)
        logger.info(f"HF API response status: {response.status_code}")
        response.raise_for_status()
        logger.info(f"HF API response: {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"HF API error: {e}")
        raise

# Chat/completion (fallback to HF if needed)
def hf_chat(prompt: str, model: str = "bigscience/bloomz-560m"):
    inputs = {"inputs": prompt}
    try:
        result = hf_inference(model, inputs)
        # Try to extract the generated text
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        return str(result)
    except Exception as e:
        logger.error(f"hf_chat error: {e}")
        return f"[Agent Error] {e}"

# Summarization (e.g., facebook/bart-large-cnn)
def hf_summarize(text: str, model: str = "facebook/bart-large-cnn"):
    inputs = {"inputs": text}
    try:
        result = hf_inference(model, inputs)
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]
        elif isinstance(result, dict) and "summary_text" in result:
            return result["summary_text"]
        return str(result)
    except Exception as e:
        logger.error(f"hf_summarize error: {e}")
        return f"[Agent Error] {e}"

def detect_intent(user_message: str):
    system_prompt = (
        "You are an intent detection assistant. "
        "If the user asks for news, extract the country and return a JSON: "
        '{"intent": "news", "country": "..."} '
        "Otherwise, return {\"intent\": \"chat\"}."
    )
    prompt = f"{system_prompt}\nUser: {user_message}\nAssistant:"
    response = openai_chat(prompt)
    try:
        return json.loads(response)
    except Exception:
        return {"intent": "chat"} 