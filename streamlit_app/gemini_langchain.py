"""
Gemini 2.5 Pro implementation using LangChain framework.
This module provides classes and utilities for integrating Google's Gemini 2.5 Pro
with LangChain for advanced language model operations.
"""

import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain.callbacks import StreamingStdOutCallbackHandler




class GeminiLangChain:
    """
    A comprehensive wrapper for Gemini 2.5 Pro using LangChain.
    Provides easy-to-use methods for various AI operations.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-exp",  # Updated to latest available model
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        streaming: bool = False
    ):
        """
        Initialize the Gemini LangChain wrapper.
        
        Args:
            api_key: Google API key. If None, will use GOOGLE_API_KEY from environment
            model_name: The Gemini model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_output_tokens: Maximum number of tokens to generate
            streaming: Whether to enable streaming responses
        """
        # Load environment variables
        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize the ChatGoogleGenerativeAI model
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            streaming=streaming,
            convert_system_message_to_human=True,  # Fix for SystemMessage support
            callbacks=[StreamingStdOutCallbackHandler()] if streaming else None
        )
        
        # Initialize memory for conversation
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Create conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False
        )
    
    def chat(self, message: str) -> str:
        """
        Simple chat interface.
        
        Args:
            message: The user's message
            
        Returns:
            The AI's response
        """
        try:
            response = self.conversation.predict(input=message)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_with_system_prompt(self, message: str, system_prompt: str) -> str:
        """
        Chat with a custom system prompt.
        
        Args:
            message: The user's message
            system_prompt: Custom system prompt to guide the AI's behavior
            
        Returns:
            The AI's response
        """
        try:
            # Create a chat prompt template
            chat_prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template("{input}")
            ])
            
            # Create chain with custom prompt
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            response = chain.run(input=message)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_text(self, text: str, analysis_type: str = "general") -> str:
        """
        Analyze text with specific focus.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (general, sentiment, summary, etc.)
            
        Returns:
            Analysis results
        """
        prompts = {
            "general": "Analyze the following text and provide insights:",
            "sentiment": "Analyze the sentiment of the following text:",
            "summary": "Provide a concise summary of the following text:",
            "keywords": "Extract key themes and keywords from the following text:",
            "tone": "Analyze the tone and writing style of the following text:"
        }
        
        system_prompt = prompts.get(analysis_type, prompts["general"])
        return self.chat_with_system_prompt(text, system_prompt)
    
    def generate_content(self, topic: str, content_type: str = "article", length: str = "medium") -> str:
        """
        Generate content on a specific topic.
        
        Args:
            topic: The topic to write about
            content_type: Type of content (article, blog, social_post, etc.)
            length: Length of content (short, medium, long)
            
        Returns:
            Generated content
        """
        length_guidelines = {
            "short": "Write a brief, concise piece (200-300 words)",
            "medium": "Write a comprehensive piece (500-800 words)",
            "long": "Write a detailed, in-depth piece (1000+ words)"
        }
        
        content_instructions = {
            "article": "Write a well-structured article",
            "blog": "Write an engaging blog post",
            "social_post": "Write a social media post",
            "email": "Write a professional email",
            "report": "Write a detailed report"
        }
        
        system_prompt = f"""
        {content_instructions.get(content_type, 'Write content')} about the topic: {topic}.
        {length_guidelines.get(length, 'Write appropriately sized content')}.
        Make it engaging, informative, and well-structured.
        """
        
        return self.chat_with_system_prompt(f"Topic: {topic}", system_prompt)
    
    def ask_with_context(self, question: str, context: str) -> str:
        """
        Ask a question with additional context.
        
        Args:
            question: The question to ask
            context: Additional context to help answer the question
            
        Returns:
            The AI's response
        """
        system_prompt = f"""
        Use the following context to answer the user's question:
        
        Context: {context}
        
        Answer the question based on the provided context. If the context doesn't 
        contain enough information, mention what additional information would be helpful.
        """
        
        return self.chat_with_system_prompt(question, system_prompt)
    
    def clear_memory(self):
        """Clear the conversation memory."""
        self.memory.clear()
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history."""
        return self.memory.chat_memory.messages
    
    def batch_process(self, prompts: List[str]) -> List[str]:
        """
        Process multiple prompts in batch.
        
        Args:
            prompts: List of prompts to process
            
        Returns:
            List of responses
        """
        responses = []
        for prompt in prompts:
            try:
                response = self.llm.predict(prompt)
                responses.append(response)
            except Exception as e:
                responses.append(f"Error processing prompt: {str(e)}")
        
        return responses


class GeminiChainBuilder:
    """
    Builder class for creating custom LangChain workflows with Gemini.
    """
    
    def __init__(self, gemini_client: GeminiLangChain):
        self.gemini_client = gemini_client
        self.chains = []
    
    def add_analysis_chain(self, analysis_type: str = "general"):
        """Add a text analysis chain."""
        def analyze(text: str) -> str:
            return self.gemini_client.analyze_text(text, analysis_type)
        
        self.chains.append(("analysis", analyze))
        return self
    
    def add_generation_chain(self, content_type: str = "article", length: str = "medium"):
        """Add a content generation chain."""
        def generate(topic: str) -> str:
            return self.gemini_client.generate_content(topic, content_type, length)
        
        self.chains.append(("generation", generate))
        return self
    
    def add_custom_chain(self, name: str, system_prompt: str):
        """Add a custom chain with specific system prompt."""
        def custom_process(input_text: str) -> str:
            return self.gemini_client.chat_with_system_prompt(input_text, system_prompt)
        
        self.chains.append((name, custom_process))
        return self
    
    def execute_pipeline(self, input_data: str) -> Dict[str, str]:
        """Execute all chains in the pipeline."""
        results = {}
        
        for chain_name, chain_func in self.chains:
            try:
                result = chain_func(input_data)
                results[chain_name] = result
            except Exception as e:
                results[chain_name] = f"Error in {chain_name}: {str(e)}"
        
        return results


# Convenience functions for quick usage
def quick_chat(message: str, api_key: Optional[str] = None) -> str:
    """Quick chat function for simple interactions."""
    client = GeminiLangChain(api_key=api_key)
    return client.chat(message)


def quick_analyze(text: str, analysis_type: str = "general", api_key: Optional[str] = None) -> str:
    """Quick analysis function."""
    client = GeminiLangChain(api_key=api_key)
    return client.analyze_text(text, analysis_type)


def quick_generate(topic: str, content_type: str = "article", api_key: Optional[str] = None) -> str:
    """Quick content generation function."""
    client = GeminiLangChain(api_key=api_key)
    return client.generate_content(topic, content_type)


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize the client
        gemini = GeminiLangChain()
        
        # Simple chat
        print("=== Simple Chat ===")
        response = gemini.chat("Hello! What can you help me with today?")
        print(f"Gemini: {response}")
        
        # Text analysis
        print("\n=== Text Analysis ===")
        sample_text = "This is an amazing product! I love how easy it is to use and the customer service is fantastic."
        sentiment = gemini.analyze_text(sample_text, "sentiment")
        print(f"Sentiment Analysis: {sentiment}")
        
        # Content generation
        print("\n=== Content Generation ===")
        article = gemini.generate_content("Artificial Intelligence in Healthcare", "article", "short")
        print(f"Generated Article: {article}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your GOOGLE_API_KEY environment variable!")
