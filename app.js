if (localStorage.getItem('isLoggedIn') !== 'true') {
    window.location.href = 'login.html';
}

const userEmail = localStorage.getItem('username');
document.getElementById('userEmail').textContent = userEmail;

document.getElementById('logoutBtn').addEventListener('click', function() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('username');
    window.location.href = 'login.html';
});

function loadFeedback() {
    const feedbackList = document.getElementById('feedbackList');
    const feedbacks = JSON.parse(localStorage.getItem('feedbacks')) || [];
    
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
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('feedbackForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const courseName = document.getElementById('courseName').value;
    const rating = document.getElementById('rating').value;
    const comments = document.getElementById('comments').value;
    
    const feedback = {
        courseName: courseName,
        rating: rating,
        comments: comments,
        date: new Date().toLocaleString()
    };
    
    const feedbacks = JSON.parse(localStorage.getItem('feedbacks')) || [];
    feedbacks.unshift(feedback);
    localStorage.setItem('feedbacks', JSON.stringify(feedbacks));
    
    document.getElementById('feedbackForm').reset();
    
    loadFeedback();
    
    showNotification('Feedback submitted successfully!');
});

document.getElementById('clearBtn').addEventListener('click', function() {
    if (confirm('Are you sure you want to clear all feedback? This action cannot be undone.')) {
        localStorage.removeItem('feedbacks');
        loadFeedback();
        showNotification('All feedback cleared!');
    }
});

function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4caf50;
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

loadFeedback();
