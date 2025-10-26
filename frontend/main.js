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
const exportExcelBtn = document.getElementById('exportExcelBtn');
const geminiOption = document.getElementById('geminiOption');
const openaiOption = document.getElementById('openaiOption');

// Settings elements
const settingsBtn = document.getElementById('settingsBtn');
const settingsPanel = document.getElementById('settingsPanel');
const closeSettings = document.getElementById('closeSettings');
const temperatureSlider = document.getElementById('temperatureSlider');
const temperatureValue = document.getElementById('temperatureValue');
const industrySelect = document.getElementById('industrySelect');
const resetSettings = document.getElementById('resetSettings');

// Chat elements
const toggleChatBtn = document.getElementById('toggleChatBtn');
const chatSidebar = document.getElementById('chatSidebar');
const closeChatSidebar = document.getElementById('closeChatSidebar');
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');
const resultsMainContent = document.getElementById('resultsMainContent');

// Navigation elements
const dashboardNavItem = document.getElementById('dashboardNavItem');
const simulatorNavItem = document.getElementById('simulatorNavItem');

// Simulator Page elements
const simulatorPage = document.getElementById('simulatorPage');
const simulatorContent = document.getElementById('simulatorContent');
const simulatorEmptyState = document.getElementById('simulatorEmptyState');
const goToDashboardBtn = document.getElementById('goToDashboard');

// History elements
const historySidebar = document.getElementById('historySidebar');
const historyNavItem = document.getElementById('historyNavItem');
const closeHistorySidebar = document.getElementById('closeHistorySidebar');
const historySearchInput = document.getElementById('historySearch');
const historyList = document.getElementById('historyList');

// Modal elements
const metricModal = document.getElementById('metricModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const closeModal = document.getElementById('closeModal');

let selectedFile = null;
let selectedProvider = 'gemini'; // Default provider
let inputMode = 'file'; // 'file' or 'text'
let historyData = [];
let currentAnalysisId = null;
let analysisContext = null;
let settings = loadSettings();
let conversationHistory = []; // Chat conversation history

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
    if (inputMode === 'file' && !selectedFile) return;
    if (inputMode === 'text' && !textInput.value.trim()) return;
    
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'flex';
    
    const loadingCard = document.querySelector('.loading-card h3');
    loadingCard.textContent = 'Analyzing with Fast AI + Accurate Math';
    
    try {
        let response;
        
        if (inputMode === 'file') {
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('provider', selectedProvider);
            formData.append('settings_json', JSON.stringify(settings));
            
            response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
        } else {
            response = await fetch('/api/analyze-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: textInput.value,
                    provider: selectedProvider,
                    settings: settings
                })
            });
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        const data = await response.json();
        analysisContext = data.analysis; // Save for chat
        displayResults(data.analysis);
        
        // Reload history to show the new analysis
        loadHistory();
        
        // Chat is now ready (user can click "Chat with AI" button)
        
    } catch (error) {
        alert('Error: ' + error.message);
        resetUpload();
    }
});

function displayResults(analysis) {
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'block';
    resultsSection.dataset.hasResults = 'true'; // Mark that we have results
    
    // Clear conversation history for new analysis
    conversationHistory = [];
    console.log('🔄 Conversation history cleared for new analysis');
    
    document.getElementById('executiveSummary').textContent = analysis.executive_summary || 'No executive summary available';
    document.getElementById('generatedText').textContent = analysis.value_market_potential_text || 'Generated text not available';
    
    if (analysis.project_type) {
        const projectTypeHeader = document.getElementById('projectTypeHeader');
        const projectTypeBadge = document.getElementById('projectTypeBadge');
        
        if (projectTypeHeader && projectTypeBadge) {
            const typeDisplay = analysis.project_type.replace(/_/g, ' ');
            const typeClass = analysis.project_type.replace(/_/g, '-').toLowerCase();
            
            projectTypeBadge.textContent = typeDisplay;
            projectTypeBadge.className = `project-type-badge ${typeClass}`;
            projectTypeHeader.style.display = 'block';
        }
    }
    
    const formatCurrency = (value) => {
        if (!value && value !== 0) return 'N/A';
        // Use currency from settings
        const currency = settings.currency || 'EUR';
        return new Intl.NumberFormat('en-US', { 
            style: 'currency', 
            currency: currency,
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

    const shouldHideCard = (value, insight) => {
        if (value === null || value === undefined) return true;
        if (value === 0) return true;
        if (value === 'N/A') return true;
        if (insight && (
            insight.includes('no unit volume') || 
            insight.includes('Savings project') ||
            insight.includes('COGS per unit: €0.00')
        )) return true;
        return false;
    };

    const hideCardIfNeeded = (cardId, value, insight) => {
        const card = document.getElementById(cardId);
        if (card) {
            if (shouldHideCard(value, insight)) {
                card.style.display = 'none';
            } else {
                card.style.display = 'block';
            }
        }
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
        const volumeValue = analysis.volume.units_sold;
        const volumeInsight = analysis.volume.insight || '';
        document.getElementById('volumeValue').textContent = formatNumber(volumeValue);
        document.getElementById('volumeInsight').textContent = volumeInsight;
        const volumeBadge = document.getElementById('volumeConfidence');
        volumeBadge.textContent = `${analysis.volume.confidence}%`;
        volumeBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.volume.confidence)}`;
        hideCardIfNeeded('volumeCard', volumeValue, volumeInsight);
    }

    if (analysis.unit_economics) {
        const ueValue = analysis.unit_economics.margin;
        const ueInsight = analysis.unit_economics.insight || '';
        document.getElementById('unitEconomicsValue').textContent = formatCurrency(ueValue);
        document.getElementById('unitEconomicsInsight').textContent = ueInsight;
        const ueBadge = document.getElementById('unitEconomicsConfidence');
        ueBadge.textContent = `${analysis.unit_economics.confidence}%`;
        ueBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.unit_economics.confidence)}`;
        hideCardIfNeeded('unitEconomicsCard', ueValue, ueInsight);
    }

    if (analysis.ebit) {
        document.getElementById('ebitValue').textContent = formatCurrency(analysis.ebit.ebit_margin);
        document.getElementById('ebitInsight').textContent = analysis.ebit.insight || '';
        const ebitBadge = document.getElementById('ebitConfidence');
        ebitBadge.textContent = `${analysis.ebit.confidence}%`;
        ebitBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.ebit.confidence)}`;
    }

    if (analysis.cogs) {
        const cogsValue = analysis.cogs.total_cogs;
        const cogsInsight = analysis.cogs.insight || '';
        document.getElementById('cogsValue').textContent = formatCurrency(cogsValue);
        document.getElementById('cogsInsight').textContent = cogsInsight;
        const cogsBadge = document.getElementById('cogsConfidence');
        cogsBadge.textContent = `${analysis.cogs.confidence}%`;
        cogsBadge.className = `confidence-badge ${getConfidenceBadgeClass(analysis.cogs.confidence)}`;
        hideCardIfNeeded('cogsCard', cogsValue, cogsInsight);
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
    
    // Render Key Risks
    if (analysis.key_risks && analysis.key_risks.length > 0) {
        const risksCard = document.getElementById('keyRisksCard');
        const risksContainer = document.getElementById('keyRisksContainer');
        risksContainer.innerHTML = '';
        
        analysis.key_risks.forEach(riskItem => {
            const riskDiv = document.createElement('div');
            riskDiv.className = 'risk-item';
            riskDiv.innerHTML = `
                <div class="risk-header">
                    <div class="risk-title">${riskItem.risk || riskItem}</div>
                    ${riskItem.probability ? `<span class="risk-probability">${riskItem.probability}</span>` : ''}
                </div>
                ${riskItem.impact ? `<div class="risk-impact"><strong>Impact:</strong> ${riskItem.impact}</div>` : ''}
                ${riskItem.mitigation ? `<div class="risk-mitigation"><strong>Mitigation:</strong> ${riskItem.mitigation}</div>` : ''}
            `;
            risksContainer.appendChild(riskDiv);
        });
        
        risksCard.style.display = 'block';
    }
    
    // Render Competitive Advantages
    if (analysis.competitive_advantages && analysis.competitive_advantages.length > 0) {
        const advCard = document.getElementById('competitiveAdvantagesCard');
        const advContainer = document.getElementById('competitiveAdvantagesContainer');
        advContainer.innerHTML = '';
        
        analysis.competitive_advantages.forEach(advItem => {
            const advDiv = document.createElement('div');
            advDiv.className = 'advantage-item';
            advDiv.innerHTML = `
                <div class="advantage-title">${advItem.advantage || advItem}</div>
                ${advItem.market_validation ? `<div class="advantage-validation"><strong>Market Validation:</strong> ${advItem.market_validation}</div>` : ''}
                ${advItem.sustainability_assessment ? `<div class="advantage-sustainability"><strong>Sustainability:</strong> ${advItem.sustainability_assessment}</div>` : ''}
            `;
            advContainer.appendChild(advDiv);
        });
        
        advCard.style.display = 'block';
    }
    
    // Render Sources
    if (analysis.sources && analysis.sources.length > 0) {
        const sourcesCard = document.getElementById('sourcesCard');
        const sourcesContainer = document.getElementById('sourcesContainer');
        sourcesContainer.innerHTML = '';
        
        analysis.sources.forEach((source, idx) => {
            const sourceDiv = document.createElement('div');
            sourceDiv.className = 'source-link-item';
            sourceDiv.innerHTML = `
                <a href="${source}" target="_blank" rel="noopener noreferrer" title="${source}">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px; display: inline-block; vertical-align: middle; margin-right: 8px;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    ${source}
                </a>
            `;
            sourcesContainer.appendChild(sourceDiv);
        });
        
        sourcesCard.style.display = 'block';
    }
    
    // Render Additional Notes
    if (analysis.additional_notes) {
        const notesCard = document.getElementById('additionalNotesCard');
        const notesText = document.getElementById('additionalNotesText');
        notesText.textContent = analysis.additional_notes;
        notesCard.style.display = 'block';
    }
    
    // Render Confidence Level Badge
    if (analysis.confidence_level) {
        const confidenceBadge = document.createElement('div');
        confidenceBadge.className = 'overall-confidence-badge';
        confidenceBadge.innerHTML = `
            <span class="badge-label">Overall Confidence:</span>
            <span class="badge-value">${analysis.confidence_level}</span>
        `;
        document.querySelector('.executive-summary-card').appendChild(confidenceBadge);
    }
    
    // Render all charts and visualizations
    if (typeof renderAllCharts === 'function') {
        setTimeout(() => renderAllCharts(analysis), 200);
    }
    
    // Initialize income simulator
    setTimeout(() => initializeSimulator(analysis), 300);
    
    // Attach click handlers to cards for modal interactions
    setTimeout(attachCardClickHandlers, 100);
}

newAnalysisBtn.addEventListener('click', resetUpload);

// Export to Excel functionality
if (exportExcelBtn) {
    exportExcelBtn.addEventListener('click', async () => {
        if (!analysisContext) {
            alert('No analysis data available to export');
            return;
        }
        
        console.log('📊 Exporting to Excel...');
        exportExcelBtn.disabled = true;
        exportExcelBtn.innerHTML = `
            <svg class="spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Generating...
        `;
        
        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(analysisContext)
            });
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }
            
            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'BMW_Analysis.xlsx';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?(.+)"?/i);
                if (match) filename = match[1];
            }
            
            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            console.log('✅ Excel exported successfully:', filename);
            
            // Show success message
            exportExcelBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Exported!
            `;
            
            setTimeout(() => {
                exportExcelBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Export to Excel
                `;
                exportExcelBtn.disabled = false;
            }, 2000);
            
        } catch (error) {
            console.error('❌ Export error:', error);
            alert('Failed to export analysis. Please try again.');
            exportExcelBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export to Excel
            `;
            exportExcelBtn.disabled = false;
        }
    });
}

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    if (textInput) {
        textInput.value = '';
        charCount.textContent = '0 characters';
    }
    analysisContext = null;
    
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
    
    // Reset and close chat
    if (chatSidebar) {
        chatSidebar.classList.remove('active');
    }
    if (resultsMainContent) {
        resultsMainContent.classList.remove('chat-open');
    }
    if (chatInput) {
        chatInput.value = '';
    }
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="chat-welcome">
                <div class="welcome-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                    </svg>
                </div>
                <h4>Chat with Quant AI</h4>
                <p>Ask questions about your analysis, request detailed breakdowns, or explore insights with interactive data visualizations.</p>
                <div class="chat-suggestions">
                    <div class="suggestion-chip" data-suggestion="Explain the TAM/SAM/SOM breakdown in detail">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span>Explain the market analysis</span>
                    </div>
                    <div class="suggestion-chip" data-suggestion="What are the main assumptions in this analysis?">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <span>Show me key assumptions</span>
                    </div>
                    <div class="suggestion-chip" data-suggestion="How can I improve the ROI?">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                        <span>Improvement recommendations</span>
                    </div>
                </div>
            </div>
        `;
    }
}

// Settings Functions
function loadSettings() {
    const saved = localStorage.getItem('quant_settings');
    if (saved) {
        return JSON.parse(saved);
    }
    return {
        temperature: 0.7,
        industry_focus: 'general',
        currency: 'EUR'
    };
}

function saveSettings() {
    localStorage.setItem('quant_settings', JSON.stringify(settings));
}

function applySettings() {
    if (temperatureSlider) {
        temperatureSlider.value = settings.temperature;
        temperatureValue.textContent = settings.temperature.toFixed(1);
    }
    if (industrySelect) industrySelect.value = settings.industry_focus;
    const currencyRadio = document.querySelector(`input[name="currency"][value="${settings.currency}"]`);
    if (currencyRadio) currencyRadio.checked = true;
    
    // Apply currency to dashboard on load
    updateDashboardCurrency(settings.currency);
}

// Settings Panel Handlers
if (settingsBtn) {
    settingsBtn.addEventListener('click', () => {
        if (settingsPanel) settingsPanel.classList.add('active');
    });
}

if (closeSettings) {
    closeSettings.addEventListener('click', () => {
        if (settingsPanel) settingsPanel.classList.remove('active');
    });
}

if (temperatureSlider) {
    temperatureSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        temperatureValue.textContent = val.toFixed(1);
        settings.temperature = val;
        saveSettings();
    });
}

if (industrySelect) {
    industrySelect.addEventListener('change', (e) => {
        settings.industry_focus = e.target.value;
        saveSettings();
    });
}

document.querySelectorAll('input[name="currency"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        settings.currency = e.target.value;
        saveSettings();
        // Apply currency change immediately to dashboard
        updateDashboardCurrency(e.target.value);
    });
});

if (resetSettings) {
    resetSettings.addEventListener('click', () => {
        settings = loadSettings();
        applySettings();
        updateDashboardCurrency(settings.currency);
    });
}

// Close settings panel when clicking outside
document.addEventListener('click', (e) => {
    if (settingsPanel && settingsPanel.classList.contains('active')) {
        if (!settingsPanel.contains(e.target) && !settingsBtn?.contains(e.target)) {
            settingsPanel.classList.remove('active');
        }
    }
});

// Function to update currency symbols in dashboard
function updateDashboardCurrency(currency) {
    const currencySymbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    };
    
    const symbol = currencySymbols[currency] || '€';
    
    // Update all currency displays in the dashboard
    document.querySelectorAll('.metric-value').forEach(el => {
        const text = el.textContent;
        // Replace existing currency symbols
        const updatedText = text.replace(/[$€£]/g, symbol);
        el.textContent = updatedText;
    });
    
    // Update chart tooltips and labels if charts exist
    if (window.charts) {
        Object.values(window.charts).forEach(chart => {
            if (chart && chart.options && chart.options.plugins && chart.options.plugins.tooltip) {
                chart.options.plugins.tooltip.callbacks.label = function(context) {
                    let label = context.dataset.label || '';
                    if (label) label += ': ';
                    if (context.parsed.y !== null) {
                        label += symbol + context.parsed.y.toLocaleString();
                    }
                    return label;
                };
                chart.update();
            }
        });
    }
    
    console.log(`💱 Currency updated to ${currency} (${symbol})`);
}

// Input Mode Tabs
const tabBtns = document.querySelectorAll('.tab-btn');
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        inputMode = mode;
        
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        if (mode === 'file') {
            if (uploadBox) uploadBox.style.display = 'block';
            if (textInputBox) textInputBox.style.display = 'none';
            uploadBtn.disabled = !selectedFile;
        } else {
            if (uploadBox) uploadBox.style.display = 'none';
            if (textInputBox) textInputBox.style.display = 'block';
            uploadBtn.disabled = !textInput.value.trim();
        }
    });
});

// Text Input Character Count
if (textInput) {
    textInput.addEventListener('input', () => {
        const count = textInput.value.length;
        if (charCount) charCount.textContent = `${count} characters`;
        uploadBtn.disabled = !textInput.value.trim();
    });
}

// Chat Handlers
if (toggleChatBtn) {
    toggleChatBtn.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('💬 Chat nav button clicked');
        if (chatSidebar) {
            chatSidebar.classList.toggle('active');
            console.log('   Chat sidebar active:', chatSidebar.classList.contains('active'));
        }
    });
}

if (closeChatSidebar) {
    closeChatSidebar.addEventListener('click', () => {
        console.log('❌ Closing chat sidebar');
        if (chatSidebar) chatSidebar.classList.remove('active');
    });
}

// Close chat when clicking outside
document.addEventListener('click', (e) => {
    if (chatSidebar && chatSidebar.classList.contains('active')) {
        // Check if click is outside chat sidebar and not on toggle button
        if (!chatSidebar.contains(e.target) && 
            !toggleChatBtn?.contains(e.target)) {
            chatSidebar.classList.remove('active');
        }
    }
});

// Handle suggestion chip clicks
document.addEventListener('click', (e) => {
    const suggestionChip = e.target.closest('.suggestion-chip');
    if (suggestionChip) {
        const suggestion = suggestionChip.getAttribute('data-suggestion');
        if (suggestion && chatInput) {
            chatInput.value = suggestion;
            chatInput.focus();
            // Auto-send the suggestion
            sendChatMessage();
        }
    }
});

if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });
}

async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message || !analysisContext) return;
    
    console.log('💬 Sending chat message:', message);
    
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    const typingId = addTypingIndicator();
    
    try {
        console.log('📡 Calling /api/chat endpoint...');
        console.log('📊 Analysis context keys:', Object.keys(analysisContext));
        console.log('🤖 Provider:', selectedProvider);
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                analysis_context: analysisContext,
                provider: selectedProvider,
                settings: settings,
                conversation_history: conversationHistory
            })
        });
        
        console.log('📥 Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Chat request failed:', errorText);
            throw new Error(`Chat request failed: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        console.log('✅ Chat response received:', data);
        console.log('   Response length:', data.response?.length);
        console.log('   Modifications:', data.modifications);
        console.log('   Simulation:', data.simulation ? 'Yes' : 'No');
        
        removeTypingIndicator(typingId);
        
        // Add assistant response
        addChatMessage(data.response || 'I received your message but have no response.', 'assistant');
        
        // Store in conversation history
        conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: data.response }
        );
        
        // If there are modifications, show them
        if (data.modifications) {
            console.log('🔧 Parameter modifications detected:', data.modifications);
            addModificationMessage(data.modifications);
        }
        
        // If simulation was run, update the UI
        if (data.simulation && data.simulation.analysis) {
            console.log('📊 Updating UI with simulation results...');
            
            // Update the simulated analysis
            updateComparisonDisplay(
                data.simulation.analysis,
                data.simulation.comparison
            );
            
            // Show success message
            addChatMessage(
                '✅ I\'ve updated the simulator with these changes. You can see the new projections above!',
                'assistant'
            );
        }
        
    } catch (error) {
        console.error('❌ Chat error:', error);
        console.error('   Error stack:', error.stack);
        
        removeTypingIndicator(typingId);
        addChatMessage(
            `Sorry, I encountered an error: ${error.message}. Please check the console for details.`,
            'assistant'
        );
    }
}

function addModificationMessage(modifications) {
    console.log('📝 Adding modification message to chat');
    
    const modList = Object.entries(modifications)
        .map(([key, value]) => {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            let displayValue = value;
            
            // Format based on parameter type
            if (key.includes('percentage') || key.includes('rate') || key.includes('coverage')) {
                displayValue = `${value}%`;
            } else if (key.includes('cost') || key.includes('revenue') || key.includes('savings')) {
                displayValue = `€${value.toLocaleString()}`;
            }
            
            return `• ${label}: ${displayValue}`;
        })
        .join('\n');
    
    const modMessage = `🔧 Parameter Changes:\n${modList}`;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message system';
    messageDiv.innerHTML = `
        <div class="message-content modification-notice">
            <pre>${escapeHtml(modMessage)}</pre>
        </div>
    `;
    
    if (chatMessages) {
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Simple markdown parser for chat messages
function parseMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Parse markdown
    // Bold: **text** or __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    // Italic: *text* or _text_
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');
    
    // Code: `text`
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');
    
    // Headers
    html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^# (.+)$/gm, '<h3>$1</h3>');
    
    // Lists - numbered
    html = html.replace(/^\d+\.\s+(.+)$/gm, '<li class="numbered-item">$1</li>');
    
    // Lists - bullet points
    html = html.replace(/^[-*]\s+(.+)$/gm, '<li class="bullet-item">$1</li>');
    
    // Wrap consecutive list items
    html = html.replace(/(<li class="numbered-item">.*?<\/li>\s*)+/gs, '<ol>$&</ol>');
    html = html.replace(/(<li class="bullet-item">.*?<\/li>\s*)+/gs, '<ul>$&</ul>');
    
    // Paragraphs - split by double newlines
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs.map(p => {
        // Don't wrap if already wrapped in tags
        if (p.match(/^<[h|u|o]/)) return p;
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');
    
    return html;
}

function addChatMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // Use logo.png for assistant avatar with white background
    const avatarContent = sender === 'assistant' 
        ? '<div class="chat-logo-container"><img src="logo.png" alt="AI Assistant" class="chat-logo-avatar" onerror="this.parentElement.style.display=\'none\'; this.parentElement.nextElementSibling.style.display=\'block\'"></div><svg viewBox="0 0 24 24" fill="currentColor" style="display:none;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>';
    
    const messageContent = sender === 'assistant' ? parseMarkdown(text) : escapeHtml(text);
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            ${avatarContent}
        </div>
        <div class="message-content">
            <div class="message-text">${messageContent}</div>
            <div class="message-timestamp">${timestamp}</div>
        </div>
    `;
    
    if (chatMessages) {
        // Remove welcome message if it exists
        const welcomeMsg = chatMessages.querySelector('.chat-welcome');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message assistant';
    typingDiv.id = 'typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <div class="chat-logo-container">
                <img src="logo.png" alt="AI Assistant" class="chat-logo-avatar" onerror="this.parentElement.style.display='none'; this.parentElement.nextElementSibling.style.display='block'">
            </div>
            <svg viewBox="0 0 24 24" fill="currentColor" style="display:none;">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    if (chatMessages) {
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    return 'typing-indicator';
}

function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Modal Functions
function openMetricModal(metricType, data) {
    const titles = {
        'tam': 'Total Addressable Market (TAM)',
        'sam': 'Serviceable Available Market (SAM)',
        'som': 'Serviceable Obtainable Market (SOM)',
        'roi': 'Return on Investment (ROI)',
        'turnover': 'Revenue & Turnover',
        'volume': 'Volume Metrics',
        'unit_economics': 'Unit Economics',
        'ebit': 'EBIT Analysis',
        'cogs': 'Cost of Goods Sold',
        'market_potential': 'Market Potential'
    };
    
    modalTitle.textContent = titles[metricType] || 'Metric Details';
    modalBody.innerHTML = generateModalContent(metricType, data);
    metricModal.classList.add('active');
    
    // Render charts if data has yearly projections
    if (data.numbers) {
        setTimeout(() => renderYearlyChart(metricType, data.numbers), 100);
    }
}

function closeMetricModal() {
    metricModal.classList.remove('active');
}

function generateModalContent(metricType, data) {
    let html = '';
    
    // Overview Section
    html += `<div class="detail-section">`;
    html += `<h3>Overview</h3>`;
    if (data.description_of_public) {
        html += `<p style="font-size: 15px; line-height: 1.7; color: var(--text-secondary); margin-bottom: 16px;">${data.description_of_public}</p>`;
    }
    
    // Key Metrics Grid
    html += `<div class="metric-stat-grid">`;
    
    // Add relevant stats based on metric type
    if (data.market_size) {
        html += `<div class="metric-stat-card">
            <div class="label">Market Size</div>
            <div class="value">${formatCurrency(data.market_size)}</div>
        </div>`;
    }
    if (data.growth_rate) {
        html += `<div class="metric-stat-card">
            <div class="label">Growth Rate (CAGR)</div>
            <div class="value">${data.growth_rate.toFixed(1)}%</div>
        </div>`;
    }
    if (data.confidence) {
        html += `<div class="metric-stat-card">
            <div class="label">Confidence</div>
            <div class="value" style="color: ${getConfidenceColor(data.confidence)}">${data.confidence}%</div>
        </div>`;
    }
    if (data.penetration_rate) {
        html += `<div class="metric-stat-card">
            <div class="label">Penetration Rate</div>
            <div class="value">${data.penetration_rate.toFixed(1)}%</div>
        </div>`;
    }
    if (data.roi_percentage) {
        html += `<div class="metric-stat-card">
            <div class="label">ROI Percentage</div>
            <div class="value">${data.roi_percentage.toFixed(1)}%</div>
        </div>`;
    }
    if (data.payback_period_months) {
        html += `<div class="metric-stat-card">
            <div class="label">Payback Period</div>
            <div class="value">${data.payback_period_months} months</div>
        </div>`;
    }
    
    html += `</div></div>`;
    
    // Justification
    if (data.justification) {
        html += `<div class="detail-section">`;
        html += `<h3>Justification</h3>`;
        html += `<p style="font-size: 14px; line-height: 1.7; color: var(--text-primary);">${data.justification}</p>`;
        html += `</div>`;
    }
    
    // Yearly Projections Table
    if (data.numbers) {
        html += `<div class="detail-section">`;
        html += `<h3>Yearly Projections</h3>`;
        html += `<table class="detail-table">`;
        html += `<thead><tr><th>Year</th><th>Value</th><th>YoY Change</th></tr></thead>`;
        html += `<tbody>`;
        
        const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030'];
        let prevValue = null;

        // Select appropriate formatter based on metric type
        const yearlyFormatter = (val) => {
            if (val === null || val === undefined) return 'N/A';
            if (metricType === 'volume') return formatNumber(val);
            if (metricType === 'roi') return formatPercentage(val);
            return formatCurrency(val);
        };

        years.forEach(year => {
            const value = data.numbers[year];
            if (value !== null && value !== undefined) {
                let changeHtml = '-';
                if (prevValue !== null && prevValue !== 0) {
                    const change = ((value - prevValue) / prevValue * 100);
                    const changeColor = change >= 0 ? 'var(--success)' : 'var(--error)';
                    changeHtml = `<span style="color: ${changeColor}">${change >= 0 ? '+' : ''}${change.toFixed(1)}%</span>`;
                }
                html += `<tr>
                    <td><strong>${year}</strong></td>
                    <td>${yearlyFormatter(value)}</td>
                    <td>${changeHtml}</td>
                </tr>`;
                prevValue = value;
            }
        });
        
        html += `</tbody></table>`;
        html += `<div class="chart-container"><canvas id="yearlyChart"></canvas></div>`;
        html += `</div>`;
    }
    
    // Breakdown
    if (data.breakdown || data.revenue_streams || data.cost_breakdown || data.opex_breakdown || data.cost_components) {
        const breakdown = data.breakdown || data.revenue_streams || data.cost_breakdown || data.opex_breakdown || data.cost_components;
        html += `<div class="detail-section">`;
        html += `<h3>Breakdown</h3>`;
        html += `<table class="detail-table">`;
        html += `<thead><tr><th>Category</th><th>Value</th></tr></thead>`;
        html += `<tbody>`;
        
        Object.entries(breakdown).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                let formatted;
                if (metricType === 'volume') {
                    formatted = formatNumber(value);
                } else if (metricType === 'roi' && typeof value === 'number' && value <= 200 && /roi|percentage|margin/i.test(key)) {
                    formatted = formatPercentage(value);
                } else {
                    formatted = formatCurrency(value);
                }
                html += `<tr>
                    <td>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td><strong>${formatted}</strong></td>
                </tr>`;
            }
        });
        
        html += `</tbody></table></div>`;
    }
    
    // Industry Example
    if (data.industry_example && data.industry_example.name) {
        html += `<div class="detail-section">`;
        html += `<h3>Industry Example</h3>`;
        html += `<div class="industry-example-card">`;
        html += `<h4>${data.industry_example.name}</h4>`;
        html += `<p>${data.industry_example.description}</p>`;
        if (data.industry_example.metric_value) {
            html += `<p><strong>Metric: </strong>${data.industry_example.metric_value}</p>`;
        }
        if (data.industry_example.link) {
            html += `<a href="${data.industry_example.link}" target="_blank" rel="noopener noreferrer">View Source →</a>`;
        }
        html += `</div></div>`;
    }
    
    // Additional Lists
    if (data.market_drivers && data.market_drivers.length > 0) {
        html += `<div class="detail-section">`;
        html += `<h3>Market Drivers</h3>`;
        html += `<ul style="margin-left: 20px; line-height: 1.8;">`;
        data.market_drivers.forEach(driver => {
            html += `<li style="margin-bottom: 8px; color: var(--text-primary);">${driver}</li>`;
        });
        html += `</ul></div>`;
    }
    
    if (data.barriers_to_entry && data.barriers_to_entry.length > 0) {
        html += `<div class="detail-section">`;
        html += `<h3>Barriers to Entry</h3>`;
        html += `<ul style="margin-left: 20px; line-height: 1.8;">`;
        data.barriers_to_entry.forEach(barrier => {
            html += `<li style="margin-bottom: 8px; color: var(--text-primary);">${barrier}</li>`;
        });
        html += `</ul></div>`;
    }
    
    if (data.growth_drivers && data.growth_drivers.length > 0) {
        html += `<div class="detail-section">`;
        html += `<h3>Growth Drivers</h3>`;
        html += `<ul style="margin-left: 20px; line-height: 1.8;">`;
        data.growth_drivers.forEach(driver => {
            html += `<li style="margin-bottom: 8px; color: var(--text-primary);">${driver}</li>`;
        });
        html += `</ul></div>`;
    }
    
    return html;
}

function renderYearlyChart(metricType, numbersData) {
    const canvas = document.getElementById('yearlyChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030'];
    const values = years.map(year => numbersData[year] || 0);
    
    const chartFormatter = (val) => {
        if (metricType === 'volume') return formatNumber(val);
        if (metricType === 'roi') return formatPercentage(val);
        return formatCurrency(val);
    };
    const datasetLabel = metricType === 'volume' ? 'Projected Units' : (metricType === 'roi' ? 'Projected ROI %' : 'Projected Value');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: datasetLabel,
                data: values,
                borderColor: '#1C69D4',
                backgroundColor: 'rgba(28, 105, 212, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#1C69D4',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            return chartFormatter(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return chartFormatter(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function getConfidenceColor(confidence) {
    if (confidence >= 80) return 'var(--success)';
    if (confidence >= 60) return 'var(--warning)';
    return 'var(--error)';
}

// Modal Event Listeners
if (closeModal) {
    closeModal.addEventListener('click', closeMetricModal);
}

if (modalBackdrop) {
    modalBackdrop.addEventListener('click', closeMetricModal);
}

// Attach click handlers to financial cards
function attachCardClickHandlers() {
    const cardMap = {
        'tamCard': 'tam',
        'samCard': 'sam',
        'somCard': 'som',
        'roiCard': 'roi',
        'turnoverCard': 'turnover',
        'volumeCard': 'volume',
        'unitEconomicsCard': 'unit_economics',
        'ebitCard': 'ebit',
        'cogsCard': 'cogs',
        'marketPotentialCard': 'market_potential'
    };
    
    Object.entries(cardMap).forEach(([cardId, metricType]) => {
        const card = document.getElementById(cardId);
        if (card && analysisContext) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', () => {
                if (analysisContext[metricType]) {
                    openMetricModal(metricType, analysisContext[metricType]);
                }
            });
        }
    });
}

// ============== HISTORY SIDEBAR FUNCTIONALITY ==============

// Load analysis history from the backend
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        
        const data = await response.json();
        historyData = data.history || [];
        renderHistory(historyData);
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = '<div class="history-empty">Failed to load history</div>';
    }
}

// Render history items in the sidebar
function renderHistory(items) {
    if (!items || items.length === 0) {
        historyList.innerHTML = '<div class="history-empty">No analysis history yet</div>';
        return;
    }
    
    historyList.innerHTML = items.map(item => {
        const date = item.date ? new Date(item.date) : null;
        const dateStr = date ? formatDateTime(date) : 'Unknown date';
        
        return `
            <div class="history-item ${item.id === currentAnalysisId ? 'active' : ''}" data-id="${item.id}">
                <div class="history-item-header">
                    <h4 class="history-item-title">${escapeHtml(item.title)}</h4>
                    <span class="history-item-provider history-item-provider-${item.provider}">
                        ${item.provider.toUpperCase()}
                    </span>
                </div>
                <div class="history-item-meta">
                    <span class="history-item-date">${dateStr}</span>
                    <span class="history-item-type">${item.file_type || 'unknown'}</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Attach click handlers to history items
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const id = item.getAttribute('data-id');
            loadAnalysisById(id);
        });
    });
}

// Format date and time with exact seconds
function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load analysis by ID from the backend
async function loadAnalysisById(id) {
    try {
        // Show loading state
        loadingSection.style.display = 'flex';
        uploadSection.style.display = 'none';
        resultsSection.style.display = 'none';
        
        const response = await fetch(`/api/documents/${id}`);
        if (!response.ok) {
            throw new Error('Failed to load analysis');
        }
        
        const data = await response.json();
        
        // Update current analysis ID
        currentAnalysisId = id;
        
        // Update active state in history list
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-id') === id);
        });
        
        // Save to context for chat
        analysisContext = data.analysis;
        
        // Display the analysis using existing displayResults function
        displayResults(data.analysis);
        
        // Close history sidebar on mobile
        if (window.innerWidth <= 768) {
            historySidebar.classList.remove('open');
        }
        
    } catch (error) {
        console.error('Error loading analysis:', error);
        loadingSection.style.display = 'none';
        uploadSection.style.display = 'flex';
        alert('Failed to load the selected analysis. Please try again.');
    }
}

// Search/filter history
function filterHistory() {
    const query = historySearchInput.value.toLowerCase().trim();
    
    if (!query) {
        renderHistory(historyData);
        return;
    }
    
    const filtered = historyData.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.provider.toLowerCase().includes(query) ||
        (item.file_type && item.file_type.toLowerCase().includes(query))
    );
    
    renderHistory(filtered);
}

// Toggle history sidebar
function toggleHistorySidebar() {
    historySidebar.classList.toggle('open');
}

// Close history sidebar
function closeHistorySidebarFunc() {
    historySidebar.classList.remove('open');
}

// History event listeners
if (historyNavItem) {
    historyNavItem.addEventListener('click', (e) => {
        e.preventDefault();
        toggleHistorySidebar();
    });
}

if (closeHistorySidebar) {
    closeHistorySidebar.addEventListener('click', closeHistorySidebarFunc);
}

if (historySearchInput) {
    historySearchInput.addEventListener('input', filterHistory);
}

// Load history on page load
loadHistory();

// ============== PAGE NAVIGATION ==============

function showDashboard() {
    console.log('📄 Switching to Dashboard');
    
    // Hide all pages
    simulatorPage.style.display = 'none';
    
    // Show dashboard sections based on whether we have results
    const hasResults = resultsSection.dataset.hasResults === 'true';
    uploadSection.style.display = hasResults ? 'none' : 'block';
    resultsSection.style.display = hasResults ? 'block' : 'none';
    
    // Chat sidebar state is preserved (it's now global)
    console.log('   Chat sidebar active:', chatSidebar?.classList.contains('active'));
    
    // Update nav (exclude chat button from active state changes)
    document.querySelectorAll('.nav-item:not(#toggleChatBtn)').forEach(item => item.classList.remove('active'));
    dashboardNavItem.classList.add('active');
}

function showSimulator() {
    console.log('🎯 Switching to Simulator');
    
    // Hide dashboard sections
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Show simulator page
    simulatorPage.style.display = 'flex';
    
    // Chat sidebar state is preserved (it's now global)
    console.log('   Chat sidebar active:', chatSidebar?.classList.contains('active'));
    
    // Check if we have analysis data
    if (analysisContext) {
        simulatorEmptyState.style.display = 'none';
        simulatorContent.style.display = 'block';
    } else {
        simulatorEmptyState.style.display = 'flex';
        simulatorContent.style.display = 'none';
    }
    
    // Update nav (exclude chat button from active state changes)
    document.querySelectorAll('.nav-item:not(#toggleChatBtn)').forEach(item => item.classList.remove('active'));
    simulatorNavItem.classList.add('active');
}

// Navigation event listeners
if (dashboardNavItem) {
    dashboardNavItem.addEventListener('click', (e) => {
        e.preventDefault();
        showDashboard();
    });
}

if (simulatorNavItem) {
    simulatorNavItem.addEventListener('click', (e) => {
        e.preventDefault();
        showSimulator();
    });
}

if (goToDashboardBtn) {
    goToDashboardBtn.addEventListener('click', (e) => {
        e.preventDefault();
        showDashboard();
    });
}

// ============== STICKY HEADER FUNCTIONALITY ==============

// Add shadow to header on scroll
const header = document.querySelector('.header');
if (header) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// ============== END HISTORY/HEADER FUNCTIONALITY ==============

// Initialize settings on load
applySettings();

// Cost Accordion Functionality
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('cost-accordion-toggle') || e.target.closest('.cost-accordion-toggle')) {
        const toggle = e.target.classList.contains('cost-accordion-toggle') ? e.target : e.target.closest('.cost-accordion-toggle');
        const targetId = toggle.getAttribute('data-target');
        const content = document.getElementById(targetId);
        
        if (content) {
            const isActive = toggle.classList.contains('active');
            
            // Toggle active state
            if (isActive) {
                toggle.classList.remove('active');
                content.classList.remove('active');
            } else {
                toggle.classList.add('active');
                content.classList.add('active');
            }
        }
    }
});

// ============== INCOME SIMULATOR FUNCTIONALITY ==============

let simulationChart = null;
let originalParameters = {};
let currentParameters = {};

function initializeSimulator(analysis) {
    if (!analysis) return;
    
    // Store analysis context globally
    analysisContext = analysis;
    
    // Store original parameters
    originalParameters = {
        project_name: analysis.project_name || 'Business Analysis',
        project_type: analysis.project_type || 'revenue',
        annual_revenue_or_savings: analysis.turnover?.total_revenue * 5 || analysis.som?.revenue_potential || 0,
        growth_rate: analysis.tam?.growth_rate || 5,
        price_per_unit: analysis.unit_economics?.unit_revenue || 0,
        fleet_size_or_units: analysis.volume?.units_sold || 0,
        development_cost: analysis.total_estimated_cost_summary?.total_cost_5_years * 0.1 || 0,
        market_coverage: 50,
        take_rate: 10,
        royalty_percentage: 0
    };
    
    currentParameters = { ...originalParameters };
    
    // Build parameter controls
    buildParameterControls(analysis);
    
    // Initialize comparison display
    updateComparisonDisplay(analysis, analysis);
    
    // Setup event listeners
    setupSimulatorEvents();
}

function buildParameterControls(analysis) {
    const container = document.getElementById('parameterControls');
    if (!container) return;
    
    container.innerHTML = '';
    
    const projectType = analysis.project_type || 'revenue';
    const isSavings = projectType === 'savings';
    
    // Growth Rate
    addParameterControl(container, {
        id: 'growth_rate',
        label: 'Annual Growth Rate',
        value: currentParameters.growth_rate,
        min: -10,
        max: 30,
        step: 0.5,
        suffix: '%',
        format: (v) => `${v.toFixed(1)}%`
    });
    
    // Annual Revenue/Savings
    if (isSavings) {
        const annualSavings = originalParameters.annual_revenue_or_savings / 5;
        addParameterControl(container, {
            id: 'annual_revenue_or_savings',
            label: 'Annual Savings (Year 1)',
            value: annualSavings,
            min: annualSavings * 0.5,
            max: annualSavings * 2,
            step: annualSavings * 0.05,
            prefix: '€',
            format: (v) => formatCurrency(v)
        });
    } else {
        // Price per Unit
        if (currentParameters.price_per_unit > 0) {
            addParameterControl(container, {
                id: 'price_per_unit',
                label: 'Price per Unit',
                value: currentParameters.price_per_unit,
                min: currentParameters.price_per_unit * 0.5,
                max: currentParameters.price_per_unit * 2,
                step: currentParameters.price_per_unit * 0.05,
                prefix: '€',
                format: (v) => formatCurrency(v)
            });
        }
        
        // Volume/Units
        if (currentParameters.fleet_size_or_units > 0) {
            addParameterControl(container, {
                id: 'fleet_size_or_units',
                label: 'Volume (Units)',
                value: currentParameters.fleet_size_or_units,
                min: currentParameters.fleet_size_or_units * 0.5,
                max: currentParameters.fleet_size_or_units * 2,
                step: currentParameters.fleet_size_or_units * 0.05,
                format: (v) => formatNumber(v)
            });
        }
    }
    
    // Development Cost
    if (currentParameters.development_cost > 0) {
        addParameterControl(container, {
            id: 'development_cost',
            label: 'Implementation Cost',
            value: currentParameters.development_cost,
            min: 0,
            max: currentParameters.development_cost * 3,
            step: currentParameters.development_cost * 0.1,
            prefix: '€',
            format: (v) => formatCurrency(v)
        });
    }
    
    // Market Coverage (for revenue projects)
    if (!isSavings) {
        addParameterControl(container, {
            id: 'market_coverage',
            label: 'Market Coverage',
            value: currentParameters.market_coverage,
            min: 10,
            max: 100,
            step: 5,
            suffix: '%',
            format: (v) => `${v.toFixed(0)}%`
        });
    }
}

function addParameterControl(container, config) {
    const group = document.createElement('div');
    group.className = 'parameter-group';
    
    group.innerHTML = `
        <div class="parameter-label">
            <span>${config.label}</span>
            <span class="parameter-value" id="${config.id}_value">${config.format(config.value)}</span>
        </div>
        <input 
            type="range" 
            class="parameter-slider" 
            id="${config.id}_slider"
            min="${config.min}" 
            max="${config.max}" 
            step="${config.step}" 
            value="${config.value}"
            data-param="${config.id}"
            data-format="${config.format.toString()}"
        />
    `;
    
    container.appendChild(group);
    
    // Add event listener
    const slider = group.querySelector('.parameter-slider');
    const valueDisplay = group.querySelector('.parameter-value');
    
    // Initialize slider fill
    updateSliderFill(slider);
    
    slider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        currentParameters[config.id] = value;
        
        // Update slider fill
        updateSliderFill(slider);
        
        // Special handling for annual_revenue_or_savings
        if (config.id === 'annual_revenue_or_savings') {
            currentParameters[config.id] = value * 5; // Convert back to 5-year total
            valueDisplay.textContent = config.format(value);
        } else {
            valueDisplay.textContent = config.format(value);
        }
    });
}

function setupSimulatorEvents() {
    // Run Simulation button
    const runBtn = document.getElementById('runSimulation');
    if (runBtn) {
        runBtn.addEventListener('click', runSimulation);
    }
    
    // Reset button
    const resetBtn = document.getElementById('resetSimulation');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            // Reset to original parameters
            currentParameters = { ...originalParameters };
            
            // Reset all scenario buttons
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.scenario === 'current') {
                    btn.classList.add('active');
                }
            });
            
            // Rebuild controls and run simulation with original values
            buildParameterControls(analysisContext);
            
            // Visual feedback
            resetBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Reset!
            `;
            
            setTimeout(() => {
                resetBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Reset
                `;
                
                // Re-run simulation with original values
                runSimulation();
            }, 800);
        });
    }
    
    // Scenario buttons
    const scenarioBtns = document.querySelectorAll('.scenario-btn');
    scenarioBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            scenarioBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const scenario = e.target.dataset.scenario;
            applyScenario(scenario);
        });
    });
}

function applyScenario(scenario) {
    const multipliers = {
        current: 1.0,
        optimistic: 1.3,
        conservative: 0.7
    };
    
    const mult = multipliers[scenario] || 1.0;
    
    // Adjust parameters based on scenario
    if (scenario === 'optimistic') {
        currentParameters.growth_rate = Math.min(originalParameters.growth_rate * 1.5, 30);
        currentParameters.annual_revenue_or_savings = originalParameters.annual_revenue_or_savings * 1.3;
        currentParameters.market_coverage = Math.min(originalParameters.market_coverage * 1.2, 100);
    } else if (scenario === 'conservative') {
        currentParameters.growth_rate = Math.max(originalParameters.growth_rate * 0.7, 0);
        currentParameters.annual_revenue_or_savings = originalParameters.annual_revenue_or_savings * 0.7;
        currentParameters.market_coverage = originalParameters.market_coverage * 0.8;
    } else {
        currentParameters = { ...originalParameters };
    }
    
    buildParameterControls(analysisContext);
    runSimulation();
}

async function runSimulation() {
    const runBtn = document.getElementById('runSimulation');
    const originalText = runBtn.innerHTML;
    
    try {
        // Show loading state
        runBtn.disabled = true;
        runBtn.innerHTML = `
            <svg style="animation: spin 1s linear infinite; width: 18px; height: 18px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Calculating...
        `;
        
        console.log('🎯 Running simulation with parameters:', currentParameters);
        
        const response = await fetch('/api/simulate-income', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_id: currentAnalysisId,
                parameters: currentParameters
            })
        });
        
        if (!response.ok) throw new Error('Simulation failed');
        
        const data = await response.json();
        console.log('✓ Simulation complete:', data);
        
        // Update display with new results
        updateComparisonDisplay(analysisContext, data.analysis, data.comparison);
        
        // Show success feedback
        runBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Updated!
        `;
        
        setTimeout(() => {
            runBtn.innerHTML = originalText;
            runBtn.disabled = false;
        }, 1500);
        
    } catch (error) {
        console.error('❌ Simulation error:', error);
        runBtn.innerHTML = originalText;
        runBtn.disabled = false;
        alert('Failed to run simulation. Please try again.');
    }
}

function updateComparisonDisplay(original, simulated, comparison) {
    // Remove pulse animation - make it live and smooth
    // document.querySelectorAll('.metric-card-sim').forEach(card => {
    //     card.classList.add('updating');
    //     setTimeout(() => card.classList.remove('updating'), 500);
    // });
    
    // Update income/cost/profit cards
    const totalIncome = simulated.total_estimated_cost_summary?.total_revenue_5_years || 0;
    const totalCost = simulated.total_estimated_cost_summary?.total_cost_5_years || 0;
    const netProfit = simulated.total_estimated_cost_summary?.net_profit_5_years || 0;
    const roi = simulated.total_estimated_cost_summary?.roi_percentage || 0;
    const breakeven = simulated.total_estimated_cost_summary?.break_even_months || 0;
    
    document.getElementById('simulatedIncome').textContent = formatCurrency(totalIncome);
    document.getElementById('simulatedCost').textContent = formatCurrency(totalCost);
    document.getElementById('simulatedProfit').textContent = formatCurrency(netProfit);
    document.getElementById('simulatedROI').textContent = `${roi.toFixed(1)}%`;
    
    // Better break-even display
    const breakevenElement = document.getElementById('breakevenMonths');
    if (breakeven === 0) {
        breakevenElement.textContent = 'Immediate';
        breakevenElement.style.color = '#10b981'; // Green for immediate ROI
    } else if (breakeven >= 60) {
        breakevenElement.textContent = 'Never (>5 years)';
        breakevenElement.style.color = '#ef4444'; // Red for never
    } else if (breakeven >= 36) {
        breakevenElement.textContent = `${breakeven} months`;
        breakevenElement.style.color = '#f59e0b'; // Orange for long payback
    } else {
        breakevenElement.textContent = `${breakeven} months`;
        breakevenElement.style.color = '#10b981'; // Green for quick payback
    }
    
    // Update change indicators
    if (comparison) {
        updateChangeIndicator('incomeChange', comparison.tam_change, comparison.tam_change_pct);
        updateChangeIndicator('costChange', 0, 0); // Cost change not tracked yet
        updateChangeIndicator('profitChange', comparison.som_change, comparison.som_change_pct);
        updateChangeIndicator('roiChangeValue', comparison.roi_change, null);
    }
    
    // Update chart
    updateSimulationChart(simulated);
}

function updateChangeIndicator(elementId, absoluteChange, percentChange) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const isPositive = absoluteChange > 0;
    const isNegative = absoluteChange < 0;
    
    element.className = 'comparison-change';
    if (isPositive) element.classList.add('positive');
    else if (isNegative) element.classList.add('negative');
    else element.classList.add('neutral');
    
    const arrow = isPositive ? '↑' : isNegative ? '↓' : '•';
    const pctText = percentChange !== null && percentChange !== undefined 
        ? `${arrow} ${Math.abs(percentChange).toFixed(1)}%` 
        : `${arrow} ${formatCurrency(Math.abs(absoluteChange))}`;
    
    element.textContent = pctText;
}

function updateSimulationChart(analysis) {
    const canvas = document.getElementById('simulationChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart
    if (simulationChart) {
        simulationChart.destroy();
    }
    
    // Extract 5-year data
    const years = ['2025', '2026', '2027', '2028', '2029'];
    const revenueData = years.map(y => analysis.turnover?.numbers?.[y] || 0);
    const costData = years.map(y => analysis.yearly_cost_breakdown?.[y]?.total_cost || 0);
    const profitData = revenueData.map((rev, i) => rev - costData[i]);
    
    simulationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Income',
                    data: revenueData,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Cost',
                    data: costData,
                    borderColor: '#F59E0B',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Net Profit',
                    data: profitData,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

// Helper function for formatting currency in simulator
function formatCurrency(value) {
    if (!value && value !== 0) return 'N/A';
    return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'EUR',
        notation: 'compact',
        maximumFractionDigits: 1
    }).format(value);
}

function formatNumber(value) {
    if (!value && value !== 0) return 'N/A';
    return new Intl.NumberFormat('en-US', { 
        notation: 'compact',
        maximumFractionDigits: 1
    }).format(value);
}

function updateSliderFill(slider) {
    const min = parseFloat(slider.min);
    const max = parseFloat(slider.max);
    const value = parseFloat(slider.value);
    const percentage = ((value - min) / (max - min)) * 100;
    slider.style.background = `linear-gradient(to right, var(--primary-light) 0%, var(--primary-light) ${percentage}%, var(--border-light) ${percentage}%, var(--border-light) 100%)`;
}

// ============== END INCOME SIMULATOR ==============

