from transformers import pipeline

# Global summarizer variable
summarizer = None


def get_summarizer():
    """
    Load the summarization model only once.
    """
    global summarizer

    if summarizer is None:
        print("Loading Summary Model...")

        summarizer = pipeline(
            task="summarization",
            model="facebook/bart-large-cnn"
        )

        print("Summary Model Loaded Successfully!")

    return summarizer


def chunk_text(text, chunk_size=2500):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(
            text[i:i + chunk_size]
        )

    return chunks


def generate_summary(text):

    # Load model only when needed
    summarizer = get_summarizer()

    if len(text.split()) < 60:
        return text

    chunks = chunk_text(text)

    summaries = []

    for chunk in chunks:

        result = summarizer(
            chunk,
            max_length=150,
            min_length=40,
            do_sample=False
        )

        summaries.append(
            result[0]["summary_text"]
        )

    final_summary = "\n\n".join(summaries)

    return final_summary