import os

from faster_whisper import WhisperModel

print("Loading Subtitle Generator...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Subtitle Generator Ready!")


def format_timestamp(seconds):

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{secs:02},"
        f"{milliseconds:03}"
    )


def generate_subtitle(audio_path, language="auto"):

    print("\nGenerating Subtitle File...")

    if language == "auto":

        print("Subtitle Language : Auto Detect")

        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True
        )

    else:

        print(f"Subtitle Language : {language}")

        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            language=language
        )

    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    filename = os.path.splitext(
        os.path.basename(audio_path)
    )[0]

    subtitle_path = os.path.join(
        output_folder,
        filename + ".srt"
    )

    segment_count = 0

    with open(
        subtitle_path,
        "w",
        encoding="utf-8"
    ) as file:

        for index, segment in enumerate(segments, start=1):

            text = segment.text.strip()

            if not text:
                continue

            file.write(f"{index}\n")

            file.write(
                f"{format_timestamp(segment.start)} --> "
                f"{format_timestamp(segment.end)}\n"
            )

            file.write(text + "\n\n")

            segment_count += 1

    print(f"Subtitle Saved : {subtitle_path}")
    print(f"Subtitle Lines : {segment_count}")

    return subtitle_path