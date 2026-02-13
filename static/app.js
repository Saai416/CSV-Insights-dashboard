let currentReportId = null;
let currentSummary = null;
let currentInsights = null;
let barChartInstance = null;
let histogramInstance = null;

// Step activation
function activateStep(stepNumber) {
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        const circle = step.querySelector('div');

        if (i <= stepNumber) {
            step.classList.remove('border-gray-200');
            step.classList.add('border-gray-300');
            circle.classList.remove('bg-gray-300', 'text-gray-600');
            circle.classList.add('bg-slate-700', 'text-white');
        } else {
            step.classList.remove('border-gray-300');
            step.classList.add('border-gray-200');
            circle.classList.remove('bg-slate-700', 'text-white');
            circle.classList.add('bg-gray-300', 'text-gray-600');
        }
    }
}

// File upload handling
document.getElementById('fileInput').addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file
    if (!file.name.endsWith('.csv')) {
        showError('Invalid file type. Only CSV files are allowed.');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showError('File too large. Maximum size is 5MB.');
        return;
    }

    // Show file info
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileInfo').classList.remove('hidden');

    // Upload file
    uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showError('', true);
    showSuccess('Uploading and analyzing...', false);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            showSuccess('', true); // Clear success message
            showError(data.error || 'Upload failed');
            return;
        }

        // Success - data now includes structured insights and chart_data
        currentReportId = data.report_id;
        currentSummary = data.summary;
        currentInsights = data.insights;

        showSuccess('File uploaded successfully', false);

        // Show warning if present
        if (data.warning) {
            showWarning(data.warning);
        } else {
            showWarning('', true);
        }

        activateStep(2);

        // Display summary
        displaySummary(data.summary);

        // Display preview
        displayPreview(data.summary);

        // Display charts
        displayCharts(data.chart_data);

        // Display insights (already generated)
        displayStructuredInsights(data.insights);
        document.getElementById('insightsPanel').classList.remove('hidden');
        document.getElementById('generateBtn').classList.add('hidden');
        document.getElementById('insightsContent').classList.remove('hidden');

        // Show export and question panels
        document.getElementById('exportPanel').classList.remove('hidden');
        document.getElementById('questionPanel').classList.remove('hidden');

        // Load history for this report
        loadQuestions(currentReportId);

        activateStep(4);

        // Load reports
        loadReports();

    } catch (error) {
        showSuccess('', true); // Clear success message
        showError('Network error. Please try again.');
    }
}

function displaySummary(summary) {
    document.getElementById('rowCount').textContent = summary.row_count;
    document.getElementById('colCount').textContent = summary.column_count;

    // Count numeric and categorical columns
    let numericCount = 0;
    let categoricalCount = 0;

    if (summary.numeric_stats) {
        numericCount = Object.keys(summary.numeric_stats).length;
    }
    categoricalCount = summary.column_count - numericCount;

    document.getElementById('numericCount').textContent = numericCount;
    document.getElementById('categoricalCount').textContent = categoricalCount;

    document.getElementById('summaryPanel').classList.remove('hidden');
}

function displayPreview(summary) {
    const columns = summary.columns;
    const sampleData = summary.sample_data;

    // Create table header
    const headerRow = document.getElementById('tableHeader');
    headerRow.innerHTML = '';

    columns.forEach(col => {
        const th = document.createElement('th');
        th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
        th.textContent = col;
        headerRow.appendChild(th);
    });

    // Create table rows from sample data
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    // Determine max rows from sample data
    const maxRows = Math.max(...Object.values(sampleData).map(arr => arr.length));

    for (let i = 0; i < Math.min(maxRows, 50); i++) {
        const tr = document.createElement('tr');

        columns.forEach(col => {
            const td = document.createElement('td');
            td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
            const value = sampleData[col]?.[i];
            td.textContent = value !== null && value !== undefined ? value : 'N/A';
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    }

    document.getElementById('previewPanel').classList.remove('hidden');
}

function displayCharts(chartData) {
    if (!chartData || !chartData.has_numeric) {
        document.getElementById('chartsPanel').classList.remove('hidden');
        document.getElementById('noChartsMsg').classList.remove('hidden');
        return;
    }

    document.getElementById('chartsPanel').classList.remove('hidden');
    document.getElementById('noChartsMsg').classList.add('hidden');

    // Update titles
    document.getElementById('barChartTitle').textContent = chartData.bar_chart.title;
    document.getElementById('histogramTitle').textContent = chartData.histogram.title;

    // Destroy existing charts if any
    if (barChartInstance) barChartInstance.destroy();
    if (histogramInstance) histogramInstance.destroy();

    // Create bar chart
    const barCtx = document.getElementById('barChart').getContext('2d');
    barChartInstance = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: chartData.bar_chart.labels,
            datasets: [{
                label: chartData.primary_column,
                data: chartData.bar_chart.values,
                backgroundColor: 'rgba(51, 65, 85, 0.8)',
                borderColor: 'rgba(51, 65, 85, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Create histogram
    const histCtx = document.getElementById('histogram').getContext('2d');
    histogramInstance = new Chart(histCtx, {
        type: 'bar',
        data: {
            labels: chartData.histogram.labels,
            datasets: [{
                label: 'Frequency',
                data: chartData.histogram.values,
                backgroundColor: 'rgba(71, 85, 105, 0.8)',
                borderColor: 'rgba(71, 85, 105, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function displayStructuredInsights(insights) {
    // Render summary with markdown support
    const summaryDiv = document.getElementById('summaryText');
    summaryDiv.innerHTML = marked.parse(insights.summary || 'No summary available');

    // Render key trends
    const trendsList = document.getElementById('trendsList');
    trendsList.innerHTML = '';
    if (insights.key_trends && insights.key_trends.length > 0) {
        insights.key_trends.forEach(trend => {
            const li = document.createElement('li');
            li.textContent = trend;
            trendsList.appendChild(li);
        });
    } else {
        trendsList.innerHTML = '<li class="text-gray-500">No trends identified</li>';
    }

    // Render outliers
    const outliersSection = document.getElementById('outliersSection');
    const outliersList = document.getElementById('outliersList');
    outliersList.innerHTML = '';
    if (insights.outliers && insights.outliers.length > 0) {
        outliersSection.classList.remove('hidden');
        insights.outliers.forEach(outlier => {
            const li = document.createElement('li');
            li.textContent = outlier;
            outliersList.appendChild(li);
        });
    } else {
        outliersSection.classList.add('hidden');
    }

    // Render risks
    const risksSection = document.getElementById('risksSection');
    const risksList = document.getElementById('risksList');
    risksList.innerHTML = '';
    if (insights.risks && insights.risks.length > 0) {
        risksSection.classList.remove('hidden');
        insights.risks.forEach(risk => {
            const li = document.createElement('li');
            li.textContent = risk;
            risksList.appendChild(li);
        });
    } else {
        risksSection.classList.add('hidden');
    }

    // Render recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    if (insights.recommendations && insights.recommendations.length > 0) {
        insights.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationsList.appendChild(li);
        });
    } else {
        recommendationsList.innerHTML = '<li class="text-gray-500">No recommendations</li>';
    }
}

// Export functionality
document.getElementById('copyBtn').addEventListener('click', async () => {
    if (!currentReportId) {
        showError('No report to export');
        return;
    }

    try {
        const response = await fetch('/export/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ report_id: currentReportId })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Export failed');
            return;
        }

        // Copy to clipboard
        await navigator.clipboard.writeText(data.formatted_text);

        const successDiv = document.getElementById('exportSuccess');
        successDiv.textContent = 'Copied to clipboard!';
        successDiv.classList.remove('hidden');
        setTimeout(() => successDiv.classList.add('hidden'), 3000);

    } catch (error) {
        showError('Failed to copy to clipboard');
    }
});

document.getElementById('downloadBtn').addEventListener('click', async () => {
    if (!currentReportId) {
        showError('No report to download');
        return;
    }

    try {
        const response = await fetch('/export/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ report_id: currentReportId })
        });

        if (!response.ok) {
            showError('Download failed');
            return;
        }

        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${currentReportId}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        const successDiv = document.getElementById('exportSuccess');
        successDiv.textContent = 'Report downloaded!';
        successDiv.classList.remove('hidden');
        setTimeout(() => successDiv.classList.add('hidden'), 3000);

    } catch (error) {
        showError('Download failed');
    }
});

// Ask question
document.getElementById('askBtn').addEventListener('click', askQuestion);
document.getElementById('questionInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') askQuestion();
});

// Q&A Functions
async function loadQuestions(reportId) {
    try {
        const response = await fetch(`/api/questions/${reportId}`);
        if (!response.ok) throw new Error('Failed to load questions');

        const questions = await response.json();
        renderQuestions(questions);

    } catch (error) {
        console.error('Error loading questions:', error);
    }
}

function renderQuestions(questions) {
    const logContainer = document.getElementById('qaHistoryLog');
    const emptyState = document.getElementById('qaEmptyState');

    // Clear log but keep empty state hidden initially
    logContainer.innerHTML = '';

    if (questions.length === 0) {
        logContainer.appendChild(emptyState);
        emptyState.classList.remove('hidden');
        return;
    }

    questions.forEach(q => {
        const entryHtml = `
            <div class="border-b border-gray-100 pb-6 last:border-0 last:pb-0 animate-fade-in">
                <div class="font-semibold text-gray-800 text-sm mb-2">
                    ${q.question}
                </div>
                <div class="text-gray-600 text-sm leading-relaxed bg-white pl-4 border-l-2 border-slate-200">
                    ${q.answer}
                </div>
                <div class="mt-2 text-xs text-gray-400">
                    Asked at: ${new Date(q.created_at).toLocaleString()}
                </div>
            </div>
        `;
        logContainer.insertAdjacentHTML('beforeend', entryHtml);
    });

    // Scroll to bottom
    logContainer.scrollTop = logContainer.scrollHeight;
}

async function askQuestion() {
    const input = document.getElementById('questionInput');
    const btn = document.getElementById('askBtn');
    const loading = document.getElementById('qaLoading');
    const question = input.value.trim();

    if (!question) return;
    if (question.length < 3) {
        showError('Question must be at least 3 characters');
        return;
    }

    // Reset UI
    showError('', true); // Clear errors
    btn.disabled = true;
    loading.classList.remove('hidden');

    try {
        const response = await fetch(`/api/questions/${currentReportId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get answer');
        }

        // Add new question to list immediately
        input.value = '';

        // Reload all questions to ensure sync and correct order
        await loadQuestions(currentReportId);

    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        loading.classList.add('hidden');
        input.focus();
    }
}

// Load reports
async function loadReports() {
    try {
        const response = await fetch('/reports');
        const data = await response.json();

        if (!response.ok) return;

        const reportsList = document.getElementById('reportsList');

        if (!data.reports || data.reports.length === 0) {
            reportsList.innerHTML = '<p class="text-sm text-gray-400 text-center py-4">No reports yet</p>';
            return;
        }

        reportsList.innerHTML = '';

        data.reports.slice(0, 5).forEach(report => {
            const div = document.createElement('div');
            div.className = 'p-3 border border-gray-200 rounded hover:border-slate-400 hover:bg-slate-50 cursor-pointer transition';
            div.onclick = () => loadReport(report.id);

            const date = new Date(report.created_at).toLocaleString();

            div.innerHTML = `
                <p class="text-sm font-medium text-gray-800 truncate">${report.filename}</p>
                <p class="text-xs text-gray-500 mt-1">${date}</p>
            `;

            reportsList.appendChild(div);
        });

    } catch (error) {
        //  Silent fail on reports list
    }
}

async function loadReport(reportId) {
    try {
        const response = await fetch(`/reports/${reportId}`);
        const data = await response.json();

        if (!response.ok) {
            showError('Failed to load report');
            return;
        }

        const report = data.report;
        currentReportId = report.id;
        currentSummary = JSON.parse(report.summary_data);
        currentInsights = report.insights_json;

        // Display summary and preview
        displaySummary(currentSummary);
        displayPreview(currentSummary);

        // Display charts
        displayCharts(report.chart_data);

        // Display insights
        document.getElementById('insightsPanel').classList.remove('hidden');
        document.getElementById('generateBtn').classList.add('hidden');
        displayStructuredInsights(currentInsights);
        document.getElementById('insightsContent').classList.remove('hidden');

        // Show panels
        document.getElementById('exportPanel').classList.remove('hidden');
        document.getElementById('questionPanel').classList.remove('hidden');

        // Update file info
        document.getElementById('fileName').textContent = report.filename;
        document.getElementById('fileInfo').classList.remove('hidden');

        showSuccess(`Loaded report: ${report.filename}`, false);
        activateStep(4);

    } catch (error) {
        showError('Failed to load report');
    }
}

// Utility functions
function showError(message, hide = false) {
    const errorEl = document.getElementById('errorMsg');
    if (hide) {
        errorEl.classList.add('hidden');
        return;
    }
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');

    // Hide success and warning messages when showing error
    document.getElementById('successMsg').classList.add('hidden');
    document.getElementById('warningMsg').classList.add('hidden');
}

function showSuccess(message, hide = false) {
    const successEl = document.getElementById('successMsg');
    if (hide) {
        successEl.classList.add('hidden');
        return;
    }
    successEl.textContent = message;
    successEl.classList.remove('hidden');

    // Hide error and warning messages when showing success
    document.getElementById('errorMsg').classList.add('hidden');
    // Don't hide warning here as we might want to show "Success" AND "Warning" together
}

function showWarning(message, hide = false) {
    const warningEl = document.getElementById('warningMsg');
    if (hide) {
        warningEl.classList.add('hidden');
        return;
    }
    warningEl.textContent = message;
    warningEl.classList.remove('hidden');
}

// Load reports on page load
window.addEventListener('DOMContentLoaded', () => {
    loadReports();
    activateStep(1);
});

// Drag and drop
const dropzone = document.getElementById('dropzone');

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-slate-400', 'bg-slate-50');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-slate-400', 'bg-slate-50');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-slate-400', 'bg-slate-50');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        document.getElementById('fileInput').files = files;
        handleFileSelect({ target: { files: files } });
    }
});
