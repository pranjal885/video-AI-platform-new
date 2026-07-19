import os
from faster_whisper import WhisperModel

# Global model variable
model = None


def get_model():
    global model

    if model is None:
        print("Loading Whisper Model...")

        model = WhisperModel(
            "tiny",      # Change to "tiny" if you need lower memory
            device="cpu",
            compute_type="int8"
        )

        print("Whisper Model Loaded Successfully!")

    return model


def transcribe_audio(audio_path, language="auto"):

    model = get_model()

    print("\n==============================")
    print("Starting Transcription...")
    print("==============================\n")

    if language == "auto":

        print("Language Mode : Auto Detect")

        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True
        )

    else:

        print(f"Language Mode : {language}")

        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            language=language
        )

    segments = list(segments)

    transcript_lines = []

    for segment in segments:

        text = segment.text.strip()

        if text:
            transcript_lines.append(text)

    transcript = "\n".join(transcript_lines)

    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    filename = os.path.splitext(
        os.path.basename(audio_path)
    )[0]

    transcript_path = os.path.join(
        output_folder,
        filename + ".txt"
    )

    with open(
        transcript_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(transcript)

    print(f"Detected Language : {info.language}")
    print(f"Language Probability : {info.language_probability:.2f}")
    print(f"Transcript Saved : {transcript_path}")
    print(f"Segments Found : {len(transcript_lines)}")
    print("Transcription Completed Successfully!\n")

    return transcript, transcript_path, segments