import whisper
from config import WHISPER_MODEL

_model = None

def get_model():
    global _model
    if _model is None:
        print(f"Cargando modelo Whisper '{WHISPER_MODEL}'... (esto puede tardar un poco la primera vez)")
        _model = whisper.load_model(WHISPER_MODEL)
    return _model

def transcribe_audio(file_path):
    """
    Transcribes the audio file using Whisper.
    Returns the transcript text.
    """
    model = get_model()
    try:
        result = model.transcribe(file_path)
        return result["text"].strip()
    except Exception as e:
        print(f"Error transcribiendo {file_path}: {e}")
        return ""
