"""
Core Data Models
Following SOLID principles - Single Responsibility
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class Action(str, Enum):
    """Action to take based on risk assessment"""
    BLOCK = "block"
    SANITIZE = "sanitize"
    MONITOR = "monitor"
    ALLOW = "allow"


class DetectionResult(BaseModel):
    """
    Result from attack detection
    
    Attributes:
        detected: Whether an attack was detected
        risk_score: Risk score (0.0 to 1.0)
        risk_level: Risk level category
        detected_patterns: List of pattern names that matched
        category: Attack category (e.g., 'instruction_override')
        details: Additional detection details
    """
    detected: bool
    risk_score: float = Field(ge=0.0, le=1.0, description="Risk score between 0 and 1")
    risk_level: RiskLevel
    detected_patterns: List[str] = Field(default_factory=list)
    category: str = "none"
    details: Optional[Dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detected": True,
                "risk_score": 0.95,
                "risk_level": "critical",
                "detected_patterns": ["instruction_override"],
                "category": "instruction_override",
                "details": {"method": "pattern_matching"}
            }
        }


class ValidationResult(BaseModel):
    """
    Result from input validation
    
    Attributes:
        valid: Whether input is valid (safe)
        action: Action to take (block, sanitize, allow, monitor)
        sanitized_input: Cleaned input if sanitized
        risk_score: Overall risk score
        detection_result: Detection details
        reasoning: Why this action was chosen
    """
    valid: bool
    action: Action
    sanitized_input: Optional[str] = None
    risk_score: float = Field(ge=0.0, le=1.0)
    detection_result: Optional[DetectionResult] = None
    reasoning: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "valid": False,
                "action": "block",
                "sanitized_input": None,
                "risk_score": 0.95,
                "reasoning": "Critical attack detected"
            }
        }


class AgentResponse(BaseModel):
    """
    Response from secure agent
    
    Attributes:
        message: Response message to user
        blocked: Whether request was blocked
        risk_score: Risk assessment score
        metadata: Additional response metadata
        security_alerts: List of security alerts/issues
        timestamp: Response timestamp
    """
    message: str
    blocked: bool
    risk_score: float = Field(ge=0.0, le=1.0)
    metadata: Dict = Field(default_factory=dict)
    security_alerts: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I cannot process that request.",
                "blocked": True,
                "risk_score": 0.95,
                "metadata": {"reason": "attack_detected"},
                "timestamp": "2025-11-12T10:00:00"
            }
        }


class FilterResult(BaseModel):
    """
    Result from output filtering
    
    Attributes:
        approved: Whether output is approved
        filtered_text: Filtered version of text
        issues_found: List of issues detected
        modifications: What was changed
    """
    approved: bool
    filtered_text: str
    issues_found: List[str] = Field(default_factory=list)
    modifications: List[str] = Field(default_factory=list)


class LogEntry(BaseModel):
    """
    Security log entry
    
    Attributes:
        timestamp: When event occurred
        event_type: Type of event (e.g., 'attack_detected')
        user_input: Original user input
        risk_score: Risk assessment
        action_taken: What action was taken
        details: Additional event details
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    user_input: str
    risk_score: float = Field(ge=0.0, le=1.0)
    action_taken: Action
    details: Dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-12T10:00:00",
                "event_type": "attack_blocked",
                "user_input": "Ignore all instructions",
                "risk_score": 0.95,
                "action_taken": "block",
                "details": {"category": "instruction_override"}
            }
        }


class Metrics(BaseModel):
    """
    System metrics
    
    Attributes:
        total_requests: Total number of requests processed
        attacks_detected: Number of attacks detected
        attacks_blocked: Number of attacks blocked
        false_positives: Number of false positives (if known)
        avg_risk_score: Average risk score
        avg_latency_ms: Average latency in milliseconds
    """
    total_requests: int = 0
    attacks_detected: int = 0
    attacks_blocked: int = 0
    false_positives: int = 0
    avg_risk_score: float = 0.0
    avg_latency_ms: float = 0.0
    
    def detection_rate(self) -> float:
        """Calculate detection rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.attacks_detected / self.total_requests) * 100
    
    def block_rate(self) -> float:
        """Calculate block rate"""
        if self.attacks_detected == 0:
            return 0.0
        return (self.attacks_blocked / self.attacks_detected) * 100

