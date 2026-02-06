/**
 * Advanced Features: Point System, Appeals, Payment Plans, AI Chatbot
 * AutoFINE System
 */

// Point System
class PointSystem {
    static async getPoints(dlNumber) {
        try {
            const response = await fetch(`/api/driver-license/${dlNumber}/points`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching points:', error);
            return null;
        }
    }

    static displayPointsBadge(dlNumber) {
        this.getPoints(dlNumber).then(data => {
            if (data && data.points !== undefined) {
                const badge = document.createElement('span');
                badge.className = 'badge-professional badge-professional-warning ms-2';
                badge.innerHTML = `<i class="bi bi-star"></i> ${data.points} Points`;
                badge.title = `License Status: ${data.status}`;
                
                if (data.status === 'Suspended') {
                    badge.className = 'badge-professional badge-professional-danger ms-2';
                }
                
                const dlElement = document.querySelector(`[data-dl="${dlNumber}"]`);
                if (dlElement) {
                    dlElement.appendChild(badge);
                }
            }
        });
    }
}

// Virtual Court / Appeals
class AppealsSystem {
    static async createAppeal(challanId, reason) {
        try {
            const response = await fetch('/api/appeals', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({challan_id: challanId, reason: reason})
            });
            const data = await response.json();
            
            if (data.success) {
                // Show AI guidance
                this.showAppealGuidance(data.guidance);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error creating appeal:', error);
            return false;
        }
    }

    static showAppealModal(challanId) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'appeal-modal';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content card-professional">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="bi bi-gavel"></i> File Appeal</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="appeal-form">
                            <input type="hidden" name="challan_id" value="${challanId}">
                            <div class="mb-3">
                                <label class="form-label">Reason for Appeal</label>
                                <textarea class="form-control-professional" name="reason" rows="4" required 
                                    placeholder="Explain why you believe this challan should be waived..."></textarea>
                            </div>
                            <button type="submit" class="btn-professional btn-professional-primary">
                                <i class="bi bi-send"></i> Submit Appeal
                            </button>
                        </form>
                        <div id="appeal-guidance" class="mt-3" style="display: none;"></div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        document.getElementById('appeal-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const reason = formData.get('reason');
            
            const success = await this.createAppeal(challanId, reason);
            if (success) {
                bsModal.hide();
                modal.remove();
                showNotification('Appeal submitted successfully!', 'success');
            }
        };
    }

    static showAppealGuidance(guidance) {
        const guidanceDiv = document.getElementById('appeal-guidance');
        if (guidanceDiv) {
            guidanceDiv.style.display = 'block';
            guidanceDiv.innerHTML = `
                <div class="alert-professional alert-professional-info">
                    <h6><i class="bi bi-robot"></i> AI Guidance</h6>
                    <p>${guidance}</p>
                </div>
            `;
        }
    }
}

// Payment Plans
class PaymentPlans {
    static async createPlan(challanId, installments = 3) {
        try {
            const response = await fetch('/api/payment-plans', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    challan_id: challanId,
                    installment_count: installments
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating payment plan:', error);
            return null;
        }
    }

    static showPlanModal(challanId, fineAmount) {
        if (fineAmount < 5000) {
            showNotification('Payment plans available only for fines above ₹5000', 'warning');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'payment-plan-modal';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content card-professional">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="bi bi-calendar-check"></i> Create Payment Plan</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Total Amount: <strong>₹${fineAmount}</strong></p>
                        <div class="mb-3">
                            <label class="form-label">Number of Installments</label>
                            <select class="form-control-professional" id="installment-count">
                                <option value="3">3 Installments</option>
                                <option value="6">6 Installments</option>
                                <option value="12">12 Installments</option>
                            </select>
                        </div>
                        <button class="btn-professional btn-professional-primary" onclick="PaymentPlans.submitPlan(${challanId})">
                            <i class="bi bi-check"></i> Create Plan
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
    }

    static async submitPlan(challanId) {
        const installments = parseInt(document.getElementById('installment-count').value);
        const result = await this.createPlan(challanId, installments);
        
        if (result && result.success) {
            showNotification(`Payment plan created! Installment: ₹${(result.installment_amount || 0).toFixed(2)}`, 'success');
            document.getElementById('payment-plan-modal').querySelector('.btn-close').click();
            setTimeout(() => location.reload(), 1500);
        }
    }
}

// AI Chatbot
class AIChatbot {
    constructor() {
        this.chatContainer = null;
        this.init();
    }

    init() {
        // Create chatbot button
        const chatButton = document.createElement('button');
        chatButton.id = 'chatbot-button';
        chatButton.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
        chatButton.style.cssText = 'width: 60px; height: 60px; z-index: 1000; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 80px; backdrop-filter: blur(6px); background: rgba(13,110,253,0.9);';
        chatButton.innerHTML = '<i class="bi bi-chat-square-text"></i>';
        chatButton.title = 'AI Assistant';
        chatButton.onclick = () => this.toggleChat();
        document.body.appendChild(chatButton);

        // Create chat window
        this.createChatWindow();
    }

    createChatWindow() {
        const chatWindow = document.createElement('div');
        chatWindow.id = 'chatbot-window';
        chatWindow.className = 'position-fixed bottom-0 end-0 m-3';
        chatWindow.style.cssText = 'width: 360px; height: 520px; background: rgba(255,255,255,0.88); backdrop-filter: blur(10px); border: 1px solid var(--border-light); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); z-index: 1001; display: none; flex-direction: column;';
        chatWindow.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center" style="background: rgba(240,248,255,0.85); border-bottom: 1px solid var(--border-light);">
                <h6 class="mb-0"><i class="bi bi-person-lines-fill"></i> AI Assistant</h6>
                <button class="btn-close" onclick="document.getElementById('chatbot-window').style.display='none'"></button>
            </div>
            <div id="chat-messages" class="flex-grow-1 p-3" style="overflow-y: auto; max-height: 420px; background: rgba(255,255,255,0.6);"></div>
            <div class="card-footer" style="background: rgba(245,245,245,0.85); border-top: 1px solid var(--border-light);">
                <div class="input-group">
                    <input type="text" id="chat-input" class="form-control-professional" placeholder="Ask me anything...">
                    <button class="btn-professional btn-professional-primary" onclick="window.chatbot.sendMessage()">
                        <i class="bi bi-send"></i>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(chatWindow);
        this.chatContainer = document.getElementById('chat-messages');
    }

    toggleChat() {
        const window = document.getElementById('chatbot-window');
        window.style.display = window.style.display === 'none' ? 'flex' : 'none';
        
        if (window.style.display !== 'none') {
            this.addWelcomeMessage();
            document.getElementById('chat-input').focus();
        }
    }

    addWelcomeMessage() {
        this.addMessage('assistant', 'Hello! I can help you with traffic rules, challans, appeals, and more. How can I assist you?');
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.addMessage('user', message);
        input.value = '';
        
        // Show typing indicator
        const typingId = this.addMessage('assistant', 'Thinking...', true);
        
        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();
            
            // Add response
            this.addMessage('assistant', data.response || 'I apologize, but I could not process your request.');
        } catch (error) {
            document.getElementById(typingId).remove();
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        }
    }

    addMessage(role, text, isTyping = false) {
        const messageId = 'msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `mb-2 d-flex ${role === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
        
        const bubble = document.createElement('div');
        bubble.className = `p-2 rounded ${role === 'user' ? 'bg-primary text-white' : 'bg-secondary'}`;
        bubble.style.maxWidth = '80%';
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        
        return messageId;
    }
}

// Analytics Dashboard
class AnalyticsDashboard {
    static async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics/dashboard');
            const data = await response.json();
            this.displayAnalytics(data);
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    static displayAnalytics(data) {
        // Display violation statistics
        if (data.violations) {
            const violationsDiv = document.getElementById('violations-chart');
            if (violationsDiv) {
                violationsDiv.innerHTML = data.violations.map(v => `
                    <div class="d-flex justify-content-between mb-2">
                        <span>${v.type}</span>
                        <span class="badge-professional badge-professional-primary">${v.count}</span>
                    </div>
                `).join('');
            }
        }

        // Display hotspots
        if (data.hotspots) {
            const hotspotsDiv = document.getElementById('hotspots-list');
            if (hotspotsDiv) {
                hotspotsDiv.innerHTML = `
                    <div class="list-group">
                        ${data.hotspots.map(h => `
                            <div class="list-group-item d-flex justify-content-between align-items-center">
                                <div class="text-truncate" style="max-width: 80%;">
                                    <i class="bi bi-geo-alt"></i> ${h.location || 'Unknown'}
                                </div>
                                <span class="badge-professional badge-professional-warning">${h.count}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        }

        // Display predictive insights
        if (data.predictive_insights) {
            const insightsDiv = document.getElementById('predictive-insights');
            if (insightsDiv) {
                const p = data.predictive_insights || {};
                insightsDiv.innerHTML = this.renderInsightsCard('All India (AI)', p);
            }
        }

        // Initialize a default map view (admin dashboard only)
        if (document.body.getAttribute('data-page-type') === 'admin-dashboard') {
            this.initMapOnce();
            // Center map on Dehradun by default
            this.updateMap({ city: 'Dehradun', lat: 30.3165, lon: 78.0322 }, data.hotspots || [], data.predictive_insights || {});
        }
    }

    static renderInsightsCard(title, insights) {
        const hotspot = insights.hotspot || 'High traffic areas';
        const peak = insights.peak_time || 'Rush hours';
        const common = insights.common_violation || 'Traffic violations';
        const rec = insights.recommendation || 'Drive safely and follow rules';
        return `
            <div class="card-professional">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="card-title mb-0"><i class="bi bi-lightbulb"></i> ${title}</h6>
                        <span class="badge-professional badge-professional-info">AI</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="d-flex flex-wrap gap-2">
                        <span class="badge-professional badge-professional-primary">Hotspot: ${hotspot}</span>
                        <span class="badge-professional badge-professional-warning">Peak Time: ${peak}</span>
                        <span class="badge-professional badge-professional-danger">Common Violation: ${common}</span>
                        <span class="badge-professional badge-professional-success">Recommendation: ${rec}</span>
                    </div>
                </div>
            </div>
        `;
    }

    static initMapOnce() {
        if (this._mapInitialized) return;
        const mapEl = document.getElementById('city-traffic-map');
        if (!mapEl || typeof L === 'undefined') return;

        this._mapInitialized = true;
        this._map = L.map('city-traffic-map', { zoomControl: true }).setView([22.9734, 78.6569], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(this._map);
        this._markersLayer = L.layerGroup().addTo(this._map);
    }

    static updateMap(cityInfo, hotspots = [], insights = {}) {
        if (!this._mapInitialized || !this._map) return;
        const lat = cityInfo?.lat ?? 22.9734;
        const lon = cityInfo?.lon ?? 78.6569;
        const zoom = cityInfo?.lat ? 12 : 5;
        this._map.setView([lat, lon], zoom);

        this._markersLayer.clearLayers();
        // City marker
        if (cityInfo?.lat) {
            L.marker([lat, lon]).addTo(this._markersLayer).bindPopup(`<b>${cityInfo.city}</b>`);
        }

        // Demo hotspot markers near the city center (offset)
        hotspots.slice(0, 5).forEach((h, idx) => {
            const offLat = lat + ((Math.random() - 0.5) * 0.02);
            const offLon = lon + ((Math.random() - 0.5) * 0.02);
            L.circleMarker([offLat, offLon], {
                radius: 8,
                color: '#c62828',
                fillColor: '#c62828',
                fillOpacity: 0.5
            }).addTo(this._markersLayer).bindPopup(`<b>Hotspot</b><br>${h.location || 'Unknown'}<br>Count: ${h.count}`);
        });

        // Random markers for AI insights with distinct colors
        const info = {
            hotspot: insights.hotspot || 'High traffic areas',
            peak: insights.peak_time || 'Rush hours',
            common: insights.common_violation || 'Traffic violations',
            rec: insights.recommendation || 'Drive safely and follow rules'
        };
        const palette = { hotspot: '#c62828', peak: '#ff9800', common: '#1565c0', rec: '#2e7d32' };
        [
            { key: 'hotspot', label: 'Hotspot' },
            { key: 'peak', label: 'Peak Time' },
            { key: 'common', label: 'Common Violation' },
            { key: 'rec', label: 'Recommendation' }
        ].forEach(it => {
            const offLat = lat + ((Math.random() - 0.5) * 0.03);
            const offLon = lon + ((Math.random() - 0.5) * 0.03);
            const color = palette[it.key];
            L.circleMarker([offLat, offLon], {
                radius: 9,
                color: color,
                fillColor: color,
                fillOpacity: 0.5
            }).addTo(this._markersLayer).bindPopup(`<b>${it.label}</b><br>${info[it.key]}`);
        });
    }

    static async loadCityInsights() {
        const input = document.getElementById('city-insights-input');
        const city = (input?.value || '').trim();
        if (!city) {
            showNotification('Enter a city name first', 'warning');
            return;
        }
        await this._fetchAndRenderCityInsights(city);
    }

    static async useMyCity() {
        const input = document.getElementById('city-insights-input');
        if (input) input.value = 'Dehradun';
        await this._fetchAndRenderCityInsights('Dehradun');
    }

    static async _fetchAndRenderCityInsights(city) {
        const insightsDiv = document.getElementById('predictive-insights');
        if (insightsDiv) {
            insightsDiv.innerHTML = `<div class="text-center"><div class="spinner-professional"></div><p class="text-muted">Loading ${city} insights...</p></div>`;
        }
        try {
            const response = await fetch(`/api/predictive/city?city=${encodeURIComponent(city)}`);
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Failed to fetch city insights');
            }
            if (insightsDiv) {
                insightsDiv.innerHTML = this.renderInsightsCard(`${data.city} (AI)`, data.insights || {});
            }
            this.initMapOnce();
            this.updateMap(data.city_info, data.hotspots || [], data.insights || {});
        } catch (e) {
            if (insightsDiv) {
                insightsDiv.innerHTML = `<div class="alert alert-danger">Error: ${e.message}</div>`;
            }
        }
    }
}

// Helper function for notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert-professional alert-professional-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    notification.style.cssText = 'min-width: 300px; z-index: 9999; animation: slideDown 0.3s ease;';
    notification.innerHTML = `
        <strong>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</strong> ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// Initialize chatbot on page load
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new AIChatbot();
    
    // Load analytics if on admin dashboard
    if (document.body.getAttribute('data-page-type') === 'admin-dashboard') {
        AnalyticsDashboard.loadAnalytics();
    }
});

// Make functions globally available
window.PointSystem = PointSystem;
window.AppealsSystem = AppealsSystem;
window.PaymentPlans = PaymentPlans;
window.AnalyticsDashboard = AnalyticsDashboard;
window.showNotification = showNotification;
