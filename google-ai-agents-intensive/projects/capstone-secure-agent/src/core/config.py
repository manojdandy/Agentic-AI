"""
Configuration Management
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from .env file
    Following DRY principle - single source of configuration
    """
    
    # API Keys
    gemini_api_key: str = ""
    
    # Model Configuration
    model_name: str = "gemini-2.0-flash-exp"
    model_temperature: float = 0.0
    max_tokens: int = 2048
    
    # Security Thresholds (following DRY - centralized)
    risk_threshold_block: float = 0.8
    risk_threshold_sanitize: float = 0.5
    risk_threshold_monitor: float = 0.3
    
    # Performance Settings
    max_context_length: int = 10000
    request_timeout: int = 30
    max_retries: int = 3
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/security.log"
    enable_metrics: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # Database (for future use)
    db_type: str = "sqlite"  # sqlite, postgresql
    db_path: str = "data/security.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings instance (singleton pattern)
    Cached to avoid reading .env multiple times
    """
    return Settings()


# Export singleton instance
settings = get_settings()


# Constants (DRY principle - single source of truth)
class RiskThresholds:
    """Risk assessment thresholds"""
    CRITICAL = 0.8
    HIGH = 0.6
    MEDIUM = 0.4
    LOW = 0.2


class AttackCategories:
    """Attack category constants"""
    INSTRUCTION_OVERRIDE = "instruction_override"
    ROLE_MANIPULATION = "role_manipulation"
    PROMPT_EXTRACTION = "prompt_extraction"
    DELIMITER_BREAKING = "delimiter_breaking"
    ENCODING = "encoding"
    JAILBREAK = "jailbreak"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MANIPULATION = "manipulation"
    TOOL_EXPLOITATION = "tool_exploitation"
    CONTEXT_ATTACK = "context_attack"
    OUTPUT_MANIPULATION = "output_manipulation"
    LOGIC_EXPLOITATION = "logic_exploitation"
    INDIRECT_INJECTION = "indirect_injection"
    PAYLOAD_SPLITTING = "payload_splitting"
    MODEL_SPECIFIC = "model_specific"


# Export commonly used constants
__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "RiskThresholds",
    "AttackCategories"
]

