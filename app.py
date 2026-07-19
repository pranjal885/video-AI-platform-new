import os
import traceback

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

    try:

        print("1. Upload request received")

        if "video" not in request.files:
            return "No file selected."

        file = request.files["video"]

        if file.filename == "":
            return "No file selected."

        language = request.form.get("language", "auto")

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)
        print("2. Video saved")

        audio_path = extract_audio(filepath)
        print("3. Audio extracted")

        transcript, transcript_path, segments = transcribe_audio(
              audio_path,
              language
        )
        print("4. Transcript generated")

        summary = generate_summary(transcript)
        print("5. Summary generated")

        subtitle_path = generate_subtitle(
            audio_path,
            segments
        )
        print("6. Subtitle generated")

        store_transcript(transcript)
        print("7. Transcript stored in ChromaDB")

        base_name = os.path.splitext(filename)[0]

        pdf_path = generate_pdf(
            summary,
            base_name
        )
        print("8. PDF generated")

        doc_path = generate_doc(
            summary,
            base_name
        )
        print("9. DOC generated")

        current_video["filename"] = filename
        current_video["audio"] = audio_path
        current_video["transcript"] = transcript
        current_video["summary"] = summary
        current_video["transcript_path"] = transcript_path
        current_video["subtitle_path"] = subtitle_path
        current_video["pdf_path"] = pdf_path
        current_video["doc_path"] = doc_path
        current_video["language"] = language

        print("10. Returning result page")

        return render_template(
            "result.html",
            filename=current_video["filename"],
            audio=current_video["audio"],
            transcript=current_video["transcript"],
            summary=current_video["summary"],
            language=current_video["language"]
        )

    except Exception as e:
        print("\n========== ERROR ==========")
        print(str(e))
        traceback.print_exc()
        print("===========================\n")
        return f"Internal Error: {str(e)}", 500


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