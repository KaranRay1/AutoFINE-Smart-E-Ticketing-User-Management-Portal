/**
 * Real-time Updates using Server-Sent Events (SSE)
 * AutoFINE System
 */

class RealtimeUpdater {
    constructor(options = {}) {
        this.url = options.url || '/api/realtime/challans';
        this.eventSource = null;
        this.callbacks = {
            onUpdate: options.onUpdate || null,
            onError: options.onError || null,
            onConnect: options.onConnect || null
        };
        this.reconnecting = false;
        this.reconnectInterval = options.reconnectInterval || 3000;
    }

    connect() {
        if (this.eventSource) {
            this.disconnect();
        }

        this.eventSource = new EventSource(this.url);

        this.eventSource.onopen = () => {
            console.log('Real-time connection established');
            this.reconnecting = false;
            if (this.callbacks.onConnect) {
                this.callbacks.onConnect();
            }
            this.updateIndicator(true);
        };

        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'update') {
                    console.log('Real-time update received:', data);
                    if (this.callbacks.onUpdate) {
                        this.callbacks.onUpdate(data);
                    }
                    this.showNotification('New challan update received!');
                } else if (data.type === 'init') {
                    console.log('Initial state:', data);
                } else if (data.type === 'heartbeat') {
                    // Silent heartbeat to keep connection alive
                }
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            this.updateIndicator(false);
            
            if (this.eventSource.readyState === EventSource.CLOSED) {
                if (this.callbacks.onError) {
                    this.callbacks.onError(error);
                }
                
                // Attempt to reconnect
                if (!this.reconnecting) {
                    this.reconnecting = true;
                    setTimeout(() => this.connect(), this.reconnectInterval);
                }
            }
        };
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            this.updateIndicator(false);
        }
    }

    updateIndicator(connected) {
        const indicator = document.getElementById('realtime-indicator');
        if (indicator) {
            indicator.style.display = connected ? 'inline-flex' : 'none';
        }
    }

    showNotification(message) {
        // Create or update notification element
        let notification = document.getElementById('realtime-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'realtime-notification';
            notification.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 end-0 m-3';
            notification.style.zIndex = '9999';
            notification.innerHTML = `
                <strong>Live Update:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(notification);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (notification) {
                    notification.remove();
                }
            }, 5000);
        } else {
            notification.querySelector('strong').nextSibling.textContent = ` ${message}`;
        }
    }
}

// Vehicle-specific real-time updater
class VehicleRealtimeUpdater extends RealtimeUpdater {
    constructor(vehicleId, options = {}) {
        super({
            ...options,
            url: `/api/realtime/vehicle/${vehicleId}/challans`
        });
        this.vehicleId = vehicleId;
    }

    handleUpdate(data) {
        if (data.type === 'update' && data.challans) {
            // Update challan list in DOM
            const challanList = document.getElementById('challan-list');
            if (challanList) {
                this.updateChallanTable(data.challans);
            }
        }
    }

    updateChallanTable(challans) {
        const tbody = document.querySelector('#challan-list tbody');
        if (!tbody) return;

        tbody.innerHTML = challans.map(challan => `
            <tr class="animate-fade-in">
                <td>#${challan.id}</td>
                <td>${challan.violation_type}</td>
                <td>${challan.location || 'N/A'}</td>
                <td><strong>₹${challan.fine_amount}</strong></td>
                <td>${challan.due_date ? new Date(challan.due_date).toLocaleDateString() : 'N/A'}</td>
                <td>
                    <span class="badge ${challan.status === 'Paid' ? 'badge-success' : 'badge-danger'}">
                        ${challan.status}
                    </span>
                </td>
                <td>${new Date(challan.created_at).toLocaleString()}</td>
            </tr>
        `).join('');
    }
}

// Initialize real-time updates on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page that needs real-time updates
    const pageType = document.body.getAttribute('data-page-type');
    
    if (pageType === 'owner-dashboard' || pageType === 'admin-dashboard') {
        const updater = new RealtimeUpdater({
            onUpdate: function(data) {
                // Refresh page data or update specific elements
                if (data.challans) {
                    updateChallanCounts(data);
                }
            },
            onConnect: function() {
                console.log('Connected to real-time updates');
            },
            onError: function(error) {
                console.error('Real-time connection error:', error);
            }
        });
        
        updater.connect();
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            updater.disconnect();
        });
    }
    
    // Vehicle detail page real-time updates
    const vehicleId = document.body.getAttribute('data-vehicle-id');
    if (vehicleId) {
        const vehicleUpdater = new VehicleRealtimeUpdater(vehicleId, {
            onUpdate: function(data) {
                if (data.challans) {
                    const vehicleUpdater = new VehicleRealtimeUpdater(vehicleId);
                    vehicleUpdater.handleUpdate(data);
                }
            }
        });
        
        vehicleUpdater.connect();
        
        window.addEventListener('beforeunload', () => {
            vehicleUpdater.disconnect();
        });
    }
});

// Helper function to update challan counts
function updateChallanCounts(data) {
    // Update statistics cards
    const totalChallans = document.getElementById('total-challans');
    const unpaidChallans = document.getElementById('unpaid-challans');
    
    if (totalChallans && data.count !== undefined) {
        totalChallans.textContent = data.count;
    }
    
    // Count unpaid challans
    if (data.challans && unpaidChallans) {
        const unpaidCount = data.challans.filter(c => c.status === 'Unpaid').length;
        unpaidChallans.textContent = unpaidCount;
    }
}

// Export for use in other scripts
window.RealtimeUpdater = RealtimeUpdater;
window.VehicleRealtimeUpdater = VehicleRealtimeUpdater;
