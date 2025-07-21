// Global variables
let currentResults = null;
let currentTab = 'simple';

// DOM elements
const documentInput = document.getElementById('documentInput');
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
    const documentContent = documentInput.value.trim();
    
    if (!documentContent) {
        showError('Please enter document content to generate questions.');
        return;
    }
    
    const targetCount = parseInt(targetQuestions.value);
    if (targetCount < 3 || targetCount > 15) {
        showError('Target questions must be between 3 and 15.');
        return;
    }
    
    const requestData = {
        documents: [
            {
                page_content: documentContent,
                metadata: {
                    source: "user_input.txt",
                    timestamp: new Date().toISOString()
                }
            }
        ],
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
    
    // Disable buttons during loading
    generateBtn.disabled = true;
    demoBtn.disabled = true;
}

// Show results
function showResults(data) {
    hideAllSections();
    resultsSection.classList.remove('hidden');
    
    // Store results globally
    currentResults = data;
    
    // Update stats
    questionCount.textContent = data.total_questions;
    processingTime.textContent = data.processing_time.toFixed(1);
    
    // Display questions for current tab
    displayQuestions(currentTab);
    
    // Re-enable buttons
    generateBtn.disabled = false;
    demoBtn.disabled = false;
}

// Show error
function showError(message) {
    hideAllSections();
    errorSection.classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
    
    // Re-enable buttons
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
    
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Display questions for selected tab
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

// Utility function to format evolution type for display
function formatEvolutionType(type) {
    return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Add some helpful features
document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textarea
    const textarea = document.getElementById('documentInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
    
    // Add character count
    const charCount = document.createElement('div');
    charCount.style.cssText = 'text-align: right; color: #718096; font-size: 0.875rem; margin-top: 0.5rem;';
    textarea.parentNode.appendChild(charCount);
    
    textarea.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = `${count} characters`;
        
        if (count > 2000) {
            charCount.style.color = '#e53e3e';
        } else if (count > 1000) {
            charCount.style.color = '#d69e2e';
        } else {
            charCount.style.color = '#718096';
        }
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to generate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!generateBtn.disabled) {
                handleGenerate();
            }
        }
        
        // Escape to hide error
        if (e.key === 'Escape') {
            hideError();
        }
    });
    
    // Add tooltips for buttons
    generateBtn.title = 'Generate questions from your document (Ctrl+Enter)';
    demoBtn.title = 'Try with sample loan documents';
    
    // Add loading animation to buttons
    [generateBtn, demoBtn].forEach(btn => {
        btn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            this.disabled = true;
            
            // Reset after a delay (will be overridden by actual API response)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 10000);
        });
    });
});

// Add smooth scrolling for better UX
function scrollToElement(element) {
    element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Add copy functionality for questions
function addCopyFunctionality() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn')) {
            const textToCopy = e.target.dataset.text;
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success feedback
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
}

// Initialize copy functionality
addCopyFunctionality(); 