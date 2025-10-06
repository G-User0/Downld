"""
YouTube Downloader - Aplicación Web con Flask
Backend API para descargar videos y audio de YouTube
Versión optimizada para producción
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import re
import tempfile
import threading
import time
import logging
from pathlib import Path
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Intentar importar yt-dlp
try:
    import yt_dlp
    logger.info(f"yt-dlp version {yt_dlp.version.__version__} cargado correctamente")
except ImportError:
    logger.error("yt-dlp no está instalado. Instala con: pip install yt-dlp")
    exit(1)

# Inicializar Flask
app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max para requests
app.config['JSON_SORT_KEYS'] = False

# Variables de entorno con valores por defecto
DEBUG_MODE = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')
TEMP_DOWNLOAD_FOLDER = os.environ.get('TEMP_FOLDER', tempfile.gettempdir())
MAX_FILE_AGE = int(os.environ.get('MAX_FILE_AGE', 3600))  # 1 hora por defecto
# Ruta al archivo de cookies
COOKIES_FILE = Path('cookies.txt')
cookies_env = os.environ.get('COOKIES_DATA')

if cookies_env and not COOKIES_FILE.exists():
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        f.write(cookies_env)
    logger.info("Archivo de cookies generado desde variable de entorno")

USE_COOKIES=True

logger.info(f"Usando cookies: {os.path.exists(COOKIES_FILE)}")



# Configurar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # En producción, especifica tu dominio
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Almacenar progreso de descargas
download_progress = {}

def clean_old_files():
    """Limpia archivos antiguos del directorio temporal"""
    try:
        current_time = time.time()
        deleted_count = 0
        
        for file in Path(TEMP_DOWNLOAD_FOLDER).glob("yt_download_*"):
            try:
                if current_time - file.stat().st_mtime > MAX_FILE_AGE:
                    file.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"No se pudo eliminar {file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Limpieza completada: {deleted_count} archivos eliminados")
            
    except Exception as e:
        logger.error(f"Error en limpieza de archivos: {e}")

def clean_youtube_url(url):
    """Limpia la URL de YouTube, extrayendo solo el ID del video"""
    try:
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                clean_url = f"https://www.youtube.com/watch?v={video_id}"
                logger.debug(f"URL limpiada: {url} -> {clean_url}")
                return clean_url
        
        logger.warning(f"No se pudo limpiar URL: {url}")
        return url
    except Exception as e:
        logger.error(f"Error limpiando URL: {e}")
        return url

def is_valid_youtube_url(url):
    """Valida si la URL es de YouTube"""
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
        r'(https?://)?(m\.)?youtube\.com/',
    ]
    return any(re.search(pattern, url) for pattern in youtube_patterns)

def check_ffmpeg():
    """Verificar si FFmpeg está disponible"""
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True, 
                      timeout=5)
        return True
    except Exception as e:
        logger.warning(f"FFmpeg no disponible: {e}")
        return False

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint de health check para servicios de hosting"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Obtiene información del video"""
    try:
        data = request.get_json()
        if not data:
            logger.warning("Request sin datos JSON")
            return jsonify({'error': 'Request inválido'}), 400
        
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400
        
        if not is_valid_youtube_url(url):
            logger.info(f"URL inválida recibida: {url}")
            return jsonify({'error': 'URL de YouTube no válida'}), 400
        
        clean_url = clean_youtube_url(url)
        logger.info(f"Obteniendo información para: {clean_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
        
        # Extraer formatos de video disponibles
        video_formats = []
        seen_heights = set()
        
        for fmt in info.get('formats', []):
            if fmt.get('vcodec') != 'none' and fmt.get('height'):
                height = fmt.get('height')
                if height not in seen_heights and height >= 144:
                    seen_heights.add(height)
                    video_formats.append(f"{height}p")
        
        video_formats.sort(key=lambda x: int(x[:-1]), reverse=True)
        
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
        
        response_data = {
            'title': info.get('title', 'N/A'),
            'uploader': info.get('uploader', 'N/A'),
            'duration': duration_str,
            'view_count': info.get('view_count', 0),
            'thumbnail': info.get('thumbnail', ''),
            'video_formats': ['Mejor calidad'] + video_formats,
            'clean_url': clean_url
        }
        
        logger.info(f"Información obtenida exitosamente: {response_data['title']}")
        return jsonify(response_data)
    
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Error de yt-dlp: {e}")
        return jsonify({'error': 'No se pudo obtener la información del video. Verifica la URL.'}), 500
    except Exception as e:
        logger.error(f"Error inesperado en get_video_info: {e}", exc_info=True)
        return jsonify({'error': f'Error al obtener información: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    """Inicia la descarga del video"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request inválido'}), 400
        
        url = data.get('url', '').strip()
        format_type = data.get('format_type', 'video')
        quality = data.get('quality', 'Mejor calidad')
        
        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400
        
        clean_url = clean_youtube_url(url)
        
        # Generar ID único para esta descarga
        download_id = f"download_{int(time.time() * 1000)}"
        download_progress[download_id] = {
            'status': 'starting',
            'progress': 0,
            'filename': None
        }
        
        logger.info(f"Iniciando descarga {download_id}: {clean_url} - {format_type} - {quality}")
        
        # Iniciar descarga en hilo separado
        thread = threading.Thread(
            target=download_worker,
            args=(download_id, clean_url, format_type, quality),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id
        })
    
    except Exception as e:
        logger.error(f"Error al iniciar descarga: {e}", exc_info=True)
        return jsonify({'error': f'Error al iniciar descarga: {str(e)}'}), 500

def download_worker(download_id, url, format_type, quality):
    """Worker que realiza la descarga"""
    try:
        has_ffmpeg = check_ffmpeg()
        output_template = os.path.join(TEMP_DOWNLOAD_FOLDER, f'yt_download_{download_id}_%(title)s.%(ext)s')
        
        def progress_hook(d):
            try:
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    elif 'total_bytes_estimate' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    else:
                        percent = 0
                    
                    download_progress[download_id] = {
                        'status': 'downloading',
                        'progress': round(percent, 1),
                        'filename': None
                    }
                elif d['status'] == 'finished':
                    download_progress[download_id] = {
                        'status': 'processing',
                        'progress': 100,
                        'filename': d.get('filename')
                    }
            except Exception as e:
                logger.error(f"Error en progress_hook: {e}")
        
        ydl_opts = {
            'outtmpl': output_template,
            'progress_hooks': [progress_hook],
            'no_warnings': False,
            'ignoreerrors': False,
            'socket_timeout': 30,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        }
        
        # Configurar opciones según formato
        if format_type == 'audio':
            if quality == 'mp3':
                ydl_opts['format'] = 'bestaudio'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif quality == 'm4a':
                ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'
            elif quality == 'wav':
                ydl_opts['format'] = 'bestaudio'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }]
            else:
                ydl_opts['format'] = 'bestaudio'
        else:  # video
            if has_ffmpeg:
                if quality == 'Mejor calidad':
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
                elif quality.endswith('p'):
                    height = quality[:-1]
                    ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}]'
                
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                if quality == 'Mejor calidad':
                    ydl_opts['format'] = 'best[ext=mp4]/best'
                elif quality.endswith('p'):
                    height = quality[:-1]
                    ydl_opts['format'] = f'best[height<={height}][ext=mp4]/best[height<={height}]'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Buscar el archivo descargado
            filename = ydl.prepare_filename(info)
            
            # Si se convirtió a mp3, actualizar extensión
            if format_type == 'audio' and quality == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            elif format_type == 'audio' and quality == 'wav':
                filename = filename.rsplit('.', 1)[0] + '.wav'
            
            download_progress[download_id] = {
                'status': 'completed',
                'progress': 100,
                'filename': os.path.basename(filename),
                'filepath': filename
            }
            
            logger.info(f"Descarga {download_id} completada: {os.path.basename(filename)}")
    
    except Exception as e:
        logger.error(f"Error en descarga {download_id}: {e}", exc_info=True)
        download_progress[download_id] = {
            'status': 'error',
            'progress': 0,
            'error': str(e)
        }

@app.route('/api/progress/<download_id>')
def get_progress(download_id):
    """Obtiene el progreso de una descarga"""
    progress = download_progress.get(download_id, {'status': 'not_found'})
    return jsonify(progress)

@app.route('/api/download-file/<download_id>')
def download_file(download_id):
    """Descarga el archivo completado"""
    try:
        progress = download_progress.get(download_id)
        
        if not progress or progress['status'] != 'completed':
            logger.warning(f"Intento de descarga de archivo no completado: {download_id}")
            return jsonify({'error': 'Descarga no completada'}), 404
        
        filepath = progress.get('filepath')
        if not filepath or not os.path.exists(filepath):
            logger.error(f"Archivo no encontrado: {filepath}")
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        logger.info(f"Enviando archivo: {progress['filename']}")
        return send_file(
            filepath,
            as_attachment=True,
            download_name=progress['filename']
        )
    
    except Exception as e:
        logger.error(f"Error al enviar archivo: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-info')
def system_info():
    """Información del sistema"""
    return jsonify({
        'ffmpeg_available': check_ffmpeg(),
        'yt_dlp_version': yt_dlp.version.__version__,
        'debug_mode': DEBUG_MODE,
        'max_file_age': MAX_FILE_AGE
    })

@app.errorhandler(404)
def not_found(error):
    """Manejo de error 404"""
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de error 500"""
    logger.error(f"Error 500: {error}")
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Crear directorio de descargas si no existe
    os.makedirs(TEMP_DOWNLOAD_FOLDER, exist_ok=True)

    # Limpiar archivos antiguos al iniciar
    logger.info("Iniciando limpieza de archivos antiguos...")
    clean_old_files()

    # Forzar uso del puerto de Render si existe
    port = int(os.environ.get('PORT', PORT))

    logger.info("=" * 60)
    logger.info("YouTube Downloader - Servidor Iniciado")
    logger.info("=" * 60)
    logger.info(f" Host: {HOST}")
    logger.info(f" Puerto: {port}")
    logger.info(f" Debug: {DEBUG_MODE}")
    logger.info(f" Carpeta temporal: {TEMP_DOWNLOAD_FOLDER}")
    logger.info(f" Tiempo máximo de archivos: {MAX_FILE_AGE}s")
    logger.info(f" FFmpeg: {'Disponible' if check_ffmpeg() else 'No disponible'}")
    logger.info("=" * 60)
    logger.info(f" Abre tu navegador en: http://localhost:{port}")
    logger.info("=" * 60)

    app.run(debug=DEBUG_MODE, host=HOST, port=port)
