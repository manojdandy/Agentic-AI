"""
FastAPI Application for Secure AI Agent
Production-ready API with monitoring and metrics
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime

from src.agents.secure_orchestrator import SecureOrchestrator
from src.filters.context_protector import ProtectedContext
from src.monitoring.security_logger import SecurityLogger
from src.monitoring.metrics_collector import MetricsCollector

# Initialize FastAPI app
app = FastAPI(
    title="Secure AI Agent API",
    description="Production-ready AI agent with prompt injection protection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the secure orchestrator
protected_context = ProtectedContext(
    system_prompt="You are a helpful, safe, and secure AI assistant.",
    secret_keys=[],  # Add your keys here
    protected_phrases=["confidential", "internal system"]
)

orchestrator = SecureOrchestrator(
    protected_context=protected_context,
    enable_monitoring=True
)

# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1, max_length=5000)
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation context")

class ChatResponse(BaseModel):
    """Chat response model"""
    message: str = Field(..., description="AI response")
    blocked: bool = Field(..., description="Whether the request was blocked")
    risk_score: float = Field(..., description="Risk assessment score (0.0 to 1.0)")
    session_id: str = Field(..., description="Session ID")
    timestamp: str = Field(..., description="Response timestamp")
    security_alerts: List[str] = Field(default_factory=list, description="Security alerts if any")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str

class StatsResponse(BaseModel):
    """Statistics response"""
    total_requests: int
    successful_requests: int
    blocked_requests: int
    success_rate: float
    block_rate: float
    active_sessions: int

class MetricsResponse(BaseModel):
    """Metrics response"""
    total_requests: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_risk_score: float
    attacks_by_type: Dict[str, int]

class EventsResponse(BaseModel):
    """Security events response"""
    total_events: int
    events: List[Dict]


# Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web UI"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure AI Agent</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 1200px;
                display: grid;
                grid-template-columns: 1fr 300px;
                gap: 0;
                overflow: hidden;
                height: 80vh;
            }
            
            .chat-section {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 30px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .header h1 {
                font-size: 24px;
                font-weight: 600;
            }
            
            .status-badge {
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                background: #4ade80;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 30px;
                background: #f9fafb;
            }
            
            .message {
                margin-bottom: 20px;
                display: flex;
                gap: 10px;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 70%;
                padding: 15px 20px;
                border-radius: 15px;
                word-wrap: break-word;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message.assistant .message-content {
                background: white;
                color: #1f2937;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-bottom-left-radius: 5px;
            }
            
            .message.blocked .message-content {
                background: #fee2e2;
                color: #991b1b;
                border-left: 4px solid #dc2626;
            }
            
            .risk-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
                margin-left: 8px;
            }
            
            .risk-critical { background: #fee2e2; color: #991b1b; }
            .risk-high { background: #fed7aa; color: #9a3412; }
            .risk-medium { background: #fef3c7; color: #92400e; }
            .risk-low { background: #d1fae5; color: #065f46; }
            
            .chat-input-area {
                padding: 20px 30px;
                background: white;
                border-top: 1px solid #e5e7eb;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
            }
            
            #messageInput {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e5e7eb;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            #messageInput:focus {
                border-color: #667eea;
            }
            
            #sendButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
                transition: transform 0.2s;
            }
            
            #sendButton:hover {
                transform: scale(1.05);
            }
            
            #sendButton:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .stats-panel {
                background: #f9fafb;
                padding: 30px 20px;
                border-left: 1px solid #e5e7eb;
                overflow-y: auto;
            }
            
            .stats-title {
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 20px;
            }
            
            .stat-card {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            
            .stat-label {
                font-size: 12px;
                color: #6b7280;
                margin-bottom: 5px;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: 700;
                color: #1f2937;
            }
            
            .stat-subtext {
                font-size: 11px;
                color: #9ca3af;
                margin-top: 3px;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #6b7280;
            }
            
            .loading.active {
                display: block;
            }
            
            .spinner {
                border: 3px solid #f3f4f6;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @media (max-width: 768px) {
                .container {
                    grid-template-columns: 1fr;
                }
                .stats-panel {
                    display: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="chat-section">
                <div class="header">
                    <h1>🛡️ Secure AI Agent</h1>
                    <div class="status-badge">
                        <div class="status-dot"></div>
                        Online
                    </div>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant">
                        <div class="message-content">
                            👋 Hello! I'm a secure AI assistant with built-in prompt injection protection. 
                            Ask me anything, and I'll respond safely!
                        </div>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <div>Processing...</div>
                </div>
                
                <div class="chat-input-area">
                    <div class="input-group">
                        <input 
                            type="text" 
                            id="messageInput" 
                            placeholder="Type your message..."
                            autocomplete="off"
                        />
                        <button id="sendButton">Send</button>
                    </div>
                </div>
            </div>
            
            <div class="stats-panel">
                <div class="stats-title">📊 Live Statistics</div>
                
                <div class="stat-card">
                    <div class="stat-label">Total Requests</div>
                    <div class="stat-value" id="totalRequests">0</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Success Rate</div>
                    <div class="stat-value" id="successRate">100%</div>
                    <div class="stat-subtext" id="successCount">0 successful</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Attacks Blocked</div>
                    <div class="stat-value" id="blockedCount">0</div>
                    <div class="stat-subtext" id="blockRate">0% block rate</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Avg Response Time</div>
                    <div class="stat-value" id="avgLatency">0ms</div>
                </div>
            </div>
        </div>
        
        <script>
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const chatMessages = document.getElementById('chatMessages');
            const loading = document.getElementById('loading');
            
            let sessionId = 'session-' + Date.now();
            
            // Send message
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage('user', message);
                messageInput.value = '';
                sendButton.disabled = true;
                loading.classList.add('active');
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message, session_id: sessionId })
                    });
                    
                    const data = await response.json();
                    
                    // Add assistant response
                    addMessage(
                        data.blocked ? 'blocked' : 'assistant', 
                        data.message,
                        data.risk_score,
                        data.security_alerts
                    );
                    
                    // Update stats
                    updateStats();
                    
                } catch (error) {
                    addMessage('assistant', '❌ Error: ' + error.message);
                }
                
                loading.classList.remove('active');
                sendButton.disabled = false;
                messageInput.focus();
            }
            
            // Add message to chat
            function addMessage(type, content, riskScore, alerts) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                let badge = '';
                if (riskScore !== undefined && riskScore > 0) {
                    let riskClass = 'risk-low';
                    if (riskScore >= 0.9) riskClass = 'risk-critical';
                    else if (riskScore >= 0.7) riskClass = 'risk-high';
                    else if (riskScore >= 0.4) riskClass = 'risk-medium';
                    
                    badge = `<span class="risk-badge ${riskClass}">Risk: ${riskScore.toFixed(2)}</span>`;
                }
                
                messageDiv.innerHTML = `<div class="message-content">${content}${badge}</div>`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Update statistics
            async function updateStats() {
                try {
                    const [statsRes, metricsRes] = await Promise.all([
                        fetch('/api/stats'),
                        fetch('/api/metrics')
                    ]);
                    
                    const stats = await statsRes.json();
                    const metrics = await metricsRes.json();
                    
                    document.getElementById('totalRequests').textContent = stats.total_requests;
                    document.getElementById('successRate').textContent = stats.success_rate.toFixed(1) + '%';
                    document.getElementById('successCount').textContent = stats.successful_requests + ' successful';
                    document.getElementById('blockedCount').textContent = stats.blocked_requests;
                    document.getElementById('blockRate').textContent = stats.block_rate.toFixed(1) + '% block rate';
                    document.getElementById('avgLatency').textContent = metrics.avg_latency_ms.toFixed(1) + 'ms';
                    
                } catch (error) {
                    console.error('Failed to update stats:', error);
                }
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            // Initial stats update
            updateStats();
            
            // Update stats every 5 seconds
            setInterval(updateStats, 5000);
        </script>
    </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - main interaction with the secure AI agent
    
    This endpoint processes user messages through the secure pipeline:
    1. Input validation & normalization
    2. Attack detection
    3. AI response generation
    4. Output filtering
    5. Monitoring & logging
    """
    try:
        # Process through secure orchestrator
        response = orchestrator.handle_request(
            user_input=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            message=response.message,
            blocked=response.blocked,
            risk_score=response.risk_score,
            session_id=response.metadata.get('session_id', 'unknown'),
            timestamp=response.timestamp.isoformat(),
            security_alerts=response.security_alerts
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    stats = orchestrator.get_stats()
    
    return StatsResponse(
        total_requests=stats['total_requests'],
        successful_requests=stats['successful_requests'],
        blocked_requests=stats['blocked_inputs'] + stats['blocked_outputs'],
        success_rate=stats['success_rate'],
        block_rate=stats['block_rate'],
        active_sessions=stats['active_sessions']
    )


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get performance metrics"""
    if not orchestrator.enable_monitoring:
        raise HTTPException(status_code=503, detail="Monitoring not enabled")
    
    summary = orchestrator.metrics.get_summary()
    
    return MetricsResponse(
        total_requests=summary.total_requests,
        avg_latency_ms=summary.avg_latency_ms,
        p95_latency_ms=summary.p95_latency_ms,
        p99_latency_ms=summary.p99_latency_ms,
        avg_risk_score=summary.avg_risk_score,
        attacks_by_type=summary.attacks_by_type
    )


@app.get("/api/events", response_model=EventsResponse)
async def get_events(limit: int = 50):
    """Get recent security events"""
    if not orchestrator.enable_monitoring:
        raise HTTPException(status_code=503, detail="Monitoring not enabled")
    
    recent_events = orchestrator.logger.get_recent_events(limit=limit)
    
    events_list = [
        {
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'severity': event.severity,
            'user_input': event.user_input,
            'risk_score': event.risk_score,
            'action_taken': event.action_taken,
            'session_id': event.session_id
        }
        for event in recent_events
    ]
    
    return EventsResponse(
        total_events=len(events_list),
        events=events_list
    )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    success = orchestrator.clear_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": f"Session {session_id} cleared successfully"}


@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    stats = orchestrator.get_stats()
    
    dashboard_data = {
        "system_status": {
            "status": "online",
            "total_requests": stats['total_requests'],
            "success_rate": stats['success_rate'],
            "block_rate": stats['block_rate'],
            "active_sessions": stats['active_sessions']
        }
    }
    
    if orchestrator.enable_monitoring:
        summary = orchestrator.metrics.get_summary()
        log_stats = orchestrator.logger.get_stats()
        
        dashboard_data["performance"] = {
            "avg_latency_ms": summary.avg_latency_ms,
            "p95_latency_ms": summary.p95_latency_ms,
            "p99_latency_ms": summary.p99_latency_ms,
        }
        
        dashboard_data["security"] = {
            "avg_risk_score": summary.avg_risk_score,
            "attacks_by_type": summary.attacks_by_type,
            "total_events": log_stats['total_events'],
            "events_by_severity": log_stats['by_severity']
        }
    
    return dashboard_data


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Secure AI Agent API")
    print("=" * 60)
    print("\n📍 Endpoints:")
    print("   Web UI:        http://localhost:8000/")
    print("   API Docs:      http://localhost:8000/docs")
    print("   Health:        http://localhost:8000/health")
    print("   Chat API:      http://localhost:8000/api/chat")
    print("   Stats:         http://localhost:8000/api/stats")
    print("   Metrics:       http://localhost:8000/api/metrics")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

