import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llama3.2:3b"


def ask_llm(context, question):

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

        response = requests.post(

            OLLAMA_URL,

            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },

            timeout=120

        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "No response received from the model."
        )

    except requests.exceptions.ConnectionError:

        return (
            "Unable to connect to Ollama.\n\n"
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "The AI model took too long to respond."
        )

    except Exception as e:

        return f"Unexpected Error:\n{str(e)}"