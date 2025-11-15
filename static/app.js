async function checkAuth() {
    try {
        const response = await fetch('/api/check-auth', {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login.html';
            return null;
        }
        
        return data.email;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login.html';
        return null;
    }
}

async function init() {
    const email = await checkAuth();
    if (!email) return;
    
    document.getElementById('userEmail').textContent = email;
    loadFeedback();
}

document.getElementById('logoutBtn').addEventListener('click', async function() {
    try {
        await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout failed:', error);
        window.location.href = '/login.html';
    }
});

async function loadFeedback() {
    const feedbackList = document.getElementById('feedbackList');
    
    try {
        const response = await fetch('/api/feedback', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to load feedback');
        }
        
        const feedbacks = await response.json();
        
        if (feedbacks.length === 0) {
            feedbackList.innerHTML = '<div class="empty-state">No feedback submitted yet. Be the first to share your thoughts!</div>';
            return;
        }
        
        feedbackList.innerHTML = feedbacks.map(feedback => `
            <div class="feedback-item">
                <div class="feedback-course">${escapeHtml(feedback.courseName)}</div>
                <span class="feedback-rating">Rating: ${feedback.rating}/5</span>
                <div class="feedback-comments">${escapeHtml(feedback.comments)}</div>
                <div class="feedback-date">Submitted on ${feedback.date}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load feedback:', error);
        feedbackList.innerHTML = '<div class="empty-state">Failed to load feedback. Please try again.</div>';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('feedbackForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const courseName = document.getElementById('courseName').value.trim();
    const rating = document.getElementById('rating').value;
    const comments = document.getElementById('comments').value.trim();
    
    if (!courseName || !rating || !comments) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                courseName: courseName,
                rating: rating,
                comments: comments
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit feedback');
        }
        
        document.getElementById('feedbackForm').reset();
        await loadFeedback();
        showNotification('Feedback submitted successfully!');
    } catch (error) {
        console.error('Failed to submit feedback:', error);
        showNotification('Failed to submit feedback. Please try again.', 'error');
    }
});

document.getElementById('clearBtn').addEventListener('click', async function() {
    if (!confirm('Are you sure you want to clear all feedback? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/feedback/clear', {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear feedback');
        }
        
        await loadFeedback();
        showNotification('All feedback cleared!');
    } catch (error) {
        console.error('Failed to clear feedback:', error);
        showNotification('Failed to clear feedback. Please try again.', 'error');
    }
});

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.textContent = message;
    const bgColor = type === 'error' ? '#f44336' : '#4caf50';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

init();
