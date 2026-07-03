import os

from flask import (
    Flask,
    render_template,
    request,
    send_file
)

from werkzeug.utils import secure_filename

from utils.audio import extract_audio
from utils.transcriber import transcribe_audio
from utils.summary import generate_summary
from utils.subtitle import generate_subtitle
from utils.pdf_generator import generate_pdf
from utils.doc_generator import generate_doc
from utils.embeddings import store_transcript, search_transcript
from utils.chatbot import ask_llm

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Stores current uploaded file information
current_video = {
    "filename": "",
    "audio": "",
    "transcript": "",
    "summary": "",
    "transcript_path": "",
    "subtitle_path": "",
    "pdf_path": "",
    "doc_path": "",
    "language": ""
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "video" not in request.files:
        return "No file selected."

    file = request.files["video"]

    if file.filename == "":
        return "No file selected."

    # Get selected language
    language = request.form.get("language", "auto")

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    print("✅ Video Uploaded")
    print(f"🌍 Selected Language : {language}")

    audio_path = extract_audio(filepath)

    print("✅ Audio Extracted")

    # Pass language to Whisper
    transcript, transcript_path = transcribe_audio(
        audio_path,
        language
    )

    print("✅ Transcript Generated")

    summary = generate_summary(transcript)

    print("✅ Summary Generated")

    subtitle_path = generate_subtitle(
    audio_path,
    language
    )
    
    print("✅ Subtitle Generated")

    store_transcript(transcript)

    print("✅ Transcript Stored in ChromaDB")

    base_name = os.path.splitext(filename)[0]

    pdf_path = generate_pdf(
        summary,
        base_name
    )

    doc_path = generate_doc(
        summary,
        base_name
    )

    current_video["filename"] = filename
    current_video["audio"] = audio_path
    current_video["transcript"] = transcript
    current_video["summary"] = summary
    current_video["transcript_path"] = transcript_path
    current_video["subtitle_path"] = subtitle_path
    current_video["pdf_path"] = pdf_path
    current_video["doc_path"] = doc_path
    current_video["language"] = language

    return render_template(
        "result.html",
        filename=current_video["filename"],
        audio=current_video["audio"],
        transcript=current_video["transcript"],
        summary=current_video["summary"],
        language=current_video["language"]
    )


@app.route("/download_transcript")
def download_transcript():

    return send_file(
        current_video["transcript_path"],
        as_attachment=True
    )


@app.route("/download_subtitle")
def download_subtitle():

    return send_file(
        current_video["subtitle_path"],
        as_attachment=True
    )


@app.route("/download_pdf")
def download_pdf():

    return send_file(
        current_video["pdf_path"],
        as_attachment=True
    )


@app.route("/download_doc")
def download_doc():

    return send_file(
        current_video["doc_path"],
        as_attachment=True
    )


@app.route("/chat", methods=["POST"])
def chat():

    question = request.form["question"]

    context = search_transcript(question)

    answer = ask_llm(
        context,
        question
    )

    return render_template(
        "result.html",
        filename=current_video["filename"],
        audio=current_video["audio"],
        transcript=current_video["transcript"],
        summary=current_video["summary"],
        language=current_video["language"],
        answer=answer
    )


if __name__ == "__main__":
    app.run(debug=False)