const { ipcRenderer } = require('electron');
const axios = require('axios');

// UI Elements
const hardwareInfo = document.getElementById('hardwareInfo');
const openFileBtn = document.getElementById('openFileBtn');
const openYoutubeBtn = document.getElementById('openYoutubeBtn');
const youtubeUrl = document.getElementById('youtubeUrl');
const selectedFile = document.getElementById('selectedFile');
const enableModelSelection = document.getElementById('enableModelSelection');
const modelSelectionSection = document.getElementById('modelSelectionSection');
const modelSelect = document.getElementById('modelSelect');
const processBtn = document.getElementById('processBtn');
const openOutputBtn = document.getElementById('openOutputBtn');
const statusSection = document.getElementById('statusSection');

let filePath = null;
let stems = ['vocals'];

// Hardware info
async function showHardwareInfo() {
  const info = await ipcRenderer.invoke('get-hardware-info');
  hardwareInfo.innerText = `CPU: ${info.cpu} (${info.cores} cores), RAM: ${info.ram}GB, GPU: ${info.gpu}`;
}
showHardwareInfo();

// Model selection toggle
enableModelSelection.addEventListener('change', () => {
  modelSelectionSection.style.display = enableModelSelection.checked ? 'block' : 'none';
});

// File open dialog
openFileBtn.addEventListener('click', async () => {
  const result = await ipcRenderer.invoke('show-open-dialog', {
    properties: ['openFile'],
    filters: [
      { name: 'Audio', extensions: ['mp3', 'wav', 'flac', 'm4a', 'aac'] }
    ]
  });
  if (!result.canceled && result.filePaths.length > 0) {
    filePath = result.filePaths[0];
    selectedFile.innerText = filePath;
  }
});

// YouTube input
openYoutubeBtn.addEventListener('click', () => {
  youtubeUrl.style.display = youtubeUrl.style.display === 'none' ? 'inline-block' : 'none';
});

document.querySelectorAll('.stems-section input[type="checkbox"]').forEach(cb => {
  cb.addEventListener('change', () => {
    stems = Array.from(document.querySelectorAll('.stems-section input[type="checkbox"]:checked')).map(cb => cb.value);
  });
});

// Process button
processBtn.addEventListener('click', async () => {
  statusSection.innerText = 'Processing...';
  let model = 'mdx_extra_q';
  if (enableModelSelection.checked) model = modelSelect.value;

  let apiUrl = '';
  let formData = new FormData();
  if (filePath) {
    apiUrl = 'http://localhost:7860/api/separate';
    formData.append('file', require('fs').createReadStream(filePath));
    formData.append('stems', stems.join(','));
    formData.append('model', model);
  } else if (youtubeUrl.value) {
    apiUrl = 'http://localhost:7860/api/separate-youtube';
    formData.append('url', youtubeUrl.value);
    formData.append('stems', stems.join(','));
    formData.append('model', model);
  } else {
    statusSection.innerText = 'Please select a file or enter a YouTube URL.';
    return;
  }

  try {
    // Use axios for multipart/form-data
    const response = await axios.post(apiUrl, formData, {
      headers: formData.getHeaders ? formData.getHeaders() : {},
      responseType: 'json',
    });
    if (response.data && response.data.files) {
      // Ask user where to save each file
      for (const [stem, fileInfo] of Object.entries(response.data.files)) {
        const saveResult = await ipcRenderer.invoke('show-save-dialog', {
          title: `Save ${fileInfo.name}`,
          defaultPath: fileInfo.filename,
        });
        if (!saveResult.canceled && saveResult.filePath) {
          // Download from backend and save
          const fileResp = await axios.get('http://localhost:7860/' + fileInfo.url, { responseType: 'arraybuffer' });
          require('fs').writeFileSync(saveResult.filePath, Buffer.from(fileResp.data));
        }
      }
      statusSection.innerText = 'Done! Files saved.';
    } else {
      statusSection.innerText = 'Processing failed: ' + (response.data.detail || 'Unknown error');
    }
  } catch (err) {
    statusSection.innerText = 'Error: ' + (err.message || err);
  }
});

// Open output folder
openOutputBtn.addEventListener('click', () => {
  ipcRenderer.invoke('open-output-folder');
});
