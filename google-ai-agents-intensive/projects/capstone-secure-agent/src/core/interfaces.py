"""
Abstract Interfaces
Following SOLID: Interface Segregation Principle
Small, focused interfaces
"""

from abc import ABC, abstractmethod
from typing import Any
from src.core.models import DetectionResult, ValidationResult, FilterResult, AgentResponse


class IDetector(ABC):
    """
    Interface for attack detection
    Following SOLID: ISP - Single focused interface
    """
    
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """
        Detect attacks in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            DetectionResult with findings
        """
        pass


class IValidator(ABC):
    """
    Interface for input validation
    Following SOLID: ISP - Separate from detection
    """
    
    @abstractmethod
    def validate(self, text: str, detection: DetectionResult) -> ValidationResult:
        """
        Validate input and determine action
        
        Args:
            text: Input text
            detection: Detection results
            
        Returns:
            ValidationResult with action to take
        """
        pass


class IFilter(ABC):
    """
    Interface for output filtering
    Following SOLID: ISP - Separate concern
    """
    
    @abstractmethod
    def filter(self, text: str, system_prompt: str = "") -> FilterResult:
        """
        Filter output for safety
        
        Args:
            text: Output text to filter
            system_prompt: System prompt to check against
            
        Returns:
            FilterResult with filtered text
        """
        pass


class IAgent(ABC):
    """
    Base interface for agents
    Following SOLID: ISP - Minimal interface
    """
    
    @abstractmethod
    def process_message(self, message: str, session: Any = None) -> AgentResponse:
        """
        Process a message
        
        Args:
            message: User message
            session: Optional session context
            
        Returns:
            AgentResponse with reply
        """
        pass


class IOrchestrator(ABC):
    """
    Interface for request orchestration
    Following SOLID: ISP - Coordinates security layers
    """
    
    @abstractmethod
    def handle_request(self, user_input: str, session_id: str = None) -> AgentResponse:
        """
        Handle a complete user request through all security layers
        
        Args:
            user_input: User's input message
            session_id: Optional session ID
            
        Returns:
            AgentResponse with final response or block message
        """
        pass


class ILogger(ABC):
    """
    Interface for logging
    Following SOLID: ISP - Separate logging concern
    """
    
    @abstractmethod
    def log(self, event_type: str, data: dict) -> None:
        """
        Log security event
        
        Args:
            event_type: Type of event
            data: Event data
        """
        pass


class IRepository(ABC):
    """
    Interface for data persistence
    Following SOLID: DIP - Depend on abstraction
    """
    
    @abstractmethod
    def save(self, data: Any) -> None:
        """Save data"""
        pass
    
    @abstractmethod
    def find_all(self) -> list:
        """Retrieve all data"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Any:
        """Find by ID"""
        pass


# Export all interfaces
__all__ = [
    "IDetector",
    "IValidator",
    "IFilter",
    "IAgent",
    "IOrchestrator",
    "ILogger",
    "IRepository"
]

