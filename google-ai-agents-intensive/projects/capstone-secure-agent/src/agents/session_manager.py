"""
Session Manager
Manages conversation sessions and context
Following SOLID: Single Responsibility (only session management)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """
    A single message in a conversation
    
    Attributes:
        role: Message role (user, assistant, system)
        content: Message content
        timestamp: When message was created
        metadata: Additional message metadata
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Session:
    """
    A conversation session
    
    Attributes:
        session_id: Unique session identifier
        messages: List of messages in session
        context: Session context/state
        created_at: When session was created
        last_activity: Last activity timestamp
    """
    session_id: str
    messages: List[Message] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to the session
        
        Args:
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get messages from session
        
        Args:
            limit: Optional limit on number of messages
            
        Returns:
            List of messages
        """
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history in dict format
        
        Args:
            limit: Optional limit on number of messages
            
        Returns:
            List of message dictionaries
        """
        messages = self.get_messages(limit)
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
        self.last_activity = datetime.now()


class SessionManager:
    """
    Manages multiple conversation sessions
    Following DRY: Centralized session management
    """
    
    def __init__(self, max_sessions: int = 1000):
        """
        Initialize session manager
        
        Args:
            max_sessions: Maximum number of concurrent sessions
        """
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = max_sessions
    
    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Create a new session
        
        Args:
            session_id: Optional session ID (generates if not provided)
            
        Returns:
            Created session
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Check if session already exists
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Enforce max sessions limit
        if len(self.sessions) >= self.max_sessions:
            self._cleanup_old_sessions()
        
        session = Session(session_id=session_id)
        self.sessions[session_id] = session
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session or None if not found
        """
        return self.sessions.get(session_id)
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Get existing session or create new one
        
        Args:
            session_id: Optional session ID
            
        Returns:
            Session
        """
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        return self.create_session(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def _cleanup_old_sessions(self, keep_count: int = 100):
        """
        Clean up old sessions to free memory (DRY)
        
        Args:
            keep_count: Number of sessions to keep
        """
        # Sort sessions by last activity
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].last_activity,
            reverse=True
        )
        
        # Keep only recent sessions
        self.sessions = dict(sorted_sessions[:keep_count])
    
    def get_session_count(self) -> int:
        """
        Get total number of active sessions
        
        Returns:
            Session count
        """
        return len(self.sessions)
    
    def get_stats(self) -> Dict:
        """
        Get session statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.sessions:
            return {
                'total_sessions': 0,
                'total_messages': 0,
                'avg_messages_per_session': 0
            }
        
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        
        return {
            'total_sessions': len(self.sessions),
            'total_messages': total_messages,
            'avg_messages_per_session': total_messages / len(self.sessions) if self.sessions else 0
        }


# Demo/Test
if __name__ == "__main__":
    """
    Demo: Test the session manager
    Run: python -m src.agents.session_manager
    """
    print("=" * 60)
    print("💬 SESSION MANAGER TEST")
    print("=" * 60)
    
    manager = SessionManager()
    
    # Create sessions
    session1 = manager.create_session()
    session2 = manager.create_session("custom-session-id")
    
    print(f"\n✅ Created {manager.get_session_count()} sessions")
    print(f"   Session 1 ID: {session1.session_id}")
    print(f"   Session 2 ID: {session2.session_id}")
    
    # Add messages
    session1.add_message("user", "Hello!")
    session1.add_message("assistant", "Hi! How can I help?")
    session1.add_message("user", "What is Python?")
    
    session2.add_message("user", "Test message")
    
    print(f"\n✅ Added messages")
    print(f"   Session 1: {len(session1.messages)} messages")
    print(f"   Session 2: {len(session2.messages)} messages")
    
    # Get conversation history
    history = session1.get_conversation_history(limit=2)
    print(f"\n✅ Recent conversation (last 2 messages):")
    for msg in history:
        print(f"   {msg['role']}: {msg['content']}")
    
    # Get stats
    stats = manager.get_stats()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Delete session
    deleted = manager.delete_session(session2.session_id)
    print(f"\n✅ Deleted session: {deleted}")
    print(f"   Remaining sessions: {manager.get_session_count()}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

