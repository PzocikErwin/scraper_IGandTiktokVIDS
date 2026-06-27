import time
import urllib.parse
from pathlib import Path
from config import SESSIONS_DIR
from database import add_video

try:
    from scrapling.fetchers import StealthySession
    from playwright.sync_api import Page
except ImportError:
    print("WARNING: scrapling could not be imported. Ensure dependencies are installed via a standard Windows Python distribution.")
    StealthySession = None

def tiktok_action(page: Page):
    print("[TikTok] Iniciando acciones en el navegador...")
    page.wait_for_timeout(5000) # esperar carga
    
    # 1. Comprobar inicio de sesión
    if "login" in page.url or page.locator("text='Log in'").is_visible() or page.locator("text='Iniciar sesión'").is_visible():
        print("[TikTok] No se detectó sesión iniciada. Por favor, loguéate en la ventana del navegador.")
        # Esperar a que el usuario se loguee y sea redireccionado a una página que no sea login
        for i in range(12): # Esperar hasta 2 minutos
            page.wait_for_timeout(10000)
            if "login" not in page.url and not page.locator("text='Log in'").is_visible():
                print("[TikTok] ¡Sesión iniciada correctamente!")
                break
        else:
            print("[TikTok] Tiempo de espera agotado para iniciar sesión.")
            return

    # 2. Navegar a la pestaña 'Me gusta'
    print("[TikTok] Buscando pestaña 'Me gusta' o 'Liked'...")
    liked_tab = None
    selectors = [
        '[data-e2e="liked-tab"]',
        'text="Me gusta"',
        'text="Liked"',
        'a[href*="/liked"]',
        'div[data-e2e="liked-tab"]'
    ]
    
    # Buscar el elemento visible que contenga los selectores
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.first.is_visible():
                liked_tab = loc.first
                break
        except Exception:
            continue
            
    if liked_tab:
        print("[TikTok] Pestaña de likes encontrada. Haciendo click...")
        liked_tab.click()
        page.wait_for_timeout(3000)
    else:
        print("[TikTok] No se pudo encontrar la pestaña de 'Me gusta' automáticamente.")
        print("[TikTok] Guardando captura en 'tiktok_debug.png' para verificar la estructura...")
        page.screenshot(path="tiktok_debug.png")
        
    # 3. Hacer scroll para cargar videos
    print("[TikTok] Desplazando página (scroll) para cargar videos favoritos...")
    for i in range(8):
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(1500)
    
    print("[TikTok] Acciones del navegador completadas.")

def instagram_action(page: Page):
    print("[Instagram] Iniciando acciones en el navegador...")
    page.wait_for_timeout(5000) # esperar carga
    
    # 1. Comprobar inicio de sesión
    if "login" in page.url:
        print("[Instagram] No se detectó sesión iniciada. Por favor, loguéate en la ventana del navegador.")
        for i in range(12):
            page.wait_for_timeout(10000)
            if "login" not in page.url:
                print("[Instagram] ¡Sesión iniciada correctamente!")
                break
        else:
            print("[Instagram] Tiempo de espera agotado para iniciar sesión.")
            return

    # 2. Intentar ir a la sección de guardados ('saved') directamente
    # En Instagram, al estar logueado, podemos intentar deducir el perfil
    # O navegar a la página de inicio para buscar el enlace de perfil
    print("[Instagram] Buscando la sección de guardados...")
    
    # Intentamos buscar el enlace del perfil en la barra lateral
    profile_link = page.locator('a[href*="/profile/"], a[href^="/"][href$="/"]').filter(has_not=page.locator('span')).first
    
    # Alternativamente, podemos hacer click en el menú lateral de 'Guardado' si existe
    saved_btn = page.locator('text="Guardado"').or_(page.locator('text="Saved"')).first
    
    if saved_btn.is_visible():
        print("[Instagram] Botón 'Guardado' encontrado en barra lateral. Haciendo click...")
        saved_btn.click()
        page.wait_for_timeout(5000)
    else:
        # Ir a la página del perfil primero
        print("[Instagram] Navegando al perfil...")
        page.goto("https://www.instagram.com/profile") # redirecciona al perfil propio
        page.wait_for_timeout(5000)
        
        # Una vez en el perfil, buscar la pestaña de Guardados
        saved_tab = page.locator('a[href*="/saved/"]').first
        if saved_tab.is_visible():
            print("[Instagram] Pestaña de guardados encontrada en el perfil. Haciendo click...")
            saved_tab.click()
            page.wait_for_timeout(5000)
        else:
            print("[Instagram] No se encontró el botón de Guardados de forma automática.")
            print("[Instagram] Guardando captura en 'instagram_debug.png'...")
            page.screenshot(path="instagram_debug.png")
            
    # 3. Hacer scroll para cargar reels/publicaciones guardadas
    print("[Instagram] Desplazando página (scroll) para cargar videos guardados...")
    for i in range(8):
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(1500)
        
    print("[Instagram] Acciones del navegador completadas.")

def scrape_tiktok_likes(headless=True):
    if not StealthySession:
        return
    print("Iniciando scraper de TikTok...")
    tiktok_dir = SESSIONS_DIR / "tiktok"
    tiktok_dir.mkdir(exist_ok=True, parents=True)
    
    with StealthySession(user_data_dir=str(tiktok_dir), headless=headless) as session:
        # Se pasa tiktok_action para ejecutar en el navegador real
        response = session.fetch("https://www.tiktok.com/@me", page_action=tiktok_action)
        
        # Buscar enlaces de videos en la respuesta final
        video_links = response.css('a[href*="/video/"]')
        new_count = 0
        
        for link in video_links:
            url = link.attrib.get('href', '')
            if url:
                if not url.startswith('http'):
                    url = urllib.parse.urljoin("https://www.tiktok.com", url)
                url = url.split('?')[0] # Limpiar parámetros UTM
                if add_video("tiktok", url):
                    new_count += 1
                    
        print(f"Sincronización de TikTok completada. Agregados {new_count} nuevos videos.")

def scrape_instagram_saved(headless=True):
    if not StealthySession:
        return
    print("Iniciando scraper de Instagram...")
    ig_dir = SESSIONS_DIR / "instagram"
    ig_dir.mkdir(exist_ok=True, parents=True)
    
    with StealthySession(user_data_dir=str(ig_dir), headless=headless) as session:
        response = session.fetch("https://www.instagram.com/", page_action=instagram_action)
        
        # En instagram las publicaciones guardadas tienen URLs del tipo /reel/ o /p/
        video_links = response.css('a[href*="/reel/"]') + response.css('a[href*="/p/"]')
        new_count = 0
        
        for link in video_links:
            url = link.attrib.get('href', '')
            if url:
                if not url.startswith('http'):
                    url = urllib.parse.urljoin("https://www.instagram.com", url)
                url = url.split('?')[0] # Limpiar parámetros
                if add_video("instagram", url):
                    new_count += 1
                    
        print(f"Sincronización de Instagram completada. Agregados {new_count} nuevos videos.")
