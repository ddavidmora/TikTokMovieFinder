import os
import yt_dlp


def download_audio_from_tiktok(video_url, output_filename="temp_audio"):
    """
    Downloads ONLY the audio from a TikTok video and converts it to MP3.
    Returns the path to the file.
    """
    # Delete existing temp file if it exists
    if os.path.exists(f"{output_filename}.mp3"):
        os.remove(f"{output_filename}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_filename,  # FileName template
        'quiet': True,
        'no_warnings': True,
    }

    print(f"👂 Extracting Audio from: {video_url}...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        final_path = f"{output_filename}.mp3"
        if os.path.exists(final_path):
            return final_path
        else:
            return None

    except Exception as e:
        print(f"❌ Audio Download Error (Do you have FFmpeg installed?): {e}")
        return None