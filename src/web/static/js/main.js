async function handleDraftAction(draftId, action) {
    const card = document.getElementById(`draft-${draftId}`);
    
    // Thêm hiệu ứng loading cho nút
    const buttons = card.querySelectorAll('button');
    buttons.forEach(b => b.disabled = true);
    
    try {
        const response = await fetch(`/api/drafts/${draftId}/${action}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Animate card removal
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                card.remove();
                
                // Check if grid is empty
                const grid = document.querySelector('.draft-grid');
                if (grid && grid.children.length === 0) {
                    location.reload(); // Tải lại để hiện empty state
                }
            }, 300);
        } else {
            alert('Lỗi: ' + data.detail);
            buttons.forEach(b => b.disabled = false);
        }
    } catch (error) {
        alert('Lỗi kết nối tới server.');
        buttons.forEach(b => b.disabled = false);
    }
}

function approveDraft(draftId) {
    handleDraftAction(draftId, 'approve');
}

function rejectDraft(draftId) {
    handleDraftAction(draftId, 'reject');
}

async function saveSettings(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Đang lưu...';
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            showToast();
        } else {
            const data = await response.json();
            alert('Lỗi: ' + (data.detail || 'Không xác định'));
        }
    } catch (error) {
        alert('Lỗi kết nối tới server.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

function showToast() {
    const toast = document.getElementById('toast-message');
    if (toast) {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

async function triggerManualJob(jobType, btnElement) {
    const originalText = btnElement.innerHTML;
    btnElement.disabled = true;
    btnElement.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Đang gửi lệnh...';
    
    try {
        const response = await fetch(`/api/trigger/${jobType}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const toast = document.getElementById('toast-message');
            if (toast) {
                toast.innerHTML = data.message;
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                    // Reload if crawling to fetch new drafts
                    if (jobType === 'crawl') {
                        location.reload();
                    }
                }, 3000);
            } else {
                alert(data.message);
                if (jobType === 'crawl') location.reload();
            }
        } else {
            alert('Lỗi: ' + (data.detail || 'Không xác định'));
        }
    } catch (error) {
        alert('Lỗi kết nối tới server.');
    } finally {
        setTimeout(() => {
            btnElement.disabled = false;
            btnElement.innerHTML = originalText;
        }, 1000);
    }
}
