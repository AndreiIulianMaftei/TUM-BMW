const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

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
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!validTypes.includes(file.type)) {
        alert('Please upload a PDF or Word document');
        return;
    }
    
    selectedFile = file;
    uploadBox.innerHTML = `
        <div class="upload-icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
        </div>
        <h3>Document Ready</h3>
        <p class="upload-hint"><strong>${file.name}</strong></p>
        <div class="file-types">
            <span class="file-badge">Ready to analyze</span>
        </div>
    `;
    uploadBtn.disabled = false;
}

uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'flex';
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        displayResults(data.analysis);
        
    } catch (error) {
        alert('Error: ' + error.message);
        resetUpload();
    }
});

function displayResults(analysis) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    document.getElementById('generatedText').textContent = analysis.value_market_potential_text || 'Generated text not available';
    
    const variablesContainer = document.getElementById('variablesContainer');
    variablesContainer.innerHTML = '';
    if (analysis.identified_variables && analysis.identified_variables.length > 0) {
        analysis.identified_variables.forEach(v => {
            const div = document.createElement('div');
            div.className = 'variable-item';
            div.innerHTML = `<strong>${v.name}:</strong> ${v.value}<br><small>${v.description}</small>`;
            variablesContainer.appendChild(div);
        });
    } else {
        variablesContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 14px;">No variables identified</p>';
    }
    
    const formulasContainer = document.getElementById('formulasContainer');
    formulasContainer.innerHTML = '';
    if (analysis.formulas && analysis.formulas.length > 0) {
        analysis.formulas.forEach(f => {
            const div = document.createElement('div');
            div.className = 'formula-item';
            div.innerHTML = `<strong>${f.name}:</strong> ${f.formula}<br><small>Result: ${f.calculation}</small>`;
            formulasContainer.appendChild(div);
        });
    } else {
        formulasContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 14px;">No formulas generated</p>';
    }
    
    document.getElementById('marketSizeValue').textContent = analysis.market_size || 'Not available';
    document.getElementById('revenuePotentialValue').textContent = analysis.revenue_potential || 'Not available';
    document.getElementById('addressableMarketValue').textContent = analysis.addressable_market || 'Not available';
    document.getElementById('targetMarketShareValue').textContent = analysis.target_market_share || 'Not available';
    document.getElementById('roiEstimateValue').textContent = analysis.roi_estimate || 'Not available';
    
    const assumptionsList = document.getElementById('assumptionsList');
    assumptionsList.innerHTML = '';
    if (analysis.business_assumptions && analysis.business_assumptions.length > 0) {
        analysis.business_assumptions.forEach(assumption => {
            const li = document.createElement('li');
            li.textContent = assumption;
            assumptionsList.appendChild(li);
        });
    } else {
        assumptionsList.innerHTML = '<li>No assumptions provided</li>';
    }
}

newAnalysisBtn.addEventListener('click', resetUpload);

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    uploadBox.innerHTML = `
        <div class="upload-icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
        </div>
        <h3>Drop your document here</h3>
        <p class="upload-hint">or click to browse files</p>
        <div class="file-types">
            <span class="file-badge">PDF</span>
            <span class="file-badge">DOCX</span>
        </div>
    `;
    uploadBtn.disabled = true;
    
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
}
