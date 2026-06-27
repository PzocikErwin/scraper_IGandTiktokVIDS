# Scraper, Transcriptor y Buscador de Videos (TikTok & Instagram)

Una potente herramienta de línea de comandos (CLI) diseñada para automatizar la extracción de videos favoritos y guardados de **TikTok** e **Instagram**. Descarga el audio, lo transcribe usando Inteligencia Artificial y permite realizar búsquedas semánticas sobre el contenido de todos los videos.

## Próximamente: Interfaz Gráfica (UI)
Actualmente esta herramienta funciona por línea de comandos. Sin embargo, se tiene planeado agregar una **interfaz visual interactiva** en el futuro para facilitar su uso a personas menos técnicas, evitando que tengan que interactuar directamente con código o consolas.

## ¿Cómo funciona?

El proyecto está dividido en varios módulos que trabajan en cadena:

1. **Extracción (Scraping):** 
   Se utiliza la librería [Scrapling](https://github.com/D4Vinci/Scrapling) (un framework adaptativo de web scraping) junto con su `StealthySession`. Esto permite evadir las estrictas protecciones anti-bots de Cloudflare, Instagram y TikTok, manteniendo un contexto de navegador de Patchright persistente donde solo es necesario iniciar sesión una vez de forma segura.
2. **Descarga de Audio:** 
   Se utiliza `yt-dlp` para descargar únicamente la pista de audio de los videos extraídos. Esto ahorra espacio de almacenamiento y agiliza el proceso.
3. **Transcripción:** 
   El audio es procesado localmente mediante el modelo **Whisper** de OpenAI (gratuito y privado) para convertir la voz en texto.
4. **Almacenamiento y Búsqueda Semántica:** 
   La transcripción se procesa a través de `sentence-transformers` para generar vectores matemáticos (Embeddings). Todo se guarda en una base de datos local SQLite (`videos.db`). El sistema busca por "significado" y contexto (similitud del coseno), no solo por coincidencias exactas de palabras.

## Instalación

### Requisitos Previos
1. **Python 3.9+** instalado nativamente en el sistema (Descargar desde [python.org](https://www.python.org/)).
2. **FFmpeg** instalado y agregado al PATH (Necesario para procesar el audio de Whisper y yt-dlp).
   - *Windows:* Se puede instalar usando la terminal con `winget install ffmpeg` o descargando los binarios desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).

### Pasos de Instalación
Clonar este repositorio y configurar el entorno virtual en una terminal de PowerShell o CMD:

```bash
git clone https://github.com/PzocikErwin/scraper_IGandTiktokVIDS.git
cd scraper_IGandTiktokVIDS
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Instalar el navegador oculto requerido por Scrapling/Patchright
python -m patchright install chromium
```

## Uso de la Herramienta

### 1. Iniciar Sesión (La primera vez)
Para que el bot pueda acceder a los videos privados o favoritos, es necesario iniciar sesión manualmente la primera vez. Ejecutar:
```bash
python main.py sync --login
```
Se abrirá una ventana de navegador. Iniciar sesión en TikTok y/o Instagram de forma normal. La sesión se guardará localmente en la carpeta `.sessions/` de manera persistente.

### 2. Sincronizar y Extraer Nuevos Videos
Cada vez que se desee descargar y transcribir nuevos videos favoritos, ejecutar el comando:
```bash
python main.py sync
```
El bot se ejecutará en segundo plano (de forma invisible "headless"), detectará qué videos son nuevos, descargará su audio, los transcribirá y los guardará en la base de datos.

### 3. Buscar Videos
Para encontrar un video específico, usar el comando de búsqueda con una descripción natural:
```bash
python main.py search "buenas practicas de clean architecture en react"
```
El script devolverá los enlaces directos a los videos originales, el fragmento de texto exacto donde mencionan el tema y el porcentaje de coincidencia semántica.

---
*Este proyecto fue construido priorizando la privacidad (la transcripción ocurre 100% localmente) y la resiliencia contra sistemas anti-bots modernos gracias a la integración de [Scrapling](https://github.com/D4Vinci/Scrapling).*
