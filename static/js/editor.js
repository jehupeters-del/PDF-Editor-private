// Editor page functionality
const pageGrid = document.getElementById('pageGrid');
const pageCount = document.getElementById('pageCount');
const selectionInfo = document.getElementById('selectionInfo');
const selectedCount = document.getElementById('selectedCount');
const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
const validateBtn = document.getElementById('validateBtn');
const extractBtn = document.getElementById('extractBtn');
const downloadBtn = document.getElementById('downloadBtn');

let selectedPages = new Set();

// Initialize page event listeners
function initializePageCards() {
    // Individual delete buttons
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const pageId = btn.dataset.pageId;
            await deletePage(pageId);
        });
    });
    
    // Checkbox selection
    document.querySelectorAll('.page-select').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const pageId = checkbox.dataset.pageId;
            const card = checkbox.closest('.page-card');
            
            if (checkbox.checked) {
                selectedPages.add(pageId);
                card.classList.add('selected');
            } else {
                selectedPages.delete(pageId);
                card.classList.remove('selected');
            }
            
            updateSelectionInfo();
        });
    });
    
    // Card click for selection (toggle)
    document.querySelectorAll('.page-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // Don't toggle if clicking button or checkbox
            if (e.target.closest('.btn-delete') || e.target.closest('.page-select')) {
                return;
            }
            
            const checkbox = card.querySelector('.page-select');
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event('change'));
        });
    });
}

// Delete a single page
async function deletePage(pageId) {
    if (!confirm('Are you sure you want to remove this page?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete_page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ page_id: pageId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Remove the card from DOM
            const card = document.querySelector(`[data-page-id="${pageId}"]`);
            if (card) {
                card.remove();
            }
            
            // Remove from selected pages
            selectedPages.delete(pageId);
            
            // Update counts
            pageCount.textContent = data.remaining_pages;
            updateSelectionInfo();
            
            // Reload if no pages left
            if (data.remaining_pages === 0) {
                window.location.reload();
            }
        } else {
            throw new Error(data.error || 'Failed to delete page');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showModal('Error', 'Failed to delete page: ' + error.message);
    }
}

// Delete selected pages
deleteSelectedBtn.addEventListener('click', async () => {
    if (selectedPages.size === 0) {
        return;
    }
    
    if (!confirm(`Are you sure you want to remove ${selectedPages.size} page(s)?`)) {
        return;
    }
    
    const pagesToDelete = Array.from(selectedPages);
    let successCount = 0;
    let errorCount = 0;
    
    deleteSelectedBtn.disabled = true;
    deleteSelectedBtn.textContent = 'Deleting...';
    
    for (const pageId of pagesToDelete) {
        try {
            const response = await fetch('/api/delete_page', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ page_id: pageId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const card = document.querySelector(`[data-page-id="${pageId}"]`);
                if (card) {
                    card.remove();
                }
                successCount++;
                
                // Update page count
                pageCount.textContent = data.remaining_pages;
            } else {
                errorCount++;
            }
        } catch (error) {
            console.error('Delete error:', error);
            errorCount++;
        }
    }
    
    // Clear selection
    selectedPages.clear();
    updateSelectionInfo();
    
    deleteSelectedBtn.disabled = false;
    deleteSelectedBtn.textContent = 'Delete Selected';
    
    // Show result
    if (errorCount > 0) {
        showModal('Deletion Complete', `Deleted ${successCount} page(s). ${errorCount} failed.`);
    }
    
    // Reload if no pages left
    const remaining = parseInt(pageCount.textContent);
    if (remaining === 0) {
        window.location.reload();
    }
});

// Update selection info display
function updateSelectionInfo() {
    if (selectedPages.size > 0) {
        selectionInfo.style.display = 'flex';
        selectedCount.textContent = selectedPages.size;
    } else {
        selectionInfo.style.display = 'none';
    }
}

// Validate questions
validateBtn.addEventListener('click', async () => {
    validateBtn.disabled = true;
    validateBtn.textContent = '⏳ Validating...';
    
    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            let message = '';
            
            if (data.is_valid) {
                message = `<div style="color: #10b981; font-weight: bold; font-size: 18px; margin-bottom: 16px;">✓ Validation Passed</div>`;
                message += `<p>All questions from 1 to ${data.max_question} are present.</p>`;
                message += `<p>Total pages: ${data.total_pages}</p>`;
            } else {
                message = `<div style="color: #ef4444; font-weight: bold; font-size: 18px; margin-bottom: 16px;">✗ Validation Failed</div>`;
                message += `<p>Missing questions: <strong>${data.missing_questions.join(', ')}</strong></p>`;
                message += `<p>Expected questions: 1 to ${data.max_question}</p>`;
                message += `<p>Total pages: ${data.total_pages}</p>`;
            }
            
            showModal('Question Validation', message, true);
        } else {
            throw new Error(data.error || 'Validation failed');
        }
    } catch (error) {
        console.error('Validation error:', error);
        showModal('Error', 'Validation failed: ' + error.message);
    } finally {
        validateBtn.disabled = false;
        validateBtn.textContent = '✓ Validate Questions';
    }
});

// Extract questions
extractBtn.addEventListener('click', async () => {
    extractBtn.disabled = true;
    extractBtn.textContent = '⏳ Extracting...';
    
    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            let message = `<pre>${escapeHtml(data.report)}</pre>`;
            message += `<div style="margin-top: 16px;">`;
            message += `<p><em>Note: This is a preview. The actual extraction happens during download.</em></p>`;
            message += `</div>`;
            
            showModal('Question Extraction Report', message, true);
        } else {
            throw new Error(data.error || 'Extraction failed');
        }
    } catch (error) {
        console.error('Extraction error:', error);
        showModal('Error', 'Extraction failed: ' + error.message);
    } finally {
        extractBtn.disabled = false;
        extractBtn.textContent = '📤 Extract Questions';
    }
});

// Download merged PDF
downloadBtn.addEventListener('click', () => {
    downloadBtn.disabled = true;
    downloadBtn.textContent = '⏳ Preparing...';
    
    // Trigger download
    window.location.href = '/download';
    
    // Re-enable button after a delay
    setTimeout(() => {
        downloadBtn.disabled = false;
        downloadBtn.textContent = '📥 Download Merged PDF';
    }, 2000);
});

// Utility function
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
initializePageCards();
