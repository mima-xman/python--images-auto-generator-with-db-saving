"""
Token Estimation Utilities
"""


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of tokens
    Rule of thumb: 1 token ≈ 4 characters in English
    More accurate: 1 token ≈ 0.75 words
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # Method 1: Character-based (conservative)
    char_based = len(text) // 4
    
    # Method 2: Word-based (more accurate for English)
    word_based = int(len(text.split()) * 1.3)
    
    # Use the higher estimate for safety
    return max(char_based, word_based)


def trim_chat_history(chat_history: list, system_prompt: str, max_messages: int, max_tokens: int, enable_trimming: bool) -> list:
    """
    Trim chat history to prevent token limit errors
    
    Args:
        chat_history: List of chat messages
        system_prompt: System prompt text
        max_messages: Maximum number of messages to keep
        max_tokens: Maximum token limit
        enable_trimming: Whether trimming is enabled
        
    Returns:
        Trimmed chat history
    """
    if not enable_trimming:
        print(f"📊 Chat history trimming: DISABLED")
        print(f"📊 Using full history: {len(chat_history)} messages")
        return chat_history
    
    if not chat_history:
        return chat_history
    
    # Calculate total estimated tokens
    total_tokens = estimate_tokens(system_prompt)
    for msg in chat_history:
        total_tokens += estimate_tokens(msg.get('content', ''))
    
    print(f"📊 Chat history: {len(chat_history)} messages, ~{total_tokens:,} tokens")
    
    # If under limit and message count is reasonable, return as is
    if total_tokens < max_tokens and len(chat_history) <= max_messages:
        print(f"✅ Within limits (Max: {max_messages} messages, {max_tokens:,} tokens)")
        return chat_history
    
    # Trim to last N messages (keep pairs of user+assistant)
    trimmed_history = chat_history[-max_messages:]
    
    # Ensure we start with a user message
    if trimmed_history and trimmed_history[0].get('role') == 'assistant':
        trimmed_history = trimmed_history[1:]
    
    # Recalculate tokens after trimming
    trimmed_tokens = estimate_tokens(system_prompt)
    for msg in trimmed_history:
        trimmed_tokens += estimate_tokens(msg.get('content', ''))
    
    print(f"✂️ TRIMMED: {len(chat_history)} → {len(trimmed_history)} messages")
    print(f"📊 Tokens: {total_tokens:,} → {trimmed_tokens:,} (Limit: {max_tokens:,})")
    
    # If still over limit, trim more aggressively
    if trimmed_tokens > max_tokens:
        print(f"⚠️ Still over limit! Trimming more aggressively...")
        
        # Remove messages until under limit
        while trimmed_tokens > max_tokens and len(trimmed_history) > 10:
            # Remove oldest pair (user + assistant)
            if len(trimmed_history) >= 2:
                removed_user = trimmed_history.pop(0)
                removed_assistant = trimmed_history.pop(0) if trimmed_history else None
                
                trimmed_tokens -= estimate_tokens(removed_user.get('content', ''))
                if removed_assistant:
                    trimmed_tokens -= estimate_tokens(removed_assistant.get('content', ''))
        
        print(f"✅ Final: {len(trimmed_history)} messages, ~{trimmed_tokens:,} tokens")
    
    return trimmed_history
