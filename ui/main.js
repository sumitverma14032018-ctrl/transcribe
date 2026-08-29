const urlInput = document.getElementById('url-input');
const pathInput = document.getElementById('path-input');
const transcribeBtn = document.getElementById('transcribe-btn');
const progressCard = document.getElementById('progress-card');
const statusText = document.getElementById('status-text');
const progressFill = document.getElementById('progress-fill');
const progressPercent = document.getElementById('progress-percent');
const logsCard = document.getElementById('logs-card');
const logContainer = document.getElementById('log-container');
const outputCard = document.getElementById('output-card');
const transcriptionText = document.getElementById('transcription-text');
const copyBtn = document.getElementById('copy-btn');

const modeUrlBtn = document.getElementById('mode-url');
const modePathBtn = document.getElementById('mode-path');

let currentMode = 'url'; // 'url' or 'path'

modeUrlBtn.addEventListener('click', () => {
    currentMode = 'url';
    modeUrlBtn.classList.add('active');
    modePathBtn.classList.remove('active');
    urlInput.classList.remove('hidden');
    pathInput.classList.add('hidden');
});

modePathBtn.addEventListener('click', () => {
    currentMode = 'path';
    modePathBtn.classList.add('active');
    modeUrlBtn.classList.remove('active');
    urlInput.classList.add('hidden');
    pathInput.classList.remove('hidden');
});

const API_BASE = ''; // Same origin

transcribeBtn.addEventListener('click', async () => {
    const value = currentMode === 'url' ? urlInput.value.trim() : pathInput.value.trim();
    if (!value) return;

    // Reset UI
    transcribeBtn.disabled = true;
    progressCard.classList.remove('hidden');
    logsCard.classList.remove('hidden');
    outputCard.classList.add('hidden');
    logContainer.innerHTML = '';
    updateProgress(0, 'Initializing...');

    try {
        const param = currentMode === 'url' ? `url=${encodeURIComponent(value)}` : `path=${encodeURIComponent(value)}`;
        const response = await fetch(`${API_BASE}/api/transcribe?${param}`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            transcribeBtn.disabled = false;
            return;
        }

        const { task_id } = data;

        // Connect to SSE
        const eventSource = new EventSource(`${API_BASE}/api/events/${task_id}`);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.status) {
                updateProgress(data.progress, data.status);
            }

            if (data.new_logs && data.new_logs.length > 0) {
                appendLogs(data.new_logs);
            }

            if (data.status === 'Completed') {
                eventSource.close();
                showOutput(data.result);
                transcribeBtn.disabled = false;
            } else if (data.status.startsWith('Error')) {
                eventSource.close();
                transcribeBtn.disabled = false;
                alert(data.status);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            transcribeBtn.disabled = false;
            updateProgress(0, 'Connection lost');
        };

    } catch (error) {
        console.error('Transcription error:', error);
        alert('Failed to start transcription');
        transcribeBtn.disabled = false;
    }
});

function appendLogs(logs) {
    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.textContent = log;
        logContainer.appendChild(div);
    });
    // Auto scroll to bottom
    logContainer.scrollTop = logContainer.scrollHeight;
}

function updateProgress(percent, status) {
    statusText.textContent = status;
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
}

function showOutput(text) {
    outputCard.classList.remove('hidden');
    transcriptionText.textContent = text;
    // Scroll to output
    outputCard.scrollIntoView({ behavior: 'smooth' });
}

copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(transcriptionText.textContent);
    const originalText = copyBtn.textContent;
    copyBtn.textContent = 'Copied!';
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
});
