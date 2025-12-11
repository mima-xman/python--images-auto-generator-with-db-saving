"""
Chat Manager Service
Handles chat history and prompt management
"""

import os
from src.utils.token_estimator import estimate_tokens, trim_chat_history


class ChatManager:
    """Manages chat history and prompts"""
    
    def __init__(self, config):
        """
        Initialize chat manager
        
        Args:
            config: Generator configuration
        """
        self.config = config
    
    def load_prompt(self, prompt_file: str = None) -> str:
        """
        Load system prompt from file
        
        Args:
            prompt_file: Prompt filename (optional, uses config if not provided)
            
        Returns:
            Prompt content or None if failed
        """
        try:
            file_name = prompt_file or self.config.prompt_file_name
            file_path = os.path.join(self.config.prompts_dir, file_name)
            
            if not os.path.exists(self.config.prompts_dir):
                print(f"❌ Error: '{self.config.prompts_dir}/' directory not found!")
                os.makedirs(self.config.prompts_dir, exist_ok=True)
                return None
            
            if not os.path.exists(file_path):
                print(f"❌ Error: Prompt file '{file_path}' not found!")
                prompt_files = [f for f in os.listdir(self.config.prompts_dir) if f.endswith('.txt')]
                if prompt_files:
                    print(f"💡 Available prompts:")
                    for f in prompt_files:
                        print(f"   - {f}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
            
            print(f"✅ Loaded prompt from: {file_path}")
            print(f"📏 Prompt length: {len(prompt_content)} characters (~{estimate_tokens(prompt_content)} tokens)")
            
            return prompt_content
            
        except Exception as e:
            print(f"❌ Error reading prompt file: {e}")
            return None
    
    def trim_history(self, chat_history: list, system_prompt: str) -> list:
        """
        Trim chat history to prevent token limit errors
        
        Args:
            chat_history: List of chat messages
            system_prompt: System prompt text
            
        Returns:
            Trimmed chat history
        """
        return trim_chat_history(
            chat_history,
            system_prompt,
            self.config.max_history_messages,
            self.config.max_tokens_limit,
            self.config.enable_history_trimming
        )
