"""
Configuration Management
Loads ALL settings from environment variables (.env file)
No hardcoded values - everything is configurable!
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings - ALL values loaded from .env file
    Following DRY principle - single source of configuration
    
    Defaults are provided but can be overridden via environment variables
    Set values in .env file or export them before running
    """
    
    # ===== API Keys =====
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API Key (required for LLM)",
        validation_alias="GEMINI_API_KEY"
    )
    
    # ===== Model Configuration =====
    use_mock_gemini: bool = Field(
        default=False,
        description="Use MockGeminiClient (True) or real Gemini API (False). Set to True for testing without API costs.",
        validation_alias="USE_MOCK_GEMINI"
    )
    model_name: str = Field(
        default="gemini-2.0-flash-exp",
        description="Gemini model to use",
        validation_alias="MODEL_NAME"
    )
    model_temperature: float = Field(
        default=0.0,
        description="Model temperature (0.0 = deterministic, 1.0 = creative)",
        validation_alias="MODEL_TEMPERATURE"
    )
    max_tokens: int = Field(
        default=2048,
        description="Maximum tokens in model response",
        validation_alias="MAX_TOKENS"
    )
    
    # ===== Security Thresholds (following DRY - centralized) =====
    risk_threshold_block: float = Field(
        default=0.8,
        description="Risk score threshold to block requests (0.0-1.0)",
        validation_alias="RISK_THRESHOLD_BLOCK"
    )
    risk_threshold_sanitize: float = Field(
        default=0.5,
        description="Risk score threshold to sanitize input (0.0-1.0)",
        validation_alias="RISK_THRESHOLD_SANITIZE"
    )
    risk_threshold_monitor: float = Field(
        default=0.3,
        description="Risk score threshold to monitor requests (0.0-1.0)",
        validation_alias="RISK_THRESHOLD_MONITOR"
    )
    
    # ===== Performance Settings =====
    max_context_length: int = Field(
        default=10000,
        description="Maximum context length in characters",
        validation_alias="MAX_CONTEXT_LENGTH"
    )
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        validation_alias="REQUEST_TIMEOUT"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests",
        validation_alias="MAX_RETRIES"
    )
    
    # ===== Logging Configuration =====
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
        validation_alias="LOG_LEVEL"
    )
    log_file: str = Field(
        default="logs/security.log",
        description="Path to security log file",
        validation_alias="LOG_FILE"
    )
    enable_metrics: bool = Field(
        default=True,
        description="Enable metrics collection",
        validation_alias="ENABLE_METRICS"
    )
    
    # ===== Rate Limiting =====
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per time window",
        validation_alias="RATE_LIMIT_REQUESTS"
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Time window for rate limiting (seconds)",
        validation_alias="RATE_LIMIT_WINDOW_SECONDS"
    )
    
    # ===== Database (for future use) =====
    db_type: str = Field(
        default="sqlite",
        description="Database type (sqlite, postgresql)",
        validation_alias="DB_TYPE"
    )
    db_path: str = Field(
        default="data/security.db",
        description="Path to database file",
        validation_alias="DB_PATH"
    )
    
    # ===== Length Validator (Large Prompt Defense) =====
    tier: str = Field(
        default="free",
        description="Service tier (free, starter, pro, enterprise)",
        validation_alias="TIER"
    )
    max_char_limit: int = Field(
        default=50000,
        description="Maximum characters allowed in input",
        validation_alias="MAX_CHAR_LIMIT"
    )
    max_token_limit: int = Field(
        default=2000,
        description="Maximum tokens allowed in input",
        validation_alias="MAX_TOKEN_LIMIT"
    )
    
    # ===== Environment =====
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
        validation_alias="ENVIRONMENT"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
        validation_alias="DEBUG"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
        env_ignore_empty=True  # Ignore if .env doesn't exist
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings instance (singleton pattern)
    Cached to avoid reading .env multiple times
    .env file is optional - will use defaults if not present
    """
    try:
        return Settings()
    except (PermissionError, FileNotFoundError):
        # If .env is not accessible, use defaults from environment or defaults
        return Settings(_env_file=None)


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

