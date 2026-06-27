import sys
import argparse
import os
from database import init_db, get_untranscribed_videos, update_video_transcript, get_all_transcribed_videos
from scraper import scrape_tiktok_likes, scrape_instagram_saved
from downloader import download_audio
from transcriber import transcribe_audio
from search import compute_embedding, search_videos

def sync(login=False):
    """
    1. Scrape URLs
    2. Download audio for untranscribed videos
    3. Transcribe and Embed
    """
    print("=== Fase 1: Extracción de URLs ===")
    init_db()
    
    headless = not login
    scrape_tiktok_likes(headless=headless)
    scrape_instagram_saved(headless=headless)
    
    print("\n=== Fase 2 y 3: Descarga, Transcripción y Embeddings ===")
    pending_videos = get_untranscribed_videos()
    if not pending_videos:
        print("No hay nuevos videos para transcribir.")
        return
        
    print(f"Se encontraron {len(pending_videos)} videos pendientes.")
    
    for vid, url, platform in pending_videos:
        print(f"Procesando [{platform}] ID:{vid} -> {url}")
        
        # 1. Download
        audio_path = download_audio(url, str(vid))
        if not audio_path:
            print(f"Error descargando audio para {url}. Saltando...")
            continue
            
        # 2. Transcribe
        print("Transcribiendo...")
        transcript = transcribe_audio(audio_path)
        
        # Delete audio file after transcription
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"No se pudo eliminar el archivo temporal {audio_path}: {e}")
            
        if not transcript:
            print("Transcripción vacía o fallida. Saltando...")
            continue
            
        # 3. Embed
        print("Generando vectores (embedding)...")
        embedding = compute_embedding(transcript)
        
        # 4. Save to DB
        update_video_transcript(vid, transcript, embedding)
        print("Video procesado y guardado correctamente.\n")
        
    print("Sincronización completada.")

def search(query):
    init_db()
    stored_videos = get_all_transcribed_videos()
    if not stored_videos:
        print("No hay videos en la base de datos. Ejecuta 'sync' primero.")
        return
        
    print(f"Buscando: '{query}' en {len(stored_videos)} videos...")
    results = search_videos(query, stored_videos)
    
    print("\n=== Resultados de Búsqueda ===")
    for i, res in enumerate(results, 1):
        score_percent = int(res['score'] * 100)
        snippet = res['transcript'][:200].replace('\n', ' ') + "..."
        print(f"\n{i}. [{score_percent}% de coincidencia] {res['platform'].capitalize()}")
        print(f"   Enlace: {res['url']}")
        print(f"   Fragmento: \"{snippet}\"")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TikTok/Instagram Saved Videos Semantic Search")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Sync command
    parser_sync = subparsers.add_parser("sync", help="Sincroniza y descarga nuevos videos guardados")
    parser_sync.add_argument("--login", action="store_true", help="Abre el navegador para iniciar sesión manualmente")
    
    # Search command
    parser_search = subparsers.add_parser("search", help="Busca videos por su contenido")
    parser_search.add_argument("query", type=str, help="Descripción de lo que buscas")
    
    args = parser.parse_args()
    
    if args.command == "sync":
        sync(login=args.login)
    elif args.command == "search":
        search(args.query)
    else:
        parser.print_help()
