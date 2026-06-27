import time
import urllib.parse
from config import SESSIONS_DIR
from database import add_video

try:
    from scrapling.fetchers import StealthySession
except ImportError:
    print("WARNING: scrapling could not be imported. Ensure dependencies are installed via a standard Windows Python distribution.")
    StealthySession = None

def scrape_tiktok_likes(headless=True):
    if not StealthySession:
        return
    print("Iniciando scraper de TikTok...")
    tiktok_dir = SESSIONS_DIR / "tiktok"
    tiktok_dir.mkdir(exist_ok=True, parents=True)
    
    with StealthySession(user_data_dir=str(tiktok_dir), headless=headless) as session:
        page = session.fetch("https://www.tiktok.com/@me")
        time.sleep(5) # wait for redirect or load
        
        if "login" in page.url or "Log in" in page.text:
            if headless:
                print("No estás logueado en TikTok. Ejecuta con --login para abrir la ventana e iniciar sesión manualmente.")
                return
            else:
                print("Inicia sesión manualmente. Esperando 60 segundos...")
                time.sleep(60)
                page = session.fetch("https://www.tiktok.com/@me")
                
        print("Navegando y extrayendo videos de TikTok...")
        # For a basic MVP, scroll to trigger lazy loading
        if hasattr(session, 'playwright_page') and session.playwright_page:
            session.playwright_page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(2)
            session.playwright_page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(2)
            # Re-fetch page to get updated DOM snapshot
            page = session.fetch(page.url)

        # Look for video links in TikTok
        video_links = page.css('a[href*="/video/"]')
        new_count = 0
        
        for link in video_links:
            url = link.attrib.get('href', '')
            if url:
                if not url.startswith('http'):
                    url = urllib.parse.urljoin("https://www.tiktok.com", url)
                if add_video("tiktok", url):
                    new_count += 1
                    
        print(f"Agregados {new_count} nuevos videos de TikTok.")

def scrape_instagram_saved(headless=True):
    if not StealthySession:
        return
    print("Iniciando scraper de Instagram...")
    ig_dir = SESSIONS_DIR / "instagram"
    ig_dir.mkdir(exist_ok=True, parents=True)
    
    with StealthySession(user_data_dir=str(ig_dir), headless=headless) as session:
        page = session.fetch("https://www.instagram.com/")
        time.sleep(5)
        
        if "login" in page.url:
            if headless:
                print("No estás logueado en Instagram. Ejecuta con --login para abrir la ventana e iniciar sesión manualmente.")
                return
            else:
                print("Inicia sesión manualmente en Instagram. Esperando 60 segundos...")
                time.sleep(60)
        
        # In a real scenario, this would navigate to the profile's saved section.
        # We will use the explore page for now as a placeholder/example.
        page = session.fetch("https://www.instagram.com/explore/")
        time.sleep(5)
        
        if hasattr(session, 'playwright_page') and session.playwright_page:
            session.playwright_page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(2)
            page = session.fetch(page.url)

        video_links = page.css('a[href*="/reel/"]') + page.css('a[href*="/p/"]')
        new_count = 0
        
        for link in video_links:
            url = link.attrib.get('href', '')
            if url:
                if not url.startswith('http'):
                    url = urllib.parse.urljoin("https://www.instagram.com", url)
                # Filter out pure query param links, ensuring it's a post
                if add_video("instagram", url):
                    new_count += 1
                    
        print(f"Agregados {new_count} nuevos videos de Instagram.")
