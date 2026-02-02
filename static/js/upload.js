// Upload page functionality
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const uploadActions = document.getElementById('uploadActions');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

let selectedFiles = [];

// Drag and drop handlers
uploadZone.addEventListener('click', () => {
    fileInput.click();
});

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
    addFiles(files);
});

// File input change
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    addFiles(files);
});

function addFiles(files) {
    // Filter for PDFs only
    const pdfFiles = files.filter(f => f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf'));
    
    if (pdfFiles.length === 0) {
        showModal('Error', 'Please select only PDF files.');
        return;
    }
    
    // Add to selected files
    pdfFiles.forEach(file => {
        // Check if file already exists
        if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    });
    
    updateFileList();
}

function updateFileList() {
    fileList.innerHTML = '';
    
    if (selectedFiles.length === 0) {
        uploadActions.style.display = 'none';
        return;
    }
    
    uploadActions.style.display = 'flex';
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <span class="file-icon">📄</span>
                <div>
                    <div class="file-name">${escapeHtml(file.name)}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
            </div>
            <button class="file-remove" data-index="${index}">✕</button>
        `;
        
        fileList.appendChild(fileItem);
    });
    
    // Add remove handlers
    document.querySelectorAll('.file-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.dataset.index);
            selectedFiles.splice(index, 1);
            updateFileList();
        });
    });
}

// Clear all files
clearBtn.addEventListener('click', () => {
    selectedFiles = [];
    fileInput.value = '';
    updateFileList();
});

// Upload files
uploadBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) {
        showModal('Error', 'Please select at least one PDF file.');
        return;
    }
    
    uploadBtn.disabled = true;
    clearBtn.disabled = true;
    uploadProgress.style.display = 'block';
    
    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files[]', file);
        });
        
        progressText.textContent = 'Uploading files...';
        progressFill.style.width = '50%';
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        progressFill.style.width = '100%';
        
        const data = await response.json();
        
        if (data.success) {
            progressText.textContent = 'Upload complete! Redirecting...';
            
            // Show any errors
            if (data.errors && data.errors.length > 0) {
                console.warn('Upload warnings:', data.errors);
            }
            
            // Redirect to editor
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 500);
        } else {
            throw new Error(data.error || 'Upload failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showModal('Upload Error', error.message || 'An error occurred during upload.');
        uploadBtn.disabled = false;
        clearBtn.disabled = false;
        uploadProgress.style.display = 'none';
        progressFill.style.width = '0%';
    }
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
