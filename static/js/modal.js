// Modal functionality
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const modalClose = document.querySelector('.modal-close');
const modalCloseBtn = document.getElementById('modal-close-btn');

function showModal(title, content, isHtml = false) {
    modalTitle.textContent = title;
    
    if (isHtml) {
        modalBody.innerHTML = content;
    } else {
        modalBody.textContent = content;
    }
    
    modal.classList.add('active');
}

function hideModal() {
    modal.classList.remove('active');
}

// Close modal on click
modalClose.onclick = hideModal;
modalCloseBtn.onclick = hideModal;

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target === modal) {
        hideModal();
    }
}

// Close on escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && modal.classList.contains('active')) {
        hideModal();
    }
});
