// Global variables
let currentResults = null;
let currentTab = 'simple';
let uploadedDocs = [];

// DOM elements
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const targetQuestions = document.getElementById('targetQuestions');
const generateBtn = document.getElementById('generateBtn');
const demoBtn = document.getElementById('demoBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const questionsContainer = document.getElementById('questionsContainer');
const questionCount = document.getElementById('questionCount');
const processingTime = document.getElementById('processingTime');

// API configuration
const API_BASE_URL = window.location.origin; // Will work for both local and deployed

// File upload and preview logic
fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect(e) {
    const files = Array.from(e.target.files).slice(0, 3); // Max 3 files
    uploadedDocs = [];
    filePreview.innerHTML = '';

    if (files.length === 0) {
        filePreview.innerHTML = '<span style="color:#718096;">No files selected.</span>';
        return;
    }

    files.forEach((file, idx) => {
        const ext = file.name.split('.').pop().toLowerCase();
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        let icon = '<i class="fas fa-file-alt file-icon"></i>';
        if (ext === 'pdf') icon = '<i class="fas fa-file-pdf file-icon" style="color:#e53e3e;"></i>';
        if (ext === 'docx') icon = '<i class="fas fa-file-word file-icon" style="color:#3182ce;"></i>';

        let infoHtml = `<div class="file-info">
            <span class="file-name">${file.name}</span>
            <span class="file-size">(${(file.size/1024).toFixed(1)} KB)</span>`;

        if (ext === 'txt') {
            // Read as text
            const reader = new FileReader();
            reader.onload = function(ev) {
                const text = ev.target.result;
                uploadedDocs[idx] = {
                    page_content: text.slice(0, 2000), // Limit for demo
                    metadata: {
                        source: file.name,
                        size: file.size,
                        type: file.type
                    }
                };
                fileItem.innerHTML = icon + infoHtml + `<div class="file-snippet">${escapeHtml(text.slice(0, 300))}${text.length > 300 ? '...':''}</div></div>`;
            };
            reader.readAsText(file);
        } else {
            // For pdf/docx, just show info, don't send to backend in MVP
            uploadedDocs[idx] = null;
            fileItem.innerHTML = icon + infoHtml + `<div class="file-snippet" style="color:#e53e3e;">Preview not supported in browser. Will be ignored for now.</div></div>`;
        }
        filePreview.appendChild(fileItem);
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    generateBtn.addEventListener('click', handleGenerate);
    demoBtn.addEventListener('click', handleDemo);
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
});

// Handle generate button click
async function handleGenerate() {
    // Only use .txt files for now
    const docs = uploadedDocs.filter(Boolean);
    if (docs.length === 0) {
        showError('Please upload at least one .txt document. PDF/DOCX not supported in browser preview.');
        return;
    }
    const targetCount = parseInt(targetQuestions.value);
    if (targetCount < 3 || targetCount > 15) {
        showError('Target questions must be between 3 and 15.');
        return;
    }
    const requestData = {
        documents: docs,
        target_questions: targetCount
    };
    await callAPI('/generate', requestData);
}

// Handle demo button click
async function handleDemo() {
    showLoading();
    await callAPI('/generate-demo', null);
}

// Make API call
async function callAPI(endpoint, requestData) {
    try {
        showLoading();
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        if (requestData) {
            options.body = JSON.stringify(requestData);
        }
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        showResults(data);
    } catch (error) {
        console.error('API Error:', error);
        showError(`Failed to generate questions: ${error.message}`);
    }
}

// Show loading state
function showLoading() {
    hideAllSections();
    loadingSection.classList.remove('hidden');
    generateBtn.disabled = true;
    demoBtn.disabled = true;
}

// Show results
function showResults(data) {
    hideAllSections();
    resultsSection.classList.remove('hidden');
    currentResults = data;
    questionCount.textContent = data.total_questions;
    processingTime.textContent = data.processing_time.toFixed(1);
    displayQuestions(currentTab);
    generateBtn.disabled = false;
    demoBtn.disabled = false;
}

// Show error
function showError(message) {
    hideAllSections();
    errorSection.classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
    generateBtn.disabled = false;
    demoBtn.disabled = false;
}

// Hide error
function hideError() {
    errorSection.classList.add('hidden');
}

// Hide all sections
function hideAllSections() {
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

// Switch tabs
function switchTab(tabName) {
    currentTab = tabName;
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    if (currentResults) {
        displayQuestions(tabName);
    }
}

// Display questions for a specific tab
function displayQuestions(tabName) {
    if (!currentResults) return;
    const questions = currentResults.evolved_questions.filter(q => q.evolution_type === tabName);
    const answers = currentResults.question_answers;
    const contexts = currentResults.question_contexts;
    questionsContainer.innerHTML = '';
    if (questions.length === 0) {
        questionsContainer.innerHTML = `
            <div class="question-card">
                <p style="text-align: center; color: #718096; font-style: italic;">
                    No ${tabName.replace('_', ' ')} questions generated yet.
                </p>
            </div>
        `;
        return;
    }
    questions.forEach(question => {
        const answer = answers.find(a => a.question_id === question.id);
        const context = contexts.find(c => c.question_id === question.id);
        const questionCard = createQuestionCard(question, answer, context);
        questionsContainer.appendChild(questionCard);
    });
}

// Create question card element
function createQuestionCard(question, answer, context) {
    const card = document.createElement('div');
    card.className = 'question-card';
    const evolutionTypeClass = question.evolution_type.replace('_', '-');
    const evolutionTypeText = question.evolution_type.replace('_', ' ');
    card.innerHTML = `
        <div class="question-header">
            <span class="question-id">${question.id}</span>
            <span class="evolution-type ${evolutionTypeClass}">${evolutionTypeText}</span>
        </div>
        <div class="question-text">
            ${escapeHtml(question.question)}
        </div>
        <div class="question-details">
            <div class="detail-section">
                <h4>Generated Answer</h4>
                <p>${answer ? escapeHtml(answer.answer) : 'No answer available.'}</p>
            </div>
            <div class="detail-section">
                <h4>Relevant Contexts</h4>
                ${context && context.contexts.length > 0 ? `
                    <ul class="context-list">
                        ${context.contexts.map(ctx => `<li>${escapeHtml(ctx)}</li>`).join('')}
                    </ul>
                ` : '<p>No contexts available.</p>'}
            </div>
        </div>
    `;
    return card;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add copy functionality for questions
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn')) {
            const textToCopy = e.target.dataset.text;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = e.target.innerHTML;
                e.target.innerHTML = '<i class="fas fa-check"></i> Copied!';
                e.target.style.background = '#48bb78';
                setTimeout(() => {
                    e.target.innerHTML = originalText;
                    e.target.style.background = '';
                }, 2000);
            });
        }
    });
}); 