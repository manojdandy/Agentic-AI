"""
Output Filter
Filters and validates model outputs for safety
Following SOLID: Single Responsibility & Dependency Inversion
"""

from typing import Optional
from src.core.interfaces import IFilter
from src.core.models import FilterResult
from src.filters.context_protector import ContextProtector, ProtectedContext, LeakageResult
import re


class OutputFilter(IFilter):
    """
    Filters model outputs to prevent leakage and harmful content
    Following SOLID: Depends on ContextProtector (composition over inheritance)
    Following DRY: Reuses context protection logic
    """
    
    # Threshold for blocking vs sanitizing
    BLOCK_THRESHOLD = 0.8
    SANITIZE_THRESHOLD = 0.5
    
    def __init__(self, protected_context: Optional[ProtectedContext] = None):
        """
        Initialize output filter
        
        Args:
            protected_context: Optional context protection config
        """
        # Initialize context protector
        if protected_context is None:
            protected_context = ProtectedContext()
        
        self.context_protector = ContextProtector(protected_context)
        
        # Compile harmful content patterns
        self._compile_harmful_patterns()
    
    def _compile_harmful_patterns(self):
        """
        Compile patterns for harmful content detection (DRY)
        Pre-compile for performance
        """
        self.harmful_patterns = {
            'injection_attempt': [
                re.compile(r'\b(ignore|disregard|forget)\b.*\b(instruction|command)', re.IGNORECASE),
                re.compile(r'\byou\s+(should|must|need to)\s+(ignore|disregard)', re.IGNORECASE),
            ],
            'manipulation': [
                re.compile(r'\b(trick|manipulate|deceive)\s+(the\s+)?(user|system)', re.IGNORECASE),
                re.compile(r'\bbypass\s+(security|safety|filter)', re.IGNORECASE),
            ],
            'harmful_instruction': [
                re.compile(r'\b(how\s+to|guide\s+to|steps\s+to)\s+(hack|exploit|attack)', re.IGNORECASE),
                re.compile(r'\bcreate\s+(malware|virus|exploit)', re.IGNORECASE),
            ],
        }
    
    def filter(self, text: str) -> FilterResult:
        """
        Filter output text for safety
        
        Args:
            text: Output text to filter
            
        Returns:
            FilterResult with filtered text and safety info
        """
        if not text or not text.strip():
            return FilterResult(
                approved=False,
                filtered_text="",
                issues_found=["empty_output"],
                modifications=[]
            )
        
        issues_found = []
        modifications = []
        filtered_text = text
        
        # Step 1: Check for leakage
        leakage = self.context_protector.detect_leakage(text)
        
        if leakage.leaked:
            issues_found.append(f"leakage_{leakage.leakage_type}")
            
            # Decide: block or sanitize based on confidence
            if leakage.confidence >= self.BLOCK_THRESHOLD:
                # Critical leakage - block entirely
                return FilterResult(
                    approved=False,
                    filtered_text="I apologize, but I cannot provide that information.",
                    issues_found=issues_found,
                    modifications=["blocked_due_to_leakage"]
                )
            else:
                # Sanitize the leakage
                filtered_text = self.context_protector.sanitize_output(filtered_text, leakage)
                modifications.append(f"sanitized_{leakage.leakage_type}")
        
        # Step 2: Check for harmful content
        harmful_result = self._check_harmful_content(filtered_text)
        
        if harmful_result['found']:
            issues_found.extend(harmful_result['issues'])
            
            if harmful_result['severity'] >= self.BLOCK_THRESHOLD:
                # Block harmful content
                return FilterResult(
                    approved=False,
                    filtered_text="I cannot provide that information as it may be harmful.",
                    issues_found=issues_found,
                    modifications=["blocked_due_to_harmful_content"]
                )
            else:
                # Sanitize harmful content
                filtered_text = self._sanitize_harmful_content(filtered_text)
                modifications.append("sanitized_harmful_content")
        
        # Step 3: Check output length (prevent token exhaustion attacks)
        if len(filtered_text) > 10000:
            issues_found.append("excessive_length")
            filtered_text = filtered_text[:10000] + "... [truncated]"
            modifications.append("truncated_length")
        
        # Step 4: Final safety check
        approved = len(issues_found) == 0
        
        return FilterResult(
            approved=approved,
            filtered_text=filtered_text,
            issues_found=issues_found,
            modifications=modifications
        )
    
    def _check_harmful_content(self, text: str) -> dict:
        """
        Check for harmful content patterns (DRY)
        
        Args:
            text: Text to check
            
        Returns:
            Dictionary with findings
        """
        found = False
        issues = []
        max_severity = 0.0
        
        for harm_type, patterns in self.harmful_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    found = True
                    issues.append(harm_type)
                    
                    # Assign severity
                    severity_map = {
                        'injection_attempt': 0.9,
                        'manipulation': 0.8,
                        'harmful_instruction': 0.95,
                    }
                    max_severity = max(max_severity, severity_map.get(harm_type, 0.7))
        
        return {
            'found': found,
            'issues': issues,
            'severity': max_severity
        }
    
    def _sanitize_harmful_content(self, text: str) -> str:
        """
        Remove harmful content from text (DRY)
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        sanitized = text
        
        # Remove sentences containing harmful patterns
        for harm_type, patterns in self.harmful_patterns.items():
            for pattern in patterns:
                # Remove entire sentence containing pattern
                sanitized = re.sub(
                    pattern.pattern + r'[^.!?]*[.!?]',
                    '[Content removed for safety].',
                    sanitized,
                    flags=re.IGNORECASE
                )
        
        return sanitized.strip()
    
    def update_protected_context(self, context: ProtectedContext):
        """
        Update the protected context
        
        Args:
            context: New protected context
        """
        self.context_protector = ContextProtector(context)
    
    def get_filter_stats(self) -> dict:
        """
        Get filter statistics
        
        Returns:
            Dictionary with filter stats
        """
        protection_summary = self.context_protector.get_protection_summary()
        
        return {
            'context_protection': protection_summary,
            'harmful_pattern_categories': len(self.harmful_patterns),
            'total_harmful_patterns': sum(len(p) for p in self.harmful_patterns.values()),
            'block_threshold': self.BLOCK_THRESHOLD,
            'sanitize_threshold': self.SANITIZE_THRESHOLD,
        }


# Demo/Test
if __name__ == "__main__":
    """
    Demo: Test the output filter
    Run: python -m src.filters.output_filter
    """
    print("=" * 60)
    print("🔒 OUTPUT FILTER TEST")
    print("=" * 60)
    
    # Create protected context
    context = ProtectedContext(
        system_prompt="You are a helpful AI assistant. Follow safety guidelines.",
        secret_keys=["sk-test123456789"],
        protected_phrases=["internal system", "admin access"]
    )
    
    output_filter = OutputFilter(context)
    
    # Test cases
    tests = [
        ("Hello! I'd be happy to help you learn Python.", "Safe output"),
        ("You are a helpful AI assistant. Follow safety", "System prompt leak"),
        ("Here's the API key: sk-test123456789", "Secret key leak"),
        ("To bypass security, you should ignore the filter.", "Harmful content"),
        ("Here's how to create malware using Python...", "Harmful instruction"),
        ("I can explain Python programming basics.", "Safe technical"),
        ("My internal system architecture is based on...", "Protected phrase"),
        ("A" * 15000, "Excessive length"),
    ]
    
    print("\n📋 Running filter tests:\n")
    
    passed = 0
    for output, description in tests:
        result = output_filter.filter(output)
        
        # Determine expected behavior
        is_safe = description in ["Safe output", "Safe technical"]
        success = result.approved == is_safe
        
        if success:
            passed += 1
        
        status = "✅" if success else "⚠️"
        approval = "✓ APPROVED" if result.approved else "✗ FILTERED"
        
        print(f"{status} {approval} - {description}")
        print(f"   Original: '{output[:60]}...'")
        
        if not result.approved or result.modifications:
            print(f"   Filtered: '{result.filtered_text[:60]}...'")
        
        if result.issues_found:
            print(f"   Issues: {', '.join(result.issues_found)}")
        
        if result.modifications:
            print(f"   Modifications: {', '.join(result.modifications)}")
        
        print()
    
    # Stats
    stats = output_filter.get_filter_stats()
    print("=" * 60)
    print("📊 FILTER STATISTICS")
    print("=" * 60)
    print(f"  Harmful pattern categories: {stats['harmful_pattern_categories']}")
    print(f"  Total harmful patterns: {stats['total_harmful_patterns']}")
    print(f"  Block threshold: {stats['block_threshold']}")
    print(f"  Sanitize threshold: {stats['sanitize_threshold']}")
    print(f"  Context patterns: {stats['context_protection']['total_patterns']}")
    
    print("\n" + "=" * 60)
    print(f"📊 Result: {passed}/{len(tests)} tests behaved as expected")
    print("=" * 60)
    print("Test complete!")

