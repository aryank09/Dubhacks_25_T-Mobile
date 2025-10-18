#!/usr/bin/env python3
"""
AI Brain for Navigation Assistant
Processes user queries and generates intelligent responses
"""

import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIBrain:
    def __init__(self, service='ollama'):
        """
        Initialize AI brain with specified service
        Args:
            service: 'openai', 'anthropic', 'gemini', or 'ollama' (local, FREE!)
        """
        self.service = service
        self.conversation_history = []
        
        # System prompt for the navigation assistant
        self.system_prompt = """You are a helpful navigation assistant for blind users. 
Your role is to:
1. Provide clear, concise navigation instructions
2. Describe surroundings and obstacles when asked
3. Answer questions about routes and directions
4. Be encouraging and patient
5. Prioritize safety in all navigation advice
6. Give audio-friendly responses (avoid complex formatting, be conversational)

Keep responses brief and to the point. Users rely on audio feedback, so clarity is crucial."""
        
        if service == 'ollama':
            # Local LLM - works offline, no API key needed!
            try:
                import ollama
                self.client = ollama
                logger.info("Ollama local LLM initialized")
            except ImportError:
                logger.error("Ollama library not installed. Run: pip install ollama")
                self.client = None
        
        elif service == 'openai':
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.warning("OpenAI API key not found. AI features will be limited.")
                    self.client = None
                else:
                    self.client = OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized")
            except ImportError:
                logger.error("OpenAI library not installed")
                self.client = None
                
        elif service == 'anthropic':
            try:
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    logger.warning("Anthropic API key not found. AI features will be limited.")
                    self.client = None
                else:
                    self.client = Anthropic(api_key=api_key)
                    logger.info("Anthropic client initialized")
            except ImportError:
                logger.error("Anthropic library not installed")
                self.client = None
        
        elif service == 'gemini':
            try:
                import google.generativeai as genai
                api_key = os.getenv('GEMINI_API_KEY')
                if not api_key:
                    logger.warning("Gemini API key not found. AI features will be limited.")
                    self.client = None
                else:
                    genai.configure(api_key=api_key)
                    self.client = genai.GenerativeModel('gemini-pro')
                    logger.info("Google Gemini initialized")
            except ImportError:
                logger.error("Google Generative AI library not installed")
                self.client = None
    
    def process_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        Process user query and generate response
        Args:
            user_input: User's spoken input
            context: Additional context (location, obstacles, etc.)
        Returns:
            AI-generated response
        """
        if not self.client:
            return self._fallback_response(user_input, context)
        
        # Add context to the query if available
        enhanced_input = user_input
        if context:
            context_str = self._format_context(context)
            enhanced_input = f"{user_input}\n\nContext: {context_str}"
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": enhanced_input
        })
        
        try:
            if self.service == 'ollama':
                response = self._query_ollama()
            elif self.service == 'openai':
                response = self._query_openai()
            elif self.service == 'anthropic':
                response = self._query_anthropic()
            elif self.service == 'gemini':
                response = self._query_gemini()
            else:
                response = "AI service not configured properly."
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Keep conversation history manageable (last 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query with AI: {e}")
            return self._fallback_response(user_input, context)
    
    def _query_ollama(self) -> str:
        """Query local Ollama LLM (offline, free!)"""
        # Format messages for Ollama
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        
        # Use phi or llama model (lightweight for Pi)
        try:
            response = self.client.chat(
                model='phi',  # or 'llama2', 'mistral', 'tinyllama'
                messages=messages,
                options={
                    'temperature': 0.7,
                    'num_predict': 100,  # Keep responses short
                }
            )
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            # Try alternative model
            try:
                response = self.client.chat(
                    model='tinyllama',  # Smallest model, fastest
                    messages=messages,
                )
                return response['message']['content'].strip()
            except:
                return self._fallback_response(
                    self.conversation_history[-1]['content'] if self.conversation_history else "",
                    None
                )
    
    def _query_openai(self) -> str:
        """Query OpenAI API"""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _query_anthropic(self) -> str:
        """Query Anthropic Claude API"""
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            system=self.system_prompt,
            messages=self.conversation_history
        )
        
        return response.content[0].text.strip()
    
    def _query_gemini(self) -> str:
        """Query Google Gemini API"""
        # Format conversation for Gemini
        prompt = f"{self.system_prompt}\n\n"
        for msg in self.conversation_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt += f"{role}: {msg['content']}\n"
        
        response = self.client.generate_content(prompt)
        return response.text.strip()
    
    def _format_context(self, context: Dict) -> str:
        """Format context dictionary into readable string"""
        parts = []
        if 'location' in context:
            parts.append(f"Current location: {context['location']}")
        if 'destination' in context:
            parts.append(f"Destination: {context['destination']}")
        if 'obstacles' in context:
            parts.append(f"Obstacles detected: {', '.join(context['obstacles'])}")
        if 'distance' in context:
            parts.append(f"Distance: {context['distance']}")
        if 'direction' in context:
            parts.append(f"Direction: {context['direction']}")
        
        return '; '.join(parts)
    
    def _fallback_response(self, user_input: str, context: Optional[Dict] = None) -> str:
        """Fallback response when AI is not available"""
        user_input_lower = user_input.lower()
        
        # Simple keyword-based responses
        if any(word in user_input_lower for word in ['where', 'location', 'position']):
            if context and 'location' in context:
                return f"You are currently at {context['location']}"
            return "I'm trying to determine your current location."
        
        elif any(word in user_input_lower for word in ['navigate', 'go to', 'take me']):
            return "Please specify your destination, and I'll guide you there."
        
        elif any(word in user_input_lower for word in ['obstacle', 'what\'s ahead', 'in front']):
            if context and 'obstacles' in context:
                return f"I detect the following: {', '.join(context['obstacles'])}"
            return "Scanning for obstacles ahead."
        
        elif any(word in user_input_lower for word in ['help', 'how', 'what can']):
            return "I can help you navigate, describe your surroundings, and answer questions about your route."
        
        else:
            return "I'm here to help you navigate. What would you like to know?"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")


if __name__ == "__main__":
    # Test AI brain
    brain = AIBrain(service='openai')
    
    # Test query
    response = brain.process_query(
        "Where am I and how do I get to the nearest coffee shop?",
        context={
            'location': '123 Main Street',
            'obstacles': ['bench', 'lamppost']
        }
    )
    print(f"AI Response: {response}")

