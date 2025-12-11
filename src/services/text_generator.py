"""
Text Generator Service
Handles metadata generation using AI
"""

from bytez import Bytez
from src.config.settings import TEXT_MODEL
from src.utils.text_extractor import extract_metadata


class TextGeneratorService:
    """Service for generating text/metadata using AI"""
    
    def __init__(self, api_key_manager, message_repo, chat_manager, config):
        """
        Initialize text generator service
        
        Args:
            api_key_manager: API key manager instance
            message_repo: Message repository
            chat_manager: Chat manager
            config: Generator configuration
        """
        self.api_key_manager = api_key_manager
        self.message_repo = message_repo
        self.chat_manager = chat_manager
        self.config = config
        self.model_name = TEXT_MODEL
        self.generator_type = "text"
    
    def generate_metadata(self, chat_uuid: str, chat_history: list):
        """
        Generate metadata using AI
        
        Args:
            chat_uuid: Chat UUID
            chat_history: Current chat history
            
        Returns:
            Tuple of (metadata, error, chat_history, message_id, api_key)
        """
        api_key_id = None
        api_key = None
        
        try:
            print("🤖 Generating metadata...")
            
            system_prompt = self.chat_manager.load_prompt()
            if not system_prompt:
                return None, "Failed to load prompt", chat_history, None, None
            
            # Trim chat history
            trimmed_history = self.chat_manager.trim_history(chat_history, system_prompt)
            
            # Retry loop
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Acquire key
                    api_key_id, api_key = self.api_key_manager.acquire_key(self.model_name, self.generator_type)
                    
                    if not api_key:
                        print("❌ No available chat API keys!")
                        return None, "No available chat API keys", chat_history, None, None
                    
                    sdk = Bytez(api_key)
                    chat_model = sdk.model(self.model_name)
                    
                    # Build messages
                    user_message = ""
                    if not trimmed_history:
                        print("📝 First generation - sending full prompt")
                        user_message = system_prompt
                        trimmed_history.append({"role": "user", "content": user_message})
                    else:
                        print("🔄 Continuing conversation - requesting new generation")
                        user_message = "Give me a new one"
                        trimmed_history.append({"role": "user", "content": user_message})
                    
                    # Generate
                    output, error, _ = chat_model.run(trimmed_history)
                    
                    if error:
                        print(f"❌ Error with key: {error}")
                        
                        # Log failed usage
                        used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                        self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, False, str(error))
                        
                        # Handle token limit error
                        if "tokens exceed" in str(error).lower() or "token limit" in str(error).lower():
                            print(f"⚠️ TOKEN LIMIT HIT! Forcing aggressive history trim...")
                            aggressive_limit = self.config.max_history_messages // 2
                            chat_history = chat_history[-aggressive_limit:]
                            print(f"✂️ EMERGENCY TRIM: Reduced to {len(chat_history)} messages")
                            trimmed_history.pop()
                            self.api_key_manager.release_key(api_key)
                            continue
                        
                        # Regular error
                        trimmed_history.pop()
                        self.api_key_manager.mark_key_expired_and_release(api_key, self.model_name)
                        continue
                    
                    # Success
                    content = output.get('content', '') if isinstance(output, dict) else str(output)
                    print(f"✅ Generated metadata successfully")
                    
                    # Add to history
                    trimmed_history.append({"role": "assistant", "content": content})
                    if not chat_history or chat_history[-1].get('content') != user_message:
                        chat_history.append({"role": "user", "content": user_message})
                    chat_history.append({"role": "assistant", "content": content})
                    
                    # Save to database
                    message_id = self.message_repo.save_message(chat_uuid, user_message, content, api_key)
                    
                    # Extract metadata
                    metadata = extract_metadata(content)
                    
                    # Validate
                    if not all([metadata.get('prompt'), metadata.get('title')]):
                        print("⚠️ Extraction failed")
                        self.message_repo.delete_message(message_id)
                        if len(trimmed_history) >= 2:
                            trimmed_history.pop()
                            trimmed_history.pop()
                        if len(chat_history) >= 2:
                            chat_history.pop()
                            chat_history.pop()
                        
                        used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                        self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, False, "Extraction failed")
                        self.api_key_manager.release_key(api_key)
                        return None, "Extraction failed", chat_history, None, None
                    
                    # Log success and release
                    used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                    self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, True, None)
                    self.api_key_manager.release_key(api_key)
                    
                    return metadata, None, chat_history, message_id, api_key
                    
                except Exception as e:
                    print(f"❌ Exception during generation: {e}")
                    if trimmed_history and trimmed_history[-1].get('role') == 'user':
                        trimmed_history.pop()
                    
                    if api_key:
                        used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                        self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, False, str(e))
                        self.api_key_manager.release_key(api_key)
                    continue
            
            print("❌ All retry attempts failed!")
            return None, "All retry attempts exhausted", chat_history, None, None
            
        except Exception as e:
            print(f"❌ Unexpected error in generate_metadata: {e}")
            if api_key:
                self.api_key_manager.release_key(api_key)
            return None, str(e), chat_history, None, None
