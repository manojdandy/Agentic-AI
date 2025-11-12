"""
Application Agent
Core AI agent using Google ADK (Gemini API)
Following SOLID: Single Responsibility & Dependency Inversion
"""

import os
from typing import Optional, Dict, List
from dataclasses import dataclass
from src.core.interfaces import IAgent
from src.core.models import AgentResponse
from src.agents.session_manager import Session


@dataclass
class AgentConfig:
    """
    Configuration for Application Agent
    
    Attributes:
        model_name: Model to use (e.g., gemini-2.0-flash-exp)
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens in response
        system_prompt: System instructions for agent
    """
    model_name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = "You are a helpful, safe, and secure AI assistant."


class ApplicationAgent(IAgent):
    """
    Application agent powered by Google ADK (Gemini)
    Following SOLID: Depends on IAgent interface
    Following DRY: Reusable agent logic
    
    Note: This implementation uses a mock interface for demo purposes.
    In production, replace with actual Google ADK integration.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, api_key: Optional[str] = None):
        """
        Initialize application agent
        
        Args:
            config: Agent configuration
            api_key: Google API key (reads from env if not provided)
        """
        self.config = config or AgentConfig()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # In production, initialize Google ADK client here
        # For now, we'll use a mock implementation
        self._initialize_client()
    
    def _initialize_client(self):
        """
        Initialize the Google ADK client
        
        In production, this would be:
        from google.generativeai import GenerativeModel
        self.client = GenerativeModel(self.config.model_name)
        """
        # Mock client for demo purposes
        self.client = MockGeminiClient(self.config)
    
    def process_message(
        self, 
        message: str, 
        session: Optional[Session] = None
    ) -> AgentResponse:
        """
        Process a user message through the agent
        
        Args:
            message: User message
            session: Optional session for context
            
        Returns:
            AgentResponse with agent's reply
        """
        try:
            # Build conversation history
            conversation = self._build_conversation(message, session)
            
            # Generate response using Google ADK
            response_text = self._generate_response(conversation)
            
            return AgentResponse(
                message=response_text,
                blocked=False,
                risk_score=0.0,
                metadata={
                    'model': self.config.model_name,
                    'temperature': self.config.temperature
                }
            )
        
        except Exception as e:
            # Handle errors gracefully
            return AgentResponse(
                message="I apologize, but I encountered an error processing your request.",
                blocked=True,
                risk_score=0.0,
                metadata={'error': str(e)}
            )
    
    def _build_conversation(
        self, 
        message: str, 
        session: Optional[Session] = None
    ) -> List[Dict]:
        """
        Build conversation history for the model (DRY)
        
        Args:
            message: Current user message
            session: Optional session for history
            
        Returns:
            List of conversation messages
        """
        conversation = [
            {'role': 'system', 'content': self.config.system_prompt}
        ]
        
        # Add conversation history if session exists
        if session:
            history = session.get_conversation_history(limit=10)  # Last 10 messages
            conversation.extend(history)
        
        # Add current message
        conversation.append({'role': 'user', 'content': message})
        
        return conversation
    
    def _generate_response(self, conversation: List[Dict]) -> str:
        """
        Generate response using Google ADK (DRY)
        
        Args:
            conversation: Conversation history
            
        Returns:
            Generated response text
        """
        # In production, this would be:
        # response = self.client.generate_content(
        #     conversation,
        #     generation_config={
        #         'temperature': self.config.temperature,
        #         'max_output_tokens': self.config.max_tokens
        #     }
        # )
        # return response.text
        
        # Mock implementation
        return self.client.generate(conversation)
    
    def update_system_prompt(self, new_prompt: str):
        """
        Update the system prompt
        
        Args:
            new_prompt: New system instructions
        """
        self.config.system_prompt = new_prompt


class MockGeminiClient:
    """
    Mock Gemini client for testing
    Replace with actual Google ADK in production
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def generate(self, conversation: List[Dict]) -> str:
        """
        Mock response generation
        
        Args:
            conversation: Conversation history
            
        Returns:
            Mock response
        """
        # Get last user message
        user_messages = [msg for msg in conversation if msg['role'] == 'user']
        if not user_messages:
            return "I'm here to help!"
        
        last_message = user_messages[-1]['content'].lower()
        
        # Simple pattern matching for demo
        if 'python' in last_message:
            return "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data science, automation, and more!"
        
        elif 'hello' in last_message or 'hi' in last_message:
            return "Hello! How can I assist you today?"
        
        elif 'help' in last_message:
            return "I'm here to help! You can ask me questions about programming, general knowledge, or anything else you'd like to know."
        
        elif 'capital' in last_message and 'france' in last_message:
            return "The capital of France is Paris."
        
        elif 'weather' in last_message:
            return "I don't have access to real-time weather data, but I'd be happy to help you with other questions!"
        
        elif '?' in last_message:
            return f"That's an interesting question! Based on what you've asked, I can provide information and assistance. How can I help you further?"
        
        else:
            return "I understand. I'm here to assist you with any questions or tasks you have. What would you like to know?"


# Demo/Test
if __name__ == "__main__":
    """
    Demo: Test the application agent
    Run: python -m src.agents.application_agent
    """
    from src.agents.session_manager import SessionManager
    
    print("=" * 60)
    print("🤖 APPLICATION AGENT TEST")
    print("=" * 60)
    
    # Create agent
    config = AgentConfig(
        model_name="gemini-2.0-flash-exp",
        temperature=0.7,
        system_prompt="You are a helpful and friendly AI assistant."
    )
    
    agent = ApplicationAgent(config)
    print(f"\n✅ Initialized agent")
    print(f"   Model: {config.model_name}")
    print(f"   Temperature: {config.temperature}")
    
    # Create session
    session_manager = SessionManager()
    session = session_manager.create_session()
    
    # Test conversations
    test_messages = [
        "Hello!",
        "What is Python?",
        "What's the capital of France?",
        "Can you help me?",
    ]
    
    print(f"\n💬 Testing conversations:\n")
    
    for user_msg in test_messages:
        # Process message
        response = agent.process_message(user_msg, session)
        
        # Add to session
        session.add_message("user", user_msg)
        session.add_message("assistant", response.message)
        
        # Display
        print(f"👤 User: {user_msg}")
        print(f"🤖 Agent: {response.message[:100]}...")
        print(f"   Blocked: {response.blocked}, Risk: {response.risk_score}")
        print()
    
    print("=" * 60)
    print(f"📊 Session statistics:")
    print(f"   Total messages: {len(session.messages)}")
    print(f"   Session ID: {session.session_id}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

