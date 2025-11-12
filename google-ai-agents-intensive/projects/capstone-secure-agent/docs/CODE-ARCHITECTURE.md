# Code Architecture & Design Principles
## Following SOLID, DRY, and Clean Code Practices

---

## 📁 Directory Structure (Clean Architecture)

```
capstone-secure-agent/
│
├── src/                                    # Source code
│   ├── __init__.py
│   │
│   ├── core/                              # Core domain (SOLID: SRP)
│   │   ├── __init__.py
│   │   ├── models.py                      # Data models (Pydantic)
│   │   ├── interfaces.py                  # Abstract base classes
│   │   ├── exceptions.py                  # Custom exceptions
│   │   └── config.py                      # Configuration management
│   │
│   ├── agents/                            # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py                  # Base agent (DRY)
│   │   ├── orchestrator.py                # Orchestrator agent
│   │   ├── detector.py                    # Detector agent
│   │   ├── validator.py                   # Validator agent
│   │   ├── application.py                 # Application agent
│   │   ├── filter.py                      # Filter agent
│   │   └── monitor.py                     # Monitor agent
│   │
│   ├── detectors/                         # Detection logic (SOLID: SRP)
│   │   ├── __init__.py
│   │   ├── base_detector.py               # Abstract detector
│   │   ├── pattern_detector.py            # Regex patterns
│   │   ├── semantic_detector.py           # Semantic analysis
│   │   ├── encoding_detector.py           # Encoding detection
│   │   └── context_detector.py            # Context analysis
│   │
│   ├── validators/                        # Validation logic (SOLID: SRP)
│   │   ├── __init__.py
│   │   ├── base_validator.py              # Abstract validator
│   │   ├── input_validator.py             # Input validation
│   │   ├── normalizer.py                  # Input normalization
│   │   └── sanitizer.py                   # Input sanitization
│   │
│   ├── filters/                           # Output filtering (SOLID: SRP)
│   │   ├── __init__.py
│   │   ├── base_filter.py                 # Abstract filter
│   │   ├── leak_detector.py               # Prompt leak detection
│   │   ├── sensitive_filter.py            # Sensitive data filter
│   │   └── content_validator.py           # Content validation
│   │
│   ├── tools/                             # Agent tools (SOLID: ISP)
│   │   ├── __init__.py
│   │   ├── base_tool.py                   # Abstract tool
│   │   ├── detection_tools.py             # Tools for detector
│   │   ├── validation_tools.py            # Tools for validator
│   │   └── monitoring_tools.py            # Tools for monitor
│   │
│   ├── services/                          # Business logic (SOLID: DIP)
│   │   ├── __init__.py
│   │   ├── orchestration_service.py       # Agent orchestration
│   │   ├── detection_service.py           # Detection coordination
│   │   └── monitoring_service.py          # Monitoring coordination
│   │
│   ├── repositories/                      # Data access (SOLID: DIP)
│   │   ├── __init__.py
│   │   ├── base_repository.py             # Abstract repository
│   │   ├── log_repository.py              # Log storage
│   │   ├── metrics_repository.py          # Metrics storage
│   │   └── cache_repository.py            # Cache storage
│   │
│   ├── utils/                             # Utilities (DRY)
│   │   ├── __init__.py
│   │   ├── logger.py                      # Logging utility
│   │   ├── decorators.py                  # Reusable decorators
│   │   ├── helpers.py                     # Helper functions
│   │   └── constants.py                   # Shared constants
│   │
│   └── api/                               # API layer (SOLID: DIP)
│       ├── __init__.py
│       ├── routes/                        # FastAPI routes
│       │   ├── __init__.py
│       │   ├── agent.py                   # Agent endpoints
│       │   └── monitoring.py              # Monitoring endpoints
│       ├── schemas/                       # API schemas (Pydantic)
│       │   ├── __init__.py
│       │   ├── request.py                 # Request models
│       │   └── response.py                # Response models
│       └── dependencies.py                # FastAPI dependencies
│
├── tests/                                 # Test suite
│   ├── __init__.py
│   ├── unit/                             # Unit tests
│   │   ├── test_detectors/
│   │   ├── test_validators/
│   │   ├── test_filters/
│   │   └── test_agents/
│   ├── integration/                      # Integration tests
│   │   ├── test_agent_workflow.py
│   │   └── test_api_endpoints.py
│   ├── security/                         # Security tests
│   │   ├── test_attacks.py
│   │   └── test_false_positives.py
│   ├── performance/                      # Performance tests
│   │   └── test_latency.py
│   ├── conftest.py                       # Pytest fixtures (DRY)
│   └── fixtures/                         # Shared fixtures
│       ├── __init__.py
│       ├── agent_fixtures.py
│       └── data_fixtures.py
│
├── data/                                 # Data files
│   ├── test-cases/                       # Test data
│   ├── patterns/                         # Attack patterns
│   └── configs/                          # Configuration files
│
├── dashboard/                            # Streamlit dashboard
│   ├── __init__.py
│   ├── app.py                           # Main dashboard
│   ├── components/                       # UI components (DRY)
│   │   ├── __init__.py
│   │   ├── metrics_view.py
│   │   └── test_view.py
│   └── pages/                           # Dashboard pages
│       ├── home.py
│       ├── testing.py
│       └── monitoring.py
│
├── scripts/                             # Utility scripts
│   ├── setup.py                         # Setup script
│   ├── evaluate.py                      # Evaluation runner
│   └── load_test_data.py               # Data loader
│
├── docs/                                # Documentation
├── logs/                                # Log files (gitignored)
├── .env.example                         # Environment template
├── .gitignore
├── requirements.txt
├── setup.py                             # Package setup
└── README.md
```

---

## 🎯 SOLID Principles Implementation

### **S - Single Responsibility Principle**

**Each class has ONE reason to change**

```python
# ❌ BAD: Multiple responsibilities
class Agent:
    def detect_attack(self): pass      # Detection
    def validate_input(self): pass     # Validation
    def log_event(self): pass          # Logging
    def send_response(self): pass      # Response

# ✅ GOOD: Single responsibility
class AttackDetector:
    """Only responsible for detection"""
    def detect(self, text: str) -> DetectionResult:
        pass

class InputValidator:
    """Only responsible for validation"""
    def validate(self, text: str) -> ValidationResult:
        pass

class EventLogger:
    """Only responsible for logging"""
    def log(self, event: Event) -> None:
        pass
```

---

### **O - Open/Closed Principle**

**Open for extension, closed for modification**

```python
# src/detectors/base_detector.py
from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """Abstract base - closed for modification"""
    
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """Subclasses must implement"""
        pass
    
    def calculate_risk(self, detections: List) -> float:
        """Common logic - available to all"""
        return max([d.severity for d in detections], default=0.0)

# src/detectors/pattern_detector.py
class PatternDetector(BaseDetector):
    """Open for extension - add new detector"""
    
    def detect(self, text: str) -> DetectionResult:
        # Pattern-specific logic
        pass

# src/detectors/semantic_detector.py
class SemanticDetector(BaseDetector):
    """Another extension - no modification to base"""
    
    def detect(self, text: str) -> DetectionResult:
        # Semantic-specific logic
        pass
```

---

### **L - Liskov Substitution Principle**

**Subclasses should be substitutable for their base classes**

```python
# ✅ GOOD: All detectors can be used interchangeably
def analyze_input(text: str, detector: BaseDetector) -> bool:
    """Works with ANY detector"""
    result = detector.detect(text)
    return result.detected

# All these work!
pattern_det = PatternDetector()
semantic_det = SemanticDetector()
encoding_det = EncodingDetector()

analyze_input(text, pattern_det)   # ✅ Works
analyze_input(text, semantic_det)  # ✅ Works
analyze_input(text, encoding_det)  # ✅ Works
```

---

### **I - Interface Segregation Principle**

**Don't force classes to implement interfaces they don't use**

```python
# ❌ BAD: Fat interface
class IAgent(ABC):
    @abstractmethod
    def detect(self): pass
    @abstractmethod
    def validate(self): pass
    @abstractmethod
    def filter(self): pass
    @abstractmethod
    def monitor(self): pass
    # Not all agents need all methods!

# ✅ GOOD: Segregated interfaces
class IDetector(ABC):
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        pass

class IValidator(ABC):
    @abstractmethod
    def validate(self, text: str) -> ValidationResult:
        pass

class IFilter(ABC):
    @abstractmethod
    def filter(self, text: str) -> FilterResult:
        pass

# Implement only what you need
class DetectorAgent(IDetector):
    def detect(self, text: str) -> DetectionResult:
        # Only implements detection
        pass
```

---

### **D - Dependency Inversion Principle**

**Depend on abstractions, not concretions**

```python
# ❌ BAD: Direct dependency on concrete class
class OrchestratorAgent:
    def __init__(self):
        self.detector = PatternDetector()  # Concrete!
        self.validator = InputValidator()  # Concrete!

# ✅ GOOD: Depend on abstractions
class OrchestratorAgent:
    def __init__(
        self,
        detector: IDetector,      # Abstract interface
        validator: IValidator     # Abstract interface
    ):
        self.detector = detector
        self.validator = validator

# Dependency injection (DI)
orchestrator = OrchestratorAgent(
    detector=PatternDetector(),      # Inject concrete
    validator=InputValidator()       # Inject concrete
)

# Easy to swap implementations!
orchestrator_v2 = OrchestratorAgent(
    detector=SemanticDetector(),     # Different implementation
    validator=EnhancedValidator()    # Different implementation
)
```

---

## 🔄 DRY Principle (Don't Repeat Yourself)

### **1. Base Classes for Common Logic**

```python
# src/agents/base_agent.py
from abc import ABC, abstractmethod
from google import genai

class BaseAgent(ABC):
    """Base agent with common functionality (DRY)"""
    
    def __init__(self, client: genai.Client, model: str = 'gemini-2.0-flash-exp'):
        self.client = client
        self.model = model
        self._agent = None
    
    def _create_agent(self, system_instruction: str, tools: List = None):
        """Common agent creation logic"""
        self._agent = self.client.agents.create(
            model=self.model,
            system_instruction=system_instruction,
            tools=tools or []
        )
    
    def start_session(self):
        """Common session management"""
        return self._agent.start_session()
    
    @abstractmethod
    def process(self, input_data):
        """Each agent implements its own processing"""
        pass

# src/agents/detector.py
class DetectorAgent(BaseAgent):
    """Inherits common functionality"""
    
    def __init__(self, client: genai.Client):
        super().__init__(client)
        self._create_agent(
            system_instruction="You detect threats...",
            tools=[self._get_tools()]
        )
    
    def process(self, text: str) -> DetectionResult:
        # Only implement specific logic
        session = self.start_session()  # Use inherited method
        return session.send_message(text)
```

---

### **2. Shared Utilities**

```python
# src/utils/decorators.py
from functools import wraps
import time

def log_execution(func):
    """Reusable decorator (DRY)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

def handle_errors(func):
    """Reusable error handler (DRY)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

# Use everywhere!
class DetectorAgent:
    @log_execution
    @handle_errors
    def detect(self, text: str):
        pass

class ValidatorAgent:
    @log_execution
    @handle_errors
    def validate(self, text: str):
        pass
```

---

### **3. Shared Constants**

```python
# src/utils/constants.py
"""Shared constants (DRY)"""

class RiskThresholds:
    CRITICAL = 0.8
    HIGH = 0.6
    MEDIUM = 0.4
    LOW = 0.2

class Actions:
    BLOCK = 'block'
    SANITIZE = 'sanitize'
    MONITOR = 'monitor'
    ALLOW = 'allow'

class AgentModels:
    GEMINI_FLASH = 'gemini-2.0-flash-exp'
    GEMINI_PRO = 'gemini-1.5-pro'

# Use everywhere
if risk_score >= RiskThresholds.CRITICAL:
    return Actions.BLOCK
```

---

## 🏛️ Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│  Presentation Layer (API/Dashboard)     │  ← FastAPI, Streamlit
│  - User interfaces                      │
│  - Input/Output formatting              │
└─────────────────┬───────────────────────┘
                  │ (Depends on ↓)
┌─────────────────┴───────────────────────┐
│  Application Layer (Services)           │  ← Business logic
│  - Use cases                            │
│  - Agent orchestration                  │
│  - Workflow coordination                │
└─────────────────┬───────────────────────┘
                  │ (Depends on ↓)
┌─────────────────┴───────────────────────┐
│  Domain Layer (Core)                    │  ← Core business rules
│  - Agents                               │
│  - Detectors                            │
│  - Validators                           │
│  - Models                               │
└─────────────────┬───────────────────────┘
                  │ (Depends on ↓)
┌─────────────────┴───────────────────────┐
│  Infrastructure Layer                   │  ← External dependencies
│  - Google ADK                           │
│  - Database                             │
│  - File system                          │
│  - Logging                              │
└─────────────────────────────────────────┘
```

**Key Rule:** Inner layers NEVER depend on outer layers!

---

## 📦 Code Organization Examples

### **1. Models (Pydantic)**

```python
# src/core/models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DetectionResult(BaseModel):
    """Detection result model (type-safe)"""
    detected: bool
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    detected_patterns: List[str]
    category: str
    details: Optional[dict] = None

class ValidationResult(BaseModel):
    """Validation result model"""
    valid: bool
    action: str  # 'allow', 'sanitize', 'block'
    sanitized_input: Optional[str] = None
    detection_result: Optional[DetectionResult] = None

class AgentResponse(BaseModel):
    """Agent response model"""
    message: str
    blocked: bool
    risk_score: float
    metadata: dict
```

---

### **2. Interfaces (Abstract Base Classes)**

```python
# src/core/interfaces.py
from abc import ABC, abstractmethod
from typing import Any
from src.core.models import DetectionResult, ValidationResult

class IDetector(ABC):
    """Detector interface"""
    
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """Detect attacks in text"""
        pass

class IValidator(ABC):
    """Validator interface"""
    
    @abstractmethod
    def validate(self, text: str, detection: DetectionResult) -> ValidationResult:
        """Validate input"""
        pass

class IAgent(ABC):
    """Base agent interface"""
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input"""
        pass
```

---

### **3. Configuration Management**

```python
# src/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings (from env)"""
    
    # API Keys
    gemini_api_key: str
    
    # Model settings
    model_name: str = 'gemini-2.0-flash-exp'
    model_temperature: float = 0.0
    
    # Security thresholds
    risk_threshold_block: float = 0.8
    risk_threshold_sanitize: float = 0.5
    risk_threshold_monitor: float = 0.3
    
    # Performance
    max_context_length: int = 10000
    request_timeout: int = 30
    
    # Logging
    log_level: str = 'INFO'
    log_file: str = 'logs/security.log'
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Singleton instance
settings = Settings()
```

---

### **4. Dependency Injection**

```python
# src/core/dependencies.py
from functools import lru_cache
from google import genai
from src.core.config import settings

@lru_cache()
def get_genai_client() -> genai.Client:
    """Get Gemini client (singleton)"""
    return genai.Client(api_key=settings.gemini_api_key)

@lru_cache()
def get_detector() -> IDetector:
    """Get detector instance"""
    from src.detectors.pattern_detector import PatternDetector
    return PatternDetector()

@lru_cache()
def get_validator() -> IValidator:
    """Get validator instance"""
    from src.validators.input_validator import InputValidator
    return InputValidator()

# Usage in FastAPI
from fastapi import Depends

@app.post("/analyze")
def analyze(
    text: str,
    detector: IDetector = Depends(get_detector),
    validator: IValidator = Depends(get_validator)
):
    detection = detector.detect(text)
    validation = validator.validate(text, detection)
    return validation
```

---

## ✅ Best Practices Checklist

### **Code Quality**
- [ ] Type hints on all functions
- [ ] Docstrings for all classes/methods
- [ ] No magic numbers (use constants)
- [ ] Max function length: 50 lines
- [ ] Max file length: 500 lines
- [ ] Follow PEP 8 style guide

### **Testing**
- [ ] Unit tests for each class
- [ ] Integration tests for workflows
- [ ] >80% code coverage
- [ ] Test fixtures in conftest.py
- [ ] Mock external dependencies

### **SOLID Compliance**
- [ ] Single Responsibility per class
- [ ] Abstract base classes for extensibility
- [ ] Subclasses substitutable
- [ ] Small, focused interfaces
- [ ] Dependency injection used

### **DRY Compliance**
- [ ] No duplicate code
- [ ] Shared utilities extracted
- [ ] Constants centralized
- [ ] Base classes for common logic
- [ ] Decorators for cross-cutting concerns

---

## 🎯 Implementation Checklist

### **Phase 1: Core Setup**
```bash
# 1. Create structure
mkdir -p src/{core,agents,detectors,validators,filters,tools,services,repositories,utils,api}
mkdir -p tests/{unit,integration,security,performance}

# 2. Create base files
touch src/core/{__init__.py,models.py,interfaces.py,config.py,exceptions.py}
touch src/agents/{__init__.py,base_agent.py}
touch src/detectors/{__init__.py,base_detector.py}

# 3. Setup configuration
cp .env.example .env
# Add your API key
```

### **Phase 2: Implement Base Classes**
- [ ] Core models (Pydantic)
- [ ] Abstract interfaces
- [ ] Base agent class
- [ ] Base detector class
- [ ] Configuration management

### **Phase 3: Implement Concrete Classes**
- [ ] Pattern detector
- [ ] Input validator
- [ ] Detector agent
- [ ] Validator agent
- [ ] Orchestrator agent

### **Phase 4: Add Infrastructure**
- [ ] Logging setup
- [ ] Error handling
- [ ] Metrics collection
- [ ] Repository pattern for data

### **Phase 5: Testing**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Security tests
- [ ] Performance tests

---

## 📚 Example: Full Implementation

See `src/` directory for complete implementation following all principles!

---

**Remember:** Clean code is not about being clever, it's about being clear! 🎯

