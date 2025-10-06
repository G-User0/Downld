# 🌐 YouTube Downloader - Versión Web

Una aplicación web moderna para descargar videos y audio de YouTube. Perfecta para incluir en tu portafolio/CV.

## 📁 Estructura del Proyecto

```
youtube-downloader-web/
│
├── app.py                 # Backend Flask (API)
├── requirements.txt       # Dependencias Python
├── templates/
│   └── index.html        # Frontend (interfaz web)
└── README.md             # Este archivo
```

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install flask flask-cors yt-dlp
```

O usando `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Crear el Archivo `requirements.txt`

Crea un archivo llamado `requirements.txt` con el siguiente contenido:

```
flask>=2.3.0
flask-cors>=4.0.0
yt-dlp>=2023.1.1
```

### 3. Crear la Carpeta `templates`

```bash
mkdir templates
```

### 4. Guardar los Archivos

- **Backend:** Guarda el código Python como `app.py`
- **Frontend:** Guarda el código HTML dentro de `templates/index.html`

### 5. Instalar FFmpeg (Opcional pero Recomendado)

**Windows:**
```bash
# Descarga desde: https://www.gyan.dev/ffmpeg/builds/
# Agrega FFmpeg al PATH del sistema
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## ▶️ Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 🎯 Cómo Usar

1. **Abre tu navegador** y ve a `http://localhost:5000`
2. **Pega la URL** de YouTube en el campo
3. **Haz clic en "Obtener Info"** para ver los detalles del video
4. **Selecciona el formato** (Video o Audio) y la calidad
5. **Haz clic en "Descargar"** y espera a que termine
6. El archivo se descargará automáticamente a tu navegador

## 🌐 Desplegar en Internet (Para tu CV)

### Opción 1: Render.com (Gratis)

1. **Crea una cuenta** en [Render.com](https://render.com)

2. **Crea un archivo `render.yaml`:**

```yaml
services:
  - type: web
    name: youtube-downloader
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

3. **Actualiza `requirements.txt`:**

```
flask>=2.3.0
flask-cors>=4.0.0
yt-dlp>=2023.1.1
gunicorn>=21.0.0
```

4. **Modifica el final de `app.py`:**

```python
if __name__ == '__main__':
    clean_old_files()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

5. **Sube tu código a GitHub**

6. **Conecta Render con tu repositorio** y despliega

### Opción 2: Railway.app (Gratis)

1. **Crea cuenta** en [Railway.app](https://railway.app)
2. **Conecta tu repositorio** de GitHub
3. Railway detectará automáticamente que es Flask
4. **Despliega** con un clic

### Opción 3: PythonAnywhere (Gratis con limitaciones)

1. Crea cuenta en [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Sube tus archivos
3. Configura una aplicación Flask
4. Obtén tu URL gratuita

## 🎨 Características de la Versión Web

✅ **Interfaz moderna y responsiva** (funciona en móviles)  
✅ **Sin instalación** para los usuarios  
✅ **Limpieza automática** de archivos temporales  
✅ **Barra de progreso** en tiempo real  
✅ **Información completa** del video antes de descargar  
✅ **Múltiples formatos** (MP4, MP3, M4A, WAV)  
✅ **Múltiples calidades** (desde 144p hasta 4K)

## 🔧 Personalización

### Cambiar el Puerto

En `app.py`, línea final:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambia el puerto aquí
```

Y en `index.html`, cambia:

```javascript
const API_URL = 'http://localhost:8080';  // Actualiza el puerto
```

### Cambiar los Colores

En `index.html`, busca la sección `<style>` y modifica:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Cambia los colores del gradiente */
```

### Limitar Tamaño de Descargas

En `app.py`, agrega en `ydl_opts`:

```python
'max_filesize': 100 * 1024 * 1024,  # 100 MB máximo
```

## 📊 Para tu CV/Portafolio

### Qué Mencionar:

**Tecnologías Utilizadas:**
- Backend: Python, Flask, yt-dlp
- Frontend: HTML5, CSS3, JavaScript (Vanilla)
- API RESTful con Flask
- Manejo de concurrencia con threading
- Procesamiento de multimedia con FFmpeg

**Habilidades Demostradas:**
- Desarrollo Full Stack
- Diseño de APIs REST
- Programación asíncrona
- Manejo de archivos y streams
- UI/UX moderno y responsivo
- Integración con APIs externas

**Link del Proyecto:**
- GitHub: `github.com/tuusuario/youtube-downloader-web`
- Demo en vivo: `tu-app.onrender.com` (si lo despliegas)

## ⚠️ Consideraciones Importantes

### Legales
- Esta herramienta es **solo para uso educativo y personal**
- Respeta los derechos de autor
- No distribuyas contenido protegido sin permiso

### Técnicas
- Los archivos se eliminan automáticamente después de 1 hora
- El servidor debe tener FFmpeg para mejor compatibilidad
- Algunos videos pueden estar restringidos geográficamente

## 🐛 Solución de Problemas

### Error: "CORS policy"
Asegúrate de que Flask-CORS está instalado:
```bash
pip install flask-cors
```

### Error: "Connection refused"
Verifica que el backend esté corriendo en el puerto correcto.

### El archivo no se descarga
- Verifica que FFmpeg esté instalado
- Revisa los logs del servidor
- Algunos videos pueden tener restricciones

### La descarga es lenta
- Normal para videos en alta resolución
- Depende de tu conexión a Internet
- YouTube puede limitar la velocidad

## 📝 Mejoras Futuras

- [ ] Soporte para playlists
- [ ] Historial de descargas
- [ ] Interfaz de administración
- [ ] Subtítulos automáticos
- [ ] Cola de descargas múltiples
- [ ] Integración con servicios en la nube

## 🤝 Contribuir

Si quieres mejorar este proyecto:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Agrega mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📜 Licencia

MIT License - Libre para usar en tu portafolio

## 🙏 Créditos

- **yt-dlp** - Motor de descarga
- **Flask** - Framework web
- **FFmpeg** - Procesamiento multimedia

---

**¡Perfecto para tu CV! Demuestra habilidades en Python, Web Development y APIs RESTful** 🚀