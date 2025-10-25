import google.generativeai as genai
from openai import OpenAI
from backend.config import get_settings
from backend.models import ChatMessage, ChatResponse
from typing import List
from datetime import datetime


def get_chat_system_prompt(document_context: str = None) -> str:
    """
    Generate system prompt for chat interaction.
    
    This is the MOST IMPORTANT part - defines how the AI assistant behaves.
    """
    base_prompt = """You are ProspectAI Assistant, an expert business analyst and financial strategist.

Your core capabilities:
- Deep analysis of business models, market opportunities, and financial metrics
- Strategic thinking about market entry, growth strategies, and competitive positioning
- Financial modeling including TAM/SAM/SOM, ROI, unit economics, and profitability
- Risk assessment and mitigation strategies
- Actionable recommendations based on data-driven insights

Your personality:
- Professional yet approachable
- Concise but comprehensive when needed
- Data-driven and analytical
- Proactive in suggesting next steps
- Honest about limitations and assumptions

Response guidelines:
- Keep responses focused and actionable
- Use bullet points for clarity
- Include specific numbers when possible
- Ask clarifying questions when needed
- Reference the analyzed document when relevant
"""
    
    if document_context:
        base_prompt += f"""

CONTEXT FROM ANALYZED DOCUMENT:
{document_context}

You have full access to this analysis. Reference specific metrics, insights, and recommendations 
when answering questions. Help users understand implications and explore scenarios.
"""
    
    return base_prompt


def chat_with_gemini(
    message: str,
    conversation_history: List[ChatMessage],
    document_context: str = None
) -> ChatResponse:
    """Handle chat interaction using Gemini 2.5 Flash"""
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')  # Latest Gemini 2.5 Flash
    
    # Build conversation context
    system_prompt = get_chat_system_prompt(document_context)
    
    # Format conversation history
    conversation_text = f"{system_prompt}\n\n"
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        role_label = "User" if msg.role == "user" else "Assistant"
        conversation_text += f"{role_label}: {msg.content}\n\n"
    
    conversation_text += f"User: {message}\n\nAssistant:"
    
    # Generate response
    response = model.generate_content(conversation_text)
    
    return ChatResponse(
        message=response.text,
        timestamp=datetime.utcnow()
    )


def chat_with_openai(
    message: str,
    conversation_history: List[ChatMessage],
    document_context: str = None
) -> ChatResponse:
    """Handle chat interaction using OpenAI o1 (best reasoning model)"""
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    
    # Build messages - o1 doesn't support system messages
    # Incorporate system prompt into first user message
    messages = []
    
    # Add system context as part of conversation
    system_context = get_chat_system_prompt(document_context)
    
    # Add conversation history with system context in first message
    if not conversation_history:
        messages.append({
            "role": "user",
            "content": f"{system_context}\n\nUser Question: {message}"
        })
    else:
        # Add history
        for i, msg in enumerate(conversation_history[-10:]):
            if i == 0 and msg.role == "user":
                # Inject system context into first message
                messages.append({
                    "role": "user",
                    "content": f"{system_context}\n\n{msg.content}"
                })
            else:
                messages.append({
                    "role": msg.role if msg.role != "assistant" else "assistant",
                    "content": msg.content
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
    
    # Generate response using o1 (no temperature control)
    response = client.chat.completions.create(
        model="o1",  # Best reasoning model
        messages=messages
    )
    
    return ChatResponse(
        message=response.choices[0].message.content,
        timestamp=datetime.utcnow(),
        tokens_used=response.usage.total_tokens if response.usage else None
    )


def process_chat_request(
    message: str,
    provider: str,
    conversation_history: List[ChatMessage],
    document_context: str = None
) -> ChatResponse:
    """
    Main chat processing function with provider routing.
    
    Args:
        message: User's message
        provider: 'gemini' or 'openai'
        conversation_history: Previous conversation messages
        document_context: Analyzed document summary for context
    
    Returns:
        ChatResponse with assistant's reply
    """
    if provider.lower() == "openai":
        return chat_with_openai(message, conversation_history, document_context)
    else:
        return chat_with_gemini(message, conversation_history, document_context)
