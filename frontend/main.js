const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingSection = document.getElementById('loadingSection');
const resetBtn = document.getElementById('resetBtn');

let selectedFile = null;

uploadBox.addEventListener('click', () => fileInput.click());

uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
        alert('Only PDF and DOCX files are allowed');
        return;
    }
    
    selectedFile = file;
    uploadBox.innerHTML = `<p><strong>${file.name}</strong> selected</p>`;
    uploadBtn.disabled = false;
}

uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    loadingSection.style.display = 'flex';
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        alert('Error: ' + error.message);
        loadingSection.style.display = 'none';
    }
});

function displayResults(data) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    const docData = data.data;
    const analysis = docData.analysis_data;
    
    document.getElementById('filename').textContent = docData.filename;
    document.getElementById('fileType').textContent = docData.file_type.toUpperCase();
    document.getElementById('wordCount').textContent = docData.word_count;
    document.getElementById('pageCount').textContent = docData.page_count || 'N/A';
    
    document.getElementById('uniqueWords').textContent = analysis.unique_words;
    document.getElementById('sentenceCount').textContent = analysis.sentence_count;
    document.getElementById('avgWordLength').textContent = analysis.average_word_length;
    
    const preview = docData.content.substring(0, 500) + (docData.content.length > 500 ? '...' : '');
    document.getElementById('previewBox').textContent = preview;
}

resetBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    uploadBox.innerHTML = `
        <svg class="upload-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <p>Drag and drop your file here or click to browse</p>
    `;
    uploadBtn.disabled = true;
    resultsSection.style.display = 'none';
});
