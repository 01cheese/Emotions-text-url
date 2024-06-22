const fileInput = document.getElementById('file-upload');
const uploadSection = document.getElementById('upload-section');
const urlInput = document.getElementById('url-input');
const analyzeUrlBtn = document.getElementById('analyze-url-btn');
const loadingIndicator = document.getElementById('loading');
const notification = document.getElementById('notification');
const fileNameDisplay = document.getElementById('file-name');
let charts = {};

uploadSection.addEventListener('click', () => fileInput.click());

uploadSection.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadSection.classList.add('dragover');
});

uploadSection.addEventListener('dragleave', () => {
    uploadSection.classList.remove('dragover');
});

uploadSection.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadSection.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', () => handleFiles(fileInput.files));

analyzeUrlBtn.addEventListener('click', () => {
    const url = urlInput.value;
    if (url) {
        analyzeUrl(url);
    }
});

function handleFiles(files) {
    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    showLoading();
    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            showError(data.error);
        } else {
            updateCharts(data.average_scores, data.positions);
            displayFileName(file.name);
        }
    }).catch(error => {
        hideLoading();
        console.error('Error:', error);
        // showError('An error occurred while processing the file.');
    });
}

function analyzeUrl(url) {
    showLoading();
    fetch('/analyze_url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
    }).then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.error) {
            showError(data.error);
        } else {
            updateCharts(data.average_scores, data.positions);
            displayFileName(url);
        }
    }).catch(error => {
        hideLoading();
        console.error('Error:', error);
        // showError('An error occurred while processing the URL.');
    });
}

function updateCharts(averageScores, positions) {
    updateChart('joy-chart', 'Joy', averageScores.joy);
    updateChart('surprise-chart', 'Surprise', averageScores.surprise);
    updateChart('sadness-chart', 'Sadness', averageScores.sadness);
    updateChart('disgust-chart', 'Disgust', averageScores.disgust);
    updateChart('anger-chart', 'Anger', averageScores.anger);
    updateChart('fear-chart', 'Fear', averageScores.fear);
    updateChart('neutral-chart', 'Neutral', averageScores.neutral);
    updateAllEmotionsChart(averageScores);
    updatePositionChart(positions);
}

function updateAllEmotionsChart(averageScores) {
    const ctx = document.getElementById('all-emotions-chart').getContext('2d');

    if (charts['all-emotions-chart']) {
        charts['all-emotions-chart'].destroy();
    }

    charts['all-emotions-chart'] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Joy', 'Surprise', 'Sadness', 'Disgust', 'Anger', 'Fear', 'Neutral'],
            datasets: [{
                data: [
                    averageScores.joy * 100 || 0,
                    averageScores.surprise * 100 || 0,
                    averageScores.sadness * 100 || 0,
                    averageScores.disgust * 100 || 0,
                    averageScores.anger * 100 || 0,
                    averageScores.fear * 100 || 0,
                    averageScores.neutral * 100 || 0
                ],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#FF9F40',
                    '#FF6384',
                    '#4BC0C0',
                    '#9966FF'
                ],
                hoverBackgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#FF9F40',
                    '#FF6384',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.raw !== null) {
                                label += context.raw.toFixed(2) + '%';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function updateChart(chartId, label, score) {
    const ctx = document.getElementById(chartId).getContext('2d');

    if (charts[chartId]) {
        charts[chartId].destroy();
    }

    let data, backgroundColor, hoverBackgroundColor, labels;
    if (score !== undefined) {
        data = [score * 100, 100 - score * 100];
        backgroundColor = ['#FF6384', '#36A2EB'];
        hoverBackgroundColor = ['#FF6384', '#36A2EB'];
        labels = [label, 'Other'];
    } else {
        data = [100];
        backgroundColor = ['#36A2EB'];
        hoverBackgroundColor = ['#36A2EB'];
        labels = ['None'];
    }

    charts[chartId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColor,
                hoverBackgroundColor: hoverBackgroundColor
            }]
        },
        options: {
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
}

function updatePositionChart(positions) {
    const ctx = document.getElementById('positions-chart').getContext('2d');

    if (charts['positions-chart']) {
        charts['positions-chart'].destroy();
    }

    const datasets = [];
    Object.keys(positions).forEach(emotion => {
        datasets.push({
            label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
            data: positions[emotion],
            fill: false,
            borderColor: getColorForEmotion(emotion),
            tension: 0.1
        });
    });

    charts['positions-chart'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: Math.max(...Object.values(positions).flat()) + 1}, (_, i) => i),
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Position in text'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Emotions'
                    }
                }
            }
        }
    });
}

function getColorForEmotion(emotion) {
    const colors = {
        joy: '#FFCE56',
        surprise: '#36A2EB',
        sadness: '#FF6384',
        disgust: '#FF9F40',
        anger: '#FF6384',
        fear: '#4BC0C0',
        neutral: '#9966FF'
    };
    return colors[emotion] || '#000000';
}

function showLoading() {
    loadingIndicator.style.display = 'block';
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

function showError(message) {
    notification.innerText = message;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

function displayFileName(name) {
    fileNameDisplay.innerText = `File/URL: ${name}`;
}
