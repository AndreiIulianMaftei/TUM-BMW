const uploadBox = document.getElementById('uploadBox');
const textInputBox = document.getElementById('textInputBox');
const fileInput = document.getElementById('fileInput');
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');
const uploadBtn = document.getElementById('uploadBtn');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const geminiOption = document.getElementById('geminiOption');
const openaiOption = document.getElementById('openaiOption');

// Settings elements
const settingsBtn = document.getElementById('settingsBtn');
const settingsPanel = document.getElementById('settingsPanel');
const closeSettings = document.getElementById('closeSettings');
const temperatureSlider = document.getElementById('temperatureSlider');
const temperatureValue = document.getElementById('temperatureValue');
const depthSelect = document.getElementById('depthSelect');
const industrySelect = document.getElementById('industrySelect');
const confidenceSlider = document.getElementById('confidenceSlider');
const confidenceValue = document.getElementById('confidenceValue');
const resetSettings = document.getElementById('resetSettings');

// Chat elements
const chatToggle = document.getElementById('chatToggle');
const chatContainer = document.getElementById('chatContainer');
const closeChat = document.getElementById('closeChat');
const chatInput = document.getElementById('chatInput');
const sendChat = document.getElementById('sendChat');
const chatMessages = document.getElementById('chatMessages');

let selectedFile = null;
let selectedProvider = 'gemini'; // Default provider
let inputMode = 'file'; // 'file' or 'text'
let analysisContext = null;
let settings = loadSettings();

// LLM Provider Selection
geminiOption.classList.add('active'); // Set Gemini as default

geminiOption.addEventListener('click', () => {
    selectedProvider = 'gemini';
    geminiOption.classList.add('active');
    openaiOption.classList.remove('active');
});

openaiOption.addEventListener('click', () => {
    selectedProvider = 'openai';
    openaiOption.classList.add('active');
    geminiOption.classList.remove('active');
});

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
    formData.append('provider', selectedProvider);
    
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'flex';
    
    // Update loading message based on provider
    const loadingCard = document.querySelector('.loading-card h3');
    const providerName = selectedProvider === 'gemini' ? 'Google Gemini 2.5 Flash' : 'OpenAI o1';
    loadingCard.textContent = `Analyzing with ${providerName}`;
    
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
    
    document.getElementById('executiveSummary').textContent = analysis.executive_summary || 'No executive summary available';
    document.getElementById('generatedText').textContent = analysis.value_market_potential_text || 'Generated text not available';
    
    const formatCurrency = (value) => {
        if (!value && value !== 0) return 'N/A';
        return new Intl.NumberFormat('en-US', { 
            style: 'currency', 
            currency: 'EUR',
            notation: 'compact',
            maximumFractionDigits: 1
        }).format(value);
    };

    const formatNumber = (value) => {
        if (!value && value !== 0) return 'N/A';
        return new Intl.NumberFormat('en-US', { 
            notation: 'compact',
            maximumFractionDigits: 1
        }).format(value);
    };

    const formatPercentage = (value) => {
        if (!value && value !== 0) return 'N/A';
        return `${value.toFixed(1)}%`;
    };

    const getConfidenceBadgeClass = (confidence) => {
        if (confidence >= 80) return 'confidence-high';
        if (confidence >= 60) return 'confidence-medium';
        return 'confidence-low';
    };

    if (analysis.tam) {
        document.getElementById('tamValue').textContent = formatCurrency(analysis.tam.market_size);
        document.getElementById('tamInsight').textContent = analysis.tam.insight || '';
        const tamBadge = document.getElementById('tamConfidence');
        tamBadge.textContent = `${analysis.tam.confidence}%`;
        tamBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.tam.confidence)}`;
    }

    if (analysis.sam) {
        document.getElementById('samValue').textContent = formatCurrency(analysis.sam.market_size);
        document.getElementById('samInsight').textContent = analysis.sam.insight || '';
        const samBadge = document.getElementById('samConfidence');
        samBadge.textContent = `${analysis.sam.confidence}%`;
        samBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.sam.confidence)}`;
    }

    if (analysis.som) {
        document.getElementById('somValue').textContent = formatCurrency(analysis.som.revenue_potential);
        document.getElementById('somInsight').textContent = analysis.som.insight || '';
        const somBadge = document.getElementById('somConfidence');
        somBadge.textContent = `${analysis.som.confidence}%`;
        somBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.som.confidence)}`;
    }

    if (analysis.roi) {
        document.getElementById('roiValue').textContent = formatPercentage(analysis.roi.roi_percentage);
        document.getElementById('roiInsight').textContent = analysis.roi.insight || '';
        const roiBadge = document.getElementById('roiConfidence');
        roiBadge.textContent = `${analysis.roi.confidence}%`;
        roiBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.roi.confidence)}`;
    }

    if (analysis.turnover) {
        document.getElementById('turnoverValue').textContent = formatCurrency(analysis.turnover.total_revenue);
        document.getElementById('turnoverInsight').textContent = analysis.turnover.insight || '';
        const turnoverBadge = document.getElementById('turnoverConfidence');
        turnoverBadge.textContent = `${analysis.turnover.confidence}%`;
        turnoverBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.turnover.confidence)}`;
    }

    if (analysis.volume) {
        document.getElementById('volumeValue').textContent = formatNumber(analysis.volume.units_sold);
        document.getElementById('volumeInsight').textContent = analysis.volume.insight || '';
        const volumeBadge = document.getElementById('volumeConfidence');
        volumeBadge.textContent = `${analysis.volume.confidence}%`;
        volumeBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.volume.confidence)}`;
    }

    if (analysis.unit_economics) {
        document.getElementById('unitEconomicsValue').textContent = formatCurrency(analysis.unit_economics.margin);
        document.getElementById('unitEconomicsInsight').textContent = analysis.unit_economics.insight || '';
        const ueBadge = document.getElementById('unitEconomicsConfidence');
        ueBadge.textContent = `${analysis.unit_economics.confidence}%`;
        ueBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.unit_economics.confidence)}`;
    }

    if (analysis.ebit) {
        document.getElementById('ebitValue').textContent = formatCurrency(analysis.ebit.ebit_margin);
        document.getElementById('ebitInsight').textContent = analysis.ebit.insight || '';
        const ebitBadge = document.getElementById('ebitConfidence');
        ebitBadge.textContent = `${analysis.ebit.confidence}%`;
        ebitBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.ebit.confidence)}`;
    }

    if (analysis.cogs) {
        document.getElementById('cogsValue').textContent = formatCurrency(analysis.cogs.total_cogs);
        document.getElementById('cogsInsight').textContent = analysis.cogs.insight || '';
        const cogsBadge = document.getElementById('cogsConfidence');
        cogsBadge.textContent = `${analysis.cogs.confidence}%`;
        cogsBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.cogs.confidence)}`;
    }

    if (analysis.market_potential) {
        document.getElementById('marketPotentialValue').textContent = formatNumber(analysis.market_potential.market_size || analysis.market_potential.penetration);
        document.getElementById('marketPotentialInsight').textContent = analysis.market_potential.insight || '';
        const mpBadge = document.getElementById('marketPotentialConfidence');
        mpBadge.textContent = `${analysis.market_potential.confidence}%`;
        mpBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.market_potential.confidence)}`;
    }
    
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

    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    if (analysis.improvement_recommendations && analysis.improvement_recommendations.length > 0) {
        analysis.improvement_recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.textContent = recommendation;
            recommendationsList.appendChild(li);
        });
    } else {
        recommendationsList.innerHTML = '<li>No recommendations available</li>';
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
