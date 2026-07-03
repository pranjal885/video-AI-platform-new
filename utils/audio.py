import os

from moviepy import VideoFileClip


def extract_audio(video_path):

    print("\nExtracting Audio...")

    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    filename = os.path.splitext(
        os.path.basename(video_path)
    )[0]

    audio_path = os.path.join(
        output_folder,
        filename + ".wav"
    )

    video = None

    try:

        video = VideoFileClip(video_path)

        if video.audio is None:
            raise Exception("The uploaded video does not contain an audio track.")

        video.audio.write_audiofile(
            audio_path,
            codec="pcm_s16le",
            logger=None
        )

        print(f"Audio Saved : {audio_path}")

        return audio_path

    except Exception as e:

        raise Exception(
            f"Audio extraction failed.\n{str(e)}"
        )

    finally:

        if video is not None:
            video.close()