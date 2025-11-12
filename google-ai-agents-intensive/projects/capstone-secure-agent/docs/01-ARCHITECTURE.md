# System Architecture
## Secure AI Agent with Prompt Injection Detection

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Dashboard / API Client)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
│  - Rate limiting                                                │
│  - Authentication                                               │
│  - Request logging                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Security Pipeline                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Pre-Processing & Normalization                      │   │
│  │     - Decode attempts (base64, unicode, etc)            │   │
│  │     - Normalize whitespace                              │   │
│  │     - Extract embedded content                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  2. Injection Detection Layer                           │   │
│  │     - Pattern matching (regex)                          │   │
│  │     - Semantic analysis                                 │   │
│  │     - Context integrity check                           │   │
│  │     - Risk scoring                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  3. Decision Engine                                     │   │
│  │     - Risk threshold evaluation                         │   │
│  │     - Action determination (allow/block/flag)           │   │
│  │     - Sanitization strategy selection                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
            BLOCKED                    ALLOWED
                 │                         │
                 ▼                         ▼
         ┌──────────────┐      ┌─────────────────────────────────┐
         │   Generate   │      │     Secure Agent Core           │
         │    Safe      │      │                                 │
         │   Response   │      │  ┌──────────────────────────┐   │
         └──────────────┘      │  │  System Prompt           │   │
                               │  │  (Protected)             │   │
                               │  └──────────────────────────┘   │
                               │              │                  │
                               │              ▼                  │
                               │  ┌──────────────────────────┐   │
                               │  │  Context Manager         │   │
                               │  │  - Conversation history  │   │
                               │  │  - Memory isolation      │   │
                               │  └──────────────────────────┘   │
                               │              │                  │
                               │              ▼                  │
                               │  ┌──────────────────────────┐   │
                               │  │  LLM (Gemini API)        │   │
                               │  └──────────────────────────┘   │
                               │              │                  │
                               │              ▼                  │
                               │  ┌──────────────────────────┐   │
                               │  │  Tool Execution          │   │
                               │  │  (Sandboxed)             │   │
                               │  └──────────────────────────┘   │
                               └─────────────┬───────────────────┘
                                             │
                                             ▼
                               ┌─────────────────────────────────┐
                               │  Output Validation Layer        │
                               │  - Check for leaked prompts     │
                               │  - Sensitive data filtering     │
                               │  - Content policy enforcement   │
                               └─────────────┬───────────────────┘
                                             │
                                             ▼
                               ┌─────────────────────────────────┐
                               │   Monitoring & Logging          │
                               │   - Audit trail                 │
                               │   - Metrics collection          │
                               │   - Alert generation            │
                               └─────────────┬───────────────────┘
                                             │
                                             ▼
                               ┌─────────────────────────────────┐
                               │       Response to User          │
                               └─────────────────────────────────┘
```

---

## 🔍 Component Details

### 1. Input Processing Layer

**Purpose:** Normalize and prepare user input for analysis

**Components:**
- **Decoder:** Detect and decode obfuscated content
  - Base64 encoding
  - Unicode escapes
  - ROT13/Caesar cipher
  - Hex encoding
  
- **Normalizer:** Standardize input format
  - Whitespace normalization
  - Case handling
  - Special character mapping

- **Extractor:** Pull out embedded content
  - URLs and their content
  - Attached files
  - Code blocks

**Output:** Normalized input + extracted metadata

---

### 2. Injection Detection Layer

**Purpose:** Identify potential injection attempts

**Detection Modules:**

#### a) Pattern Matcher
```python
class PatternDetector:
    """
    Rule-based detection using known patterns
    """
    patterns = {
        'ignore_instructions': [
            r'ignore (previous|above|all) instructions?',
            r'disregard (previous|prior) (commands?|prompts?)',
            r'forget (everything|all|what) (you|was) (told|said)',
        ],
        'role_manipulation': [
            r'you are (now|a) (new|different)',
            r'pretend (you are|to be)',
            r'act as (if|a)',
            r'roleplay as',
        ],
        'system_probe': [
            r'(show|reveal|display) (your|the) (system|original) (prompt|instructions)',
            r'what (are|were) your (instructions|rules)',
            r'repeat (your|the) (prompt|instructions)',
        ],
        'delimiter_breaking': [
            r'---+\s*END',
            r'"""\s*END',
            r'</system>',
            r'\[END INSTRUCTIONS\]',
        ],
        'encoding_tricks': [
            r'base64:',
            r'\\x[0-9a-f]{2}',
            r'&#\d+;',
        ]
    }
```

#### b) Semantic Analyzer
```python
class SemanticAnalyzer:
    """
    NLP-based detection for subtle attacks
    """
    def analyze(self, text):
        # Check for:
        # - Instruction-like language
        # - Topic shifts
        # - Contradiction with context
        # - Unusual phrasing patterns
        pass
```

#### c) Context Integrity Checker
```python
class ContextIntegrityChecker:
    """
    Verify conversation flow consistency
    """
    def check(self, current_input, conversation_history):
        # Detect:
        # - Sudden topic changes
        # - Contradictory statements
        # - Meta-conversational attempts
        # - Payload splitting across turns
        pass
```

#### d) Risk Scorer
```python
class RiskScorer:
    """
    Aggregate detection signals into risk score
    """
    def calculate_risk(self, detection_results):
        risk_score = 0
        
        # Weight different signal types
        if detection_results['pattern_match']:
            risk_score += 0.6
        if detection_results['semantic_flags']:
            risk_score += 0.3
        if detection_results['context_issues']:
            risk_score += 0.2
            
        return min(risk_score, 1.0)
```

**Output:** Risk assessment with detailed findings

---

### 3. Decision Engine

**Purpose:** Determine appropriate action based on risk

**Decision Logic:**
```python
class DecisionEngine:
    RISK_THRESHOLDS = {
        'block': 0.8,      # High confidence attack - block
        'sanitize': 0.5,   # Suspicious - sanitize and allow
        'monitor': 0.3,    # Low risk - allow but monitor
        'allow': 0.0       # Clean input
    }
    
    def decide(self, risk_score, detection_details):
        if risk_score >= self.RISK_THRESHOLDS['block']:
            return Action.BLOCK
        elif risk_score >= self.RISK_THRESHOLDS['sanitize']:
            return Action.SANITIZE
        elif risk_score >= self.RISK_THRESHOLDS['monitor']:
            return Action.MONITOR
        else:
            return Action.ALLOW
```

**Actions:**
1. **BLOCK:** Reject input, return safe error message
2. **SANITIZE:** Remove suspicious parts, proceed with cleaned input
3. **MONITOR:** Allow but log for review
4. **ALLOW:** Process normally

---

### 4. Secure Agent Core

**Purpose:** Execute agent logic with security constraints

**Key Features:**

#### a) Protected System Prompt
```python
class SecureAgent:
    def __init__(self):
        self.system_prompt = self._load_protected_prompt()
        self.prompt_hash = hash(self.system_prompt)
        
    def validate_prompt_integrity(self):
        """Ensure system prompt hasn't been modified"""
        return hash(self.system_prompt) == self.prompt_hash
```

#### b) Context Isolation
```python
class ContextManager:
    """
    Isolate user context from system context
    """
    def __init__(self):
        self.system_context = []    # Protected
        self.user_context = []      # User conversation
        
    def build_prompt(self, user_input):
        # System instructions always come first
        # User content clearly demarcated
        return self._combine_contexts(
            system=self.system_context,
            user=self.user_context + [user_input]
        )
```

#### c) Tool Sandboxing
```python
class SandboxedToolExecutor:
    """
    Execute tools with restricted permissions
    """
    ALLOWED_TOOLS = ['search', 'calculate', 'summarize']
    FORBIDDEN_TOOLS = ['execute_code', 'file_access', 'network']
    
    def execute(self, tool_name, params):
        if tool_name not in self.ALLOWED_TOOLS:
            raise SecurityError(f"Tool {tool_name} not allowed")
            
        # Execute with timeout and resource limits
        return self._safe_execute(tool_name, params)
```

---

### 5. Output Validation Layer

**Purpose:** Prevent information leakage in responses

**Validators:**

#### a) Prompt Leak Detector
```python
class PromptLeakDetector:
    """
    Detect if system prompt is being revealed
    """
    def check(self, output, system_prompt):
        # Check for exact matches
        # Check for paraphrasing
        # Check for structured extraction
        similarity = self._calculate_similarity(output, system_prompt)
        return similarity < 0.3  # Threshold
```

#### b) Sensitive Data Filter
```python
class SensitiveDataFilter:
    """
    Remove sensitive information from output
    """
    PATTERNS = {
        'api_keys': r'[A-Za-z0-9]{32,}',
        'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'internal_paths': r'/internal/|/admin/|/system/',
    }
    
    def filter(self, output):
        for pattern_type, pattern in self.PATTERNS.items():
            output = re.sub(pattern, '[REDACTED]', output)
        return output
```

---

### 6. Monitoring & Logging System

**Purpose:** Comprehensive audit trail and metrics

**Components:**

#### a) Audit Logger
```python
class AuditLogger:
    """
    Detailed logging of all security events
    """
    def log_event(self, event_type, details):
        log_entry = {
            'timestamp': datetime.now(),
            'event_type': event_type,
            'risk_score': details.get('risk_score'),
            'action_taken': details.get('action'),
            'user_id': details.get('user_id'),
            'input_hash': hash(details.get('input')),
            'detection_details': details.get('detections'),
        }
        self._write_to_log(log_entry)
```

#### b) Metrics Collector
```python
class MetricsCollector:
    """
    Track performance and security metrics
    """
    def track(self):
        return {
            'requests_total': self.request_count,
            'attacks_detected': self.attack_count,
            'attacks_blocked': self.block_count,
            'false_positives': self.false_positive_count,
            'avg_latency': self.avg_latency,
            'detection_rate': self.attack_count / self.request_count,
        }
```

#### c) Alert Manager
```python
class AlertManager:
    """
    Generate alerts for security events
    """
    def check_alert_conditions(self, metrics):
        if metrics['attack_rate'] > 0.5:
            self.send_alert('HIGH_ATTACK_RATE')
        if metrics['unique_attackers'] > 10:
            self.send_alert('COORDINATED_ATTACK')
```

---

## 🔒 Security Layers

### Defense in Depth Strategy

**Layer 1: Prevention**
- Input validation
- Pattern blocking
- Sanitization

**Layer 2: Detection**
- Real-time monitoring
- Anomaly detection
- Behavioral analysis

**Layer 3: Response**
- Graceful degradation
- Safe error messages
- Attack logging

**Layer 4: Recovery**
- Session isolation
- Context reset
- Incident review

---

## 📊 Data Flow

### Normal Request Flow
```
User Input → Normalize → Detect (Clean) → Allow → Agent → Validate → Response
```

### Suspicious Request Flow
```
User Input → Normalize → Detect (Risky) → Sanitize → Agent → Validate → Response + Log
```

### Attack Request Flow
```
User Input → Normalize → Detect (Attack) → Block → Safe Message + Alert
```

---

## 🎯 Design Principles

1. **Fail Secure:** Default to blocking on uncertainty
2. **Layered Defense:** Multiple independent checks
3. **Minimal Trust:** Validate everything
4. **Transparency:** Log all security decisions
5. **Performance:** <100ms overhead target
6. **Maintainability:** Modular, testable components

---

## 🔧 Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Detection | Regex + NLP | Fast patterns + semantic understanding |
| Agent | Google ADK | Course requirement, good tooling |
| Logging | Structured JSON | Easy querying and analysis |
| Storage | SQLite → PostgreSQL | Start simple, scale later |
| Caching | In-memory dict → Redis | Performance optimization |
| API | FastAPI | Async, fast, easy testing |
| Dashboard | Streamlit | Quick prototyping, interactive |

---

## 🚀 Scalability Considerations

### Current Scope (MVP)
- Single process
- In-memory caching
- Local SQLite
- Synchronous processing

### Future Enhancements
- Multi-process with queue
- Redis caching
- PostgreSQL database
- Async processing
- Microservices architecture

---

**Next:** See `02-ATTACK-PATTERNS.md` for detailed attack taxonomy

