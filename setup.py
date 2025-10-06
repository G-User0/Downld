"""
Script de configuración automática para YouTube Downloader Web
Ejecuta este archivo para configurar todo automáticamente
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Muestra el banner de inicio"""
    print("=" * 60)
    print("🎥 YouTube Downloader - Configuración Automática")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("📌 Verificando versión de Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} detectado")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor} no es compatible")
        print("   Se requiere Python 3.7 o superior")
        return False

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("\n📦 Instalando dependencias...")
    
    dependencies = [
        'flask>=2.3.0',
        'flask-cors>=4.0.0',
        'yt-dlp>=2023.1.1'
    ]
    
    try:
        for dep in dependencies:
            print(f"   Instalando {dep}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep, "-q"
            ])
        print("   ✓ Todas las dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Error al instalar dependencias: {e}")
        return False

def check_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    print("\n🎬 Verificando FFmpeg...")
    
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True, 
                      timeout=5)
        print("   ✓ FFmpeg está instalado")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("   ⚠ FFmpeg no está instalado")
        print("   La aplicación funcionará, pero con compatibilidad limitada")
        print_ffmpeg_instructions()
        return False

def print_ffmpeg_instructions():
    """Muestra instrucciones para instalar FFmpeg"""
    system = platform.system()
    
    print("\n   📝 Instrucciones para instalar FFmpeg:")
    
    if system == "Windows":
        print("   1. Visita: https://www.gyan.dev/ffmpeg/builds/")
        print("   2. Descarga 'ffmpeg-release-essentials.zip'")
        print("   3. Extrae y agrega la carpeta 'bin' al PATH")
    elif system == "Linux":
        print("   Ejecuta: sudo apt update && sudo apt install ffmpeg")
    elif system == "Darwin":  # macOS
        print("   Ejecuta: brew install ffmpeg")
    
    print()

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    print("\n📁 Creando estructura de directorios...")
    
    try:
        os.makedirs('templates', exist_ok=True)
        print("   ✓ Carpeta 'templates' creada")
        return True
    except Exception as e:
        print(f"   ✗ Error al crear directorios: {e}")
        return False

def create_requirements_file():
    """Crea el archivo requirements.txt"""
    print("\n📄 Creando requirements.txt...")
    
    requirements_content = """flask>=2.3.0
flask-cors>=4.0.0
yt-dlp>=2023.1.1
"""
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(requirements_content)
        print("   ✓ requirements.txt creado")
        return True
    except Exception as e:
        print(f"   ✗ Error al crear requirements.txt: {e}")
        return False

def check_files():
    """Verifica que los archivos necesarios existan"""
    print("\n🔍 Verificando archivos...")
    
    files_status = {
        'app.py': os.path.exists('app.py'),
        'templates/index.html': os.path.exists('templates/index.html')
    }
    
    all_exist = True
    for file, exists in files_status.items():
        if exists:
            print(f"   ✓ {file} encontrado")
        else:
            print(f"   ✗ {file} no encontrado")
            all_exist = False
    
    if not all_exist:
        print("\n   ⚠ Faltan archivos necesarios. Asegúrate de tener:")
        print("   - app.py (backend)")
        print("   - templates/index.html (frontend)")
    
    return all_exist

def print_next_steps():
    """Muestra los siguientes pasos"""
    print("\n" + "=" * 60)
    print("✅ ¡Configuración completada!")
    print("=" * 60)
    print("\n📝 Siguientes pasos:")
    print("\n1. Asegúrate de tener los archivos:")
    print("   - app.py")
    print("   - templates/index.html")
    print("\n2. Inicia la aplicación:")
    print("   python app.py")
    print("\n3. Abre tu navegador en:")
    print("   http://localhost:5000")
    print("\n4. ¡Disfruta descargando videos!")
    print("\n" + "=" * 60)
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear estructura
    if not create_directory_structure():
        print("\n⚠ Advertencia: No se pudo crear la estructura de directorios")
    
    # Crear requirements.txt
    create_requirements_file()
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Error fatal: No se pudieron instalar las dependencias")
        sys.exit(1)
    
    # Verificar FFmpeg
    check_ffmpeg()
    
    # Verificar archivos
    files_ok = check_files()
    
    # Mostrar siguientes pasos
    print_next_steps()
    
    if not files_ok:
        print("⚠ NOTA: Faltan algunos archivos del proyecto")
        print("Por favor, copia app.py y templates/index.html antes de continuar")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Configuración cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)