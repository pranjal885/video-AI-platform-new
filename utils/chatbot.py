import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Global model variable
model = None


def get_model():
    """
    Load the Gemini model only once.
    """
    global model

    if model is None:
        print("Loading Gemini Model...")

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        print("Gemini Model Loaded Successfully!")

    return model


def ask_llm(context, question):

    model = get_model()

    prompt = f"""
You are an intelligent AI assistant for uploaded videos.

Your task is to answer ONLY from the transcript context provided below.

Rules:

1. Never make up information.
2. If the answer is not found in the context, reply exactly:
"I could not find this information in the uploaded video."
3. Keep answers clear and concise.
4. If appropriate, answer using bullet points.

------------------------
Transcript Context
------------------------

{context}

------------------------
User Question
------------------------

{question}

------------------------
Answer
------------------------
"""

    try:

        response = model.generate_content(prompt)

        if response.text:
            return response.text.strip()

        return "No response generated."

    except Exception as e:

        return f"Gemini Error:\n{str(e)}"