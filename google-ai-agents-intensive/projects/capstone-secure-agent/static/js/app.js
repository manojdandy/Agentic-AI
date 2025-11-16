// Global state
let requestInProgress = false;
let lastPanelWidth = null;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loading = document.getElementById('loading');
const statsPanel = document.querySelector('.stats-panel');
const container = document.querySelector('.container');

// Add message to chat
function addMessage(text, type = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // CRITICAL: Force scroll to bottom
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
        chatMessages.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    });
}

// Send message to API
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || requestInProgress) return;
    
    requestInProgress = true;
    
    // Disable UI
    messageInput.disabled = true;
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';
    
    // Add user message
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show loading
    loading.classList.add('active');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                session_id: 'default'
            })
        });
        
        const data = await response.json();
        
        // Hide loading
        loading.classList.remove('active');
        
        if (data.blocked) {
            addMessage(`🛡️ Request Blocked\n\nReason: ${data.reason}\nRisk: ${data.risk_level}`, 'blocked');
        } else {
            addMessage(data.response, 'assistant');
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
        loading.classList.remove('active');
        
        if (error.message.includes('rate limit')) {
            addMessage('⏱️ Rate limit reached. Please wait 60 seconds.', 'blocked');
        } else {
            addMessage('❌ Error: Could not connect to server', 'blocked');
        }
    } finally {
        // Re-enable UI
        requestInProgress = false;
        messageInput.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
        messageInput.focus();
        
        // Update stats (non-blocking)
        setTimeout(updateStats, 0);
    }
}

// Update statistics
async function updateStats() {
    try {
        const [statsRes, metricsRes] = await Promise.all([
            fetch('/api/stats', { 
                signal: AbortSignal.timeout(3000) 
            }).catch(e => null),
            fetch('/api/metrics', { 
                signal: AbortSignal.timeout(3000) 
            }).catch(e => null)
        ]);
        
        if (statsRes?.ok) {
            const stats = await statsRes.json();
            document.getElementById('totalRequests').textContent = stats.total_requests || 0;
            document.getElementById('successRate').textContent = `${stats.success_rate || 100}%`;
            document.getElementById('successCount').textContent = `${stats.successful_requests || 0} successful`;
        }
        
        if (metricsRes?.ok) {
            const metrics = await metricsRes.json();
            document.getElementById('blockedCount').textContent = metrics.total_blocked || 0;
            document.getElementById('blockRate').textContent = `${metrics.block_rate || 0}% block rate`;
            document.getElementById('avgLatency').textContent = `${Math.round(metrics.avg_latency * 1000) || 0}ms`;
        }
        
    } catch (error) {
        console.warn('Failed to update stats:', error);
    }
}

// Force stats panel visible
function forceStatsPanelVisible() {
    if (!statsPanel) return;
    
    statsPanel.style.display = 'block';
    statsPanel.style.visibility = 'visible';
    statsPanel.style.opacity = '1';
    statsPanel.style.width = '300px';
    statsPanel.style.minWidth = '300px';
    statsPanel.style.maxWidth = '300px';
    statsPanel.style.flexShrink = '0';
    statsPanel.style.transition = 'none';
    statsPanel.style.top = '0';
    statsPanel.style.position = 'relative';
    
    if (container) {
        container.style.gridTemplateColumns = '1fr 300px';
        container.style.display = 'grid';
    }
}

// Monitor panel width
function monitorPanelWidth() {
    if (!statsPanel) return;
    
    const rect = statsPanel.getBoundingClientRect();
    const currentWidth = Math.round(rect.width);
    
    if (lastPanelWidth !== null && Math.abs(currentWidth - lastPanelWidth) > 10) {
        console.log(`📏 Panel width changed: ${lastPanelWidth}px → ${currentWidth}px`);
        forceStatsPanelVisible();
    }
    
    lastPanelWidth = currentWidth;
}

// Monitor panel position
function monitorPanelPosition() {
    if (!statsPanel) return;
    
    const rect = statsPanel.getBoundingClientRect();
    
    // If panel moved up too much, scroll it back
    if (rect.top < -50) {
        statsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Prevent body/container scroll
function preventScroll(e) {
    if (e.target === document.body || e.target === container) {
        e.preventDefault();
        e.stopPropagation();
        if (document.body.scrollTop !== 0) document.body.scrollTop = 0;
        if (container?.scrollTop !== 0) container.scrollTop = 0;
    }
}

// Force enable chatbox (watchdog)
function checkChatboxHealth() {
    if (!requestInProgress) {
        if (messageInput.disabled || sendButton.disabled) {
            console.log('🔧 Auto-enabling chatbox');
            messageInput.disabled = false;
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
        }
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !messageInput.disabled && !sendButton.disabled) {
        sendMessage();
    }
});

// Click anywhere to force-enable
document.addEventListener('click', () => {
    if (!requestInProgress) {
        messageInput.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
    }
    forceStatsPanelVisible();
});

// Keypress to force-enable
document.addEventListener('keypress', () => {
    if (!requestInProgress) {
        messageInput.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
    }
});

// Prevent unwanted scrolling
document.body.addEventListener('scroll', preventScroll, { passive: false });
container?.addEventListener('scroll', preventScroll, { passive: false });

// Initialize on load
window.addEventListener('load', () => {
    messageInput.disabled = false;
    sendButton.disabled = false;
    sendButton.textContent = 'Send';
    messageInput.focus();
    
    forceStatsPanelVisible();
    updateStats();
});

// Re-enable on visibility change
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        messageInput.disabled = false;
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
        forceStatsPanelVisible();
        updateStats();
    }
});

// Watchdogs
setInterval(forceStatsPanelVisible, 5000);
setInterval(monitorPanelWidth, 1000);
setInterval(monitorPanelPosition, 1000);
setInterval(checkChatboxHealth, 500);
setInterval(updateStats, 10000);

console.log('✅ Secure AI Agent UI loaded');



