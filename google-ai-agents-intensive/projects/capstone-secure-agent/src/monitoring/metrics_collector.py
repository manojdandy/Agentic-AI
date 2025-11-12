"""
Metrics Collector
Tracks performance and security metrics
Following SOLID: Single Responsibility (only metrics)
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class MetricsSummary:
    """
    Summary of collected metrics
    
    Attributes:
        total_requests: Total number of requests
        successful_requests: Number of successful requests
        blocked_requests: Number of blocked requests
        avg_latency_ms: Average latency in milliseconds
        avg_risk_score: Average risk score
        attacks_by_type: Count of attacks by type
        p50_latency_ms: 50th percentile latency
        p95_latency_ms: 95th percentile latency
        p99_latency_ms: 99th percentile latency
    """
    total_requests: int = 0
    successful_requests: int = 0
    blocked_requests: int = 0
    avg_latency_ms: float = 0.0
    avg_risk_score: float = 0.0
    attacks_by_type: Dict[str, int] = field(default_factory=dict)
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    def get_block_rate(self) -> float:
        """Calculate block rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.blocked_requests / self.total_requests) * 100
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


class MetricsCollector:
    """
    Collects and aggregates system metrics
    Following DRY: Centralized metrics collection
    """
    
    def __init__(self, window_size: int = 10000):
        """
        Initialize metrics collector
        
        Args:
            window_size: Maximum number of metrics to keep in memory
        """
        self.window_size = window_size
        
        # Metrics storage
        self.latencies: List[float] = []
        self.risk_scores: List[float] = []
        self.request_outcomes: List[str] = []  # 'success' or 'blocked'
        self.attack_types: List[str] = []
        self.timestamps: List[datetime] = []
        
        # Counters
        self.total_requests = 0
        self.successful_requests = 0
        self.blocked_requests = 0
    
    def record_request(
        self,
        latency_ms: float,
        risk_score: float,
        blocked: bool,
        attack_type: Optional[str] = None
    ):
        """
        Record a request's metrics
        
        Args:
            latency_ms: Request latency in milliseconds
            risk_score: Risk assessment score
            blocked: Whether request was blocked
            attack_type: Type of attack (if detected)
        """
        self.total_requests += 1
        
        # Store metrics
        self.latencies.append(latency_ms)
        self.risk_scores.append(risk_score)
        self.timestamps.append(datetime.now())
        
        # Record outcome
        if blocked:
            self.blocked_requests += 1
            self.request_outcomes.append('blocked')
            if attack_type:
                self.attack_types.append(attack_type)
        else:
            self.successful_requests += 1
            self.request_outcomes.append('success')
        
        # Trim if window exceeded
        self._trim_metrics()
    
    def get_summary(self) -> MetricsSummary:
        """
        Get metrics summary
        
        Returns:
            MetricsSummary with aggregated metrics
        """
        if not self.latencies:
            return MetricsSummary()
        
        # Calculate averages
        avg_latency = sum(self.latencies) / len(self.latencies)
        avg_risk = sum(self.risk_scores) / len(self.risk_scores)
        
        # Calculate percentiles
        sorted_latencies = sorted(self.latencies)
        p50 = self._percentile(sorted_latencies, 50)
        p95 = self._percentile(sorted_latencies, 95)
        p99 = self._percentile(sorted_latencies, 99)
        
        # Count attacks by type
        attacks_by_type = {}
        for attack_type in self.attack_types:
            attacks_by_type[attack_type] = attacks_by_type.get(attack_type, 0) + 1
        
        return MetricsSummary(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            blocked_requests=self.blocked_requests,
            avg_latency_ms=avg_latency,
            avg_risk_score=avg_risk,
            attacks_by_type=attacks_by_type,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99
        )
    
    def get_recent_latencies(self, limit: int = 100) -> List[float]:
        """
        Get recent latency measurements
        
        Args:
            limit: Number of measurements to return
            
        Returns:
            List of recent latencies
        """
        return self.latencies[-limit:]
    
    def get_requests_per_time_window(
        self,
        window_minutes: int = 60
    ) -> Dict[str, int]:
        """
        Get request counts in time window
        
        Args:
            window_minutes: Time window in minutes
            
        Returns:
            Dictionary with request counts
        """
        if not self.timestamps:
            return {
                'total': 0,
                'successful': 0,
                'blocked': 0
            }
        
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        
        # Count requests after cutoff
        total = 0
        successful = 0
        blocked = 0
        
        for timestamp, outcome in zip(self.timestamps, self.request_outcomes):
            if timestamp >= cutoff:
                total += 1
                if outcome == 'success':
                    successful += 1
                else:
                    blocked += 1
        
        return {
            'total': total,
            'successful': successful,
            'blocked': blocked,
            'requests_per_minute': total / window_minutes if window_minutes > 0 else 0
        }
    
    def get_attack_distribution(self) -> Dict[str, float]:
        """
        Get distribution of attack types as percentages
        
        Returns:
            Dictionary of attack type percentages
        """
        if not self.attack_types:
            return {}
        
        total = len(self.attack_types)
        distribution = {}
        
        for attack_type in set(self.attack_types):
            count = self.attack_types.count(attack_type)
            distribution[attack_type] = (count / total) * 100
        
        return distribution
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.latencies = []
        self.risk_scores = []
        self.request_outcomes = []
        self.attack_types = []
        self.timestamps = []
        self.total_requests = 0
        self.successful_requests = 0
        self.blocked_requests = 0
    
    def _trim_metrics(self):
        """Trim metrics to window size (DRY)"""
        if len(self.latencies) > self.window_size:
            self.latencies = self.latencies[-self.window_size:]
            self.risk_scores = self.risk_scores[-self.window_size:]
            self.request_outcomes = self.request_outcomes[-self.window_size:]
            self.timestamps = self.timestamps[-self.window_size:]
            
            # Trim attack types (proportionally)
            if len(self.attack_types) > self.window_size // 2:
                self.attack_types = self.attack_types[-(self.window_size // 2):]
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """
        Calculate percentile (DRY)
        
        Args:
            sorted_data: Sorted list of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not sorted_data:
            return 0.0
        
        index = int((percentile / 100) * len(sorted_data))
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]


# Demo/Test
if __name__ == "__main__":
    """
    Demo: Test the metrics collector
    Run: python -m src.monitoring.metrics_collector
    """
    import random
    
    print("=" * 60)
    print("📊 METRICS COLLECTOR TEST")
    print("=" * 60)
    
    # Create collector
    collector = MetricsCollector()
    
    print("\n✅ Created metrics collector")
    
    # Simulate requests
    print(f"\n📋 Simulating 100 requests:\n")
    
    attack_types = [
        'instruction_override',
        'prompt_extraction',
        'jailbreak',
        'role_manipulation'
    ]
    
    for i in range(100):
        # Simulate varying latencies and risk
        latency = random.uniform(0.5, 50.0)
        risk_score = random.random()
        
        # 20% chance of being blocked
        blocked = risk_score > 0.7
        attack_type = random.choice(attack_types) if blocked else None
        
        collector.record_request(
            latency_ms=latency,
            risk_score=risk_score,
            blocked=blocked,
            attack_type=attack_type
        )
    
    print(f"✅ Recorded 100 requests")
    
    # Get summary
    summary = collector.get_summary()
    
    print("\n" + "=" * 60)
    print("📊 METRICS SUMMARY")
    print("=" * 60)
    print(f"  Total requests: {summary.total_requests}")
    print(f"  Successful: {summary.successful_requests} ({summary.get_success_rate():.1f}%)")
    print(f"  Blocked: {summary.blocked_requests} ({summary.get_block_rate():.1f}%)")
    print(f"\n  Performance:")
    print(f"    Avg latency: {summary.avg_latency_ms:.2f}ms")
    print(f"    P50 latency: {summary.p50_latency_ms:.2f}ms")
    print(f"    P95 latency: {summary.p95_latency_ms:.2f}ms")
    print(f"    P99 latency: {summary.p99_latency_ms:.2f}ms")
    print(f"\n  Security:")
    print(f"    Avg risk score: {summary.avg_risk_score:.2f}")
    
    if summary.attacks_by_type:
        print(f"\n  Attacks by type:")
        for attack_type, count in summary.attacks_by_type.items():
            print(f"    {attack_type}: {count}")
    
    # Attack distribution
    distribution = collector.get_attack_distribution()
    if distribution:
        print(f"\n  Attack distribution:")
        for attack_type, percentage in distribution.items():
            print(f"    {attack_type}: {percentage:.1f}%")
    
    # Recent activity
    recent = collector.get_requests_per_time_window(window_minutes=60)
    print(f"\n  Last 60 minutes:")
    print(f"    Total: {recent['total']}")
    print(f"    Requests/min: {recent['requests_per_minute']:.2f}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

