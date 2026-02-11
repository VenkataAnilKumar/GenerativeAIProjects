"""Code completion service"""
from typing import Dict, Any, Optional
from ..models.base import BaseModelProvider, ChatRequest, Message


class CodeCompletionService:
    """Service for code completion tasks"""
    
    def __init__(self, model_provider: BaseModelProvider):
        self.model_provider = model_provider
    
    async def complete_code(
        self, 
        code: str,
        language: str = "python",
        instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Complete code snippet"""
        system_prompt = f"You are an expert {language} programmer. Complete the following code."
        
        if instruction:
            user_message = f"Instruction: {instruction}\n\nCode:\n```{language}\n{code}\n```"
        else:
            user_message = f"Complete this code:\n```{language}\n{code}\n```"
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_message),
        ]
        
        chat_request = ChatRequest(messages=messages, temperature=0.2)
        response = await self.model_provider.chat(chat_request)
        
        return {
            "completion": response.content,
            "model": response.model,
            "usage": response.usage,
        }
    
    async def explain_code(
        self, 
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Explain code snippet"""
        messages = [
            Message(role="system", content=f"You are an expert {language} programmer. Explain code clearly and concisely."),
            Message(role="user", content=f"Explain this code:\n```{language}\n{code}\n```"),
        ]
        
        chat_request = ChatRequest(messages=messages, temperature=0.3)
        response = await self.model_provider.chat(chat_request)
        
        return {
            "explanation": response.content,
            "model": response.model,
            "usage": response.usage,
        }
    
    async def fix_code(
        self, 
        code: str,
        error: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Fix code with error"""
        messages = [
            Message(role="system", content=f"You are an expert {language} programmer. Fix code errors."),
            Message(role="user", content=f"Fix this code:\n```{language}\n{code}\n```\n\nError: {error}"),
        ]
        
        chat_request = ChatRequest(messages=messages, temperature=0.2)
        response = await self.model_provider.chat(chat_request)
        
        return {
            "fixed_code": response.content,
            "model": response.model,
            "usage": response.usage,
        }
    
    async def generate_code(
        self, 
        description: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Generate code from description"""
        messages = [
            Message(role="system", content=f"You are an expert {language} programmer. Generate clean, efficient code."),
            Message(role="user", content=f"Generate {language} code for: {description}"),
        ]
        
        chat_request = ChatRequest(messages=messages, temperature=0.3)
        response = await self.model_provider.chat(chat_request)
        
        return {
            "code": response.content,
            "model": response.model,
            "usage": response.usage,
        }
