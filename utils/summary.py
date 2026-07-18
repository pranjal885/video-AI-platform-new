import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_summary(text):

    prompt = f"""
You are an expert text summarizer.

Summarize the following transcript in clear bullet points.

Transcript:

{text}
"""

    response = model.generate_content(prompt)

    return response.text