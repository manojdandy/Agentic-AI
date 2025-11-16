"""
Application Agent
Core AI agent using Google ADK (Gemini API)
Following SOLID: Single Responsibility & Dependency Inversion

Supports both Mock and Real Gemini clients:
- Mock: For testing without API costs (USE_MOCK_GEMINI=true)
- Real: For production with actual Gemini API (USE_MOCK_GEMINI=false)
"""

import os
from typing import Optional, Dict, List
from dataclasses import dataclass
from src.core.interfaces import IAgent
from src.core.models import AgentResponse
from src.agents.session_manager import Session
from src.core.config import settings


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
    
    Supports both Mock and Real Gemini clients via USE_MOCK_GEMINI config flag:
    - Mock: Fast, free testing (USE_MOCK_GEMINI=true)
    - Real: Production-grade AI with actual Gemini API (USE_MOCK_GEMINI=false)
    """
    
    def __init__(self, config: Optional[AgentConfig] = None, api_key: Optional[str] = None, use_mock: Optional[bool] = None):
        """
        Initialize application agent
        
        Args:
            config: Agent configuration
            api_key: Google API key (reads from env if not provided)
            use_mock: Override USE_MOCK_GEMINI setting (optional)
        """
        self.config = config or AgentConfig()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or settings.gemini_api_key
        
        # Determine whether to use mock or real client
        self.use_mock = use_mock if use_mock is not None else settings.use_mock_gemini
        
        # Initialize appropriate client
        self._initialize_client()
    
    def _initialize_client(self):
        """
        Initialize either Mock or Real Gemini client based on configuration
        
        Mock Client: For testing, no API costs
        Real Client: For production, uses actual Gemini API
        """
        if self.use_mock:
            # Use mock for testing
            print("🤖 Using MockGeminiClient (testing mode)")
            self.client = MockGeminiClient(self.config)
            self.client_type = "mock"
        else:
            # Use real Gemini API
            print("🚀 Using Real Gemini API (production mode)")
            try:
                self.client = RealGeminiClient(self.config, self.api_key)
                self.client_type = "real"
            except Exception as e:
                print(f"⚠️ Failed to initialize Real Gemini client: {e}")
                print("⚠️ Falling back to MockGeminiClient")
                self.client = MockGeminiClient(self.config)
                self.client_type = "mock_fallback"
    
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


class RealGeminiClient:
    """
    Real Gemini API client for production use
    Uses Google's Gemini API for actual AI responses
    """
    
    def __init__(self, config: AgentConfig, api_key: str):
        """
        Initialize real Gemini client
        
        Args:
            config: Agent configuration
            api_key: Google Gemini API key
        """
        self.config = config
        self.api_key = api_key
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for real Gemini client. Set USE_MOCK_GEMINI=true to use mock instead.")
        
        # Import and initialize Gemini
        try:
            from google import genai
            from google.genai import types
            
            self.genai = genai
            self.types = types
            self.client = genai.Client(api_key=self.api_key)
            
            print(f"✅ Initialized Gemini client with model: {self.config.model_name}")
            
        except ImportError as e:
            raise ImportError(
                "google-genai package not installed. "
                "Install with: pip install google-genai\n"
                f"Error: {e}"
            )
    
    def generate(self, conversation: List[Dict]) -> str:
        """
        Generate response using real Gemini API
        
        Args:
            conversation: Conversation history with role/content
            
        Returns:
            Generated response from Gemini
        """
        try:
            # Convert conversation format for Gemini
            # Gemini expects system prompt + user/model messages
            contents = self._format_conversation(conversation)
            
            # Generate response with Gemini
            response = self.client.models.generate_content(
                model=self.config.model_name,
                contents=contents,
                config=self.types.GenerateContentConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                    safety_settings=[
                        self.types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_NONE"
                        ),
                        self.types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_NONE"
                        ),
                        self.types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_NONE"
                        ),
                        self.types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_NONE"
                        )
                    ]
                )
            )
            
            # Extract text from response
            if response and response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            print(f"⚠️ Error generating response with Gemini: {e}")
            return f"I encountered an error processing your request. Please try again."
    
    def _format_conversation(self, conversation: List[Dict]) -> str:
        """
        Format conversation for Gemini API
        
        Args:
            conversation: List of {role, content} dicts
            
        Returns:
            Formatted conversation string for Gemini
        """
        # Extract system prompt
        system_prompt = None
        messages = []
        
        for msg in conversation:
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'system':
                system_prompt = content
            elif role == 'user' or role == 'assistant':
                messages.append(f"{role.upper()}: {content}")
        
        # Combine system prompt with messages
        if system_prompt:
            formatted = f"SYSTEM: {system_prompt}\n\n" + "\n\n".join(messages)
        else:
            formatted = "\n\n".join(messages)
        
        return formatted


class MockGeminiClient:
    """
    Mock Gemini client for testing without API costs
    Use by setting USE_MOCK_GEMINI=true in .env
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    def generate(self, conversation: List[Dict]) -> str:
        """
        Mock response generation with simple pattern matching
        
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

