/**
 * Gemini-Powered Real-time News and Notifications
 * AutoFINE System
 */

class GeminiNewsWidget {
    constructor() {
        this.newsContainer = null;
        this.updateInterval = 300000; // 5 minutes
        this.init();
    }

    init() {
        // Create news widget container
        this.createNewsWidget();
        
        // Load initial news
        this.loadNews();
        
        // Set up auto-refresh
        setInterval(() => this.loadNews(), this.updateInterval);
    }

    createNewsWidget() {
        // Create floating news button
        const newsButton = document.createElement('button');
        newsButton.id = 'news-button';
        newsButton.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
        newsButton.style.cssText = 'width: 60px; height: 60px; z-index: 1000; box-shadow: 0 4px 15px rgba(0,0,0,0.3);';
        newsButton.innerHTML = '<i class="bi bi-newspaper"></i>';
        newsButton.title = 'Traffic News & Updates';
        newsButton.onclick = () => this.showNewsModal();
        document.body.appendChild(newsButton);

        // Create news modal
        const modal = document.createElement('div');
        modal.id = 'news-modal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content card-professional">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="bi bi-newspaper"></i> Real-time Traffic News</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="news-content">
                        <div class="text-center">
                            <div class="spinner-professional"></div>
                            <p>Loading latest traffic updates...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async loadNews() {
        try {
            const response = await fetch('/api/gemini/news');
            const news = await response.json();
            
            this.displayNews(news);
            this.showNewsPopup(news);
        } catch (error) {
            console.error('Error loading news:', error);
        }
    }

    displayNews(news) {
        const content = document.getElementById('news-content');
        if (!content) return;

        const newsCard = `
            <div class="card-professional mb-3">
                <div class="card-header">
                    <h6 class="mb-0">
                        <i class="bi bi-info-circle text-primary"></i> ${news.title || 'Traffic Update'}
                        <span class="badge-professional badge-professional-${news.type || 'info'} float-end">${news.type || 'Info'}</span>
                    </h6>
                </div>
                <div class="card-body">
                    <p>${news.content || 'No updates available.'}</p>
                    <small class="text-muted">
                        <i class="bi bi-clock"></i> ${new Date(news.timestamp || Date.now()).toLocaleString()}
                    </small>
                </div>
            </div>
        `;
        
        content.innerHTML = newsCard;
    }

    showNewsPopup(news) {
        // Show small popup notification
        const popup = document.createElement('div');
        popup.className = `alert-professional alert-professional-${news.type || 'info'} position-fixed top-0 start-50 translate-middle-x mt-3`;
        popup.style.cssText = 'min-width: 300px; max-width: 500px; z-index: 9999; animation: slideDown 0.3s ease;';
        popup.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-newspaper me-2"></i>
                <div class="flex-grow-1">
                    <strong>${news.title || 'Traffic Update'}</strong>
                    <p class="mb-0 small">${(news.content || '').substring(0, 100)}...</p>
                </div>
                <button type="button" class="btn-close ms-2" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (popup.parentElement) {
                popup.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => popup.remove(), 300);
            }
        }, 10000);
    }

    showNewsModal() {
        const modal = new bootstrap.Modal(document.getElementById('news-modal'));
        modal.show();
        this.loadNews(); // Refresh news when modal opens
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    new GeminiNewsWidget();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
    
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
    
    #news-button:hover {
        transform: scale(1.1);
        transition: transform 0.2s;
    }
`;
document.head.appendChild(style);
