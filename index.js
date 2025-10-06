const API_URL = 'http://localhost:5000';
let currentVideoData = null;
let currentDownloadId = null;

// Elementos del DOM
const urlInput = document.getElementById('urlInput');
const getInfoBtn = document.getElementById('getInfoBtn');
const videoInfo = document.getElementById('videoInfo');
const thumbnail = document.getElementById('thumbnail');
const formatSelect = document.getElementById('formatSelect');
const qualitySelect = document.getElementById('qualitySelect');
const downloadBtn = document.getElementById('downloadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const statusMessage = document.getElementById('statusMessage');

// Obtener información del video
getInfoBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) {
        showStatus('Por favor ingresa una URL', 'error');
        return;
    }
    setLoading(getInfoBtn, true);
    hideStatus();
    try {
        const response = await fetch(`${API_URL}/api/video-info`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Error al obtener información');
        }
        currentVideoData = data;
        displayVideoInfo(data);
        downloadBtn.disabled = false;
        showStatus('✓ Información obtenida correctamente', 'success');
    } catch (error) {
        showStatus(error.message, 'error');
    } finally {
        setLoading(getInfoBtn, false);
    }
});

// Mostrar información del video
function displayVideoInfo(data) {
    document.getElementById('videoTitle').textContent = data.title;
    document.getElementById('videoUploader').textContent = data.uploader;
    document.getElementById('videoDuration').textContent = data.duration;
    document.getElementById('videoViews').textContent = data.view_count.toLocaleString();
    if (data.thumbnail) {
        thumbnail.src = data.thumbnail;
        thumbnail.classList.add('show');
    }
    videoInfo.classList.add('show');
    // Actualizar opciones de calidad
    updateQualityOptions(data.video_formats);
}

// Actualizar opciones de calidad
function updateQualityOptions(formats = []) {
    const isVideo = formatSelect.value === 'video';
    qualitySelect.innerHTML = '';
    if (isVideo) {
        formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format;
            option.textContent = format;
            qualitySelect.appendChild(option);
        });
    } else {
        ['Mejor calidad', 'mp3', 'm4a', 'wav'].forEach(format => {
            const option = document.createElement('option');
            option.value = format;
            option.textContent = format.toUpperCase();
            qualitySelect.appendChild(option);
        });
    }
}

// Cambio de formato
formatSelect.addEventListener('change', () => {
    if (currentVideoData) {
        updateQualityOptions(currentVideoData.video_formats);
    }
});

// Iniciar descarga
downloadBtn.addEventListener('click', async () => {
    if (!currentVideoData) return;
    setLoading(downloadBtn, true);
    downloadBtn.disabled = true;
    hideStatus();
    progressContainer.classList.add('show');
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    try {
        const response = await fetch(`${API_URL}/api/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: currentVideoData.clean_url,
                format_type: formatSelect.value,
                quality: qualitySelect.value
            })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Error al iniciar descarga');
        }
        currentDownloadId = data.download_id;
        monitorProgress(data.download_id);
    } catch (error) {
        showStatus(error.message, 'error');
        setLoading(downloadBtn, false);
        downloadBtn.disabled = false;
    }
});

// Monitorear progreso
async function monitorProgress(downloadId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_URL}/api/progress/${downloadId}`);
            const data = await response.json();
            if (data.status === 'downloading' || data.status === 'processing') {
                progressBar.style.width = data.progress + '%';
                progressText.textContent = data.progress + '%';
            } else if (data.status === 'completed') {
                clearInterval(interval);
                progressBar.style.width = '100%';
                progressText.textContent = '100%';
                showStatus('✓ ¡Descarga completada!', 'success');
                
                // Descargar archivo
                window.location.href = `${API_URL}/api/download-file/${downloadId}`;
                
                setLoading(downloadBtn, false);
                downloadBtn.disabled = false;
            } else if (data.status === 'error') {
                clearInterval(interval);
                showStatus('Error: ' + data.error, 'error');
                setLoading(downloadBtn, false);
                downloadBtn.disabled = false;
            }
        } catch (error) {
            clearInterval(interval);
            showStatus('Error al monitorear descarga', 'error');
            setLoading(downloadBtn, false);
            downloadBtn.disabled = false;
        }
    }, 500);
}

// Funciones auxiliares
function setLoading(button, isLoading) {
    const text = button.querySelector('[id$="Text"]');
    const loader = button.querySelector('[id$="Loader"]');
    
    if (isLoading) {
        text.style.display = 'none';
        loader.style.display = 'inline-block';
    } else {
        text.style.display = 'inline';
        loader.style.display = 'none';
    }
}

function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message show status-${type}`;
}

function hideStatus() {
    statusMessage.classList.remove('show');
}

// Enter key support
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        getInfoBtn.click();
    }
});