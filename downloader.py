import os
import yt_dlp
from config import DOWNLOADS_DIR

def download_audio(url, video_id):
    """
    Downloads the audio track of the given URL.
    Returns the file path to the downloaded audio, or None if failed.
    """
    output_template = str(DOWNLOADS_DIR / f"{video_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': True,
        'no_warnings': True,
        # 'cookiefile': str(DOWNLOADS_DIR / "cookies.txt"), # Might be needed if yt-dlp gets blocked
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # The actual file might have .mp3 extension due to postprocessor
            expected_file = DOWNLOADS_DIR / f"{video_id}.mp3"
            if expected_file.exists():
                return str(expected_file)
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None
