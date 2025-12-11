"""
Configuration Management
Supports both environment variables and programmatic configuration
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class GeneratorConfig:
    """Configuration for image generator"""
    
    # MongoDB Configuration
    mongodb_uri: Optional[str] = None  # For application data (loaded from env if not provided)
    bytez_keys_mongodb_uri: Optional[str] = None  # For API keys (falls back to mongodb_uri if not set)
    db_name: str = "auto_image_generator"
    bytez_keys_db_name: str = "bytez_keys_manager"
    
    # Generator Configuration
    generator_name: str = "images-auto-generator"
    
    # Chat Configuration
    chat_uuid: Optional[str] = None
    chat_title: Optional[str] = None
    
    # Prompt Configuration
    prompt_file_name: str = "prompt.txt"
    prompts_dir: str = "prompts"
    
    # Collection Names
    collection_images: str = "generated_images"
    collection_chats: str = "chats"
    collection_chat_messages: str = "chat_messages"
    
    # Chat History Configuration
    enable_history_trimming: bool = True
    max_history_messages: int = 400
    max_tokens_limit: int = 260000
    
    # Generation Configuration
    delay_between_generations: int = 2
    
    def __post_init__(self):
        """Load missing values from environment variables"""
        load_dotenv()
        
        # Load mongodb_uri from env if not provided
        if self.mongodb_uri is None:
            self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        # Load bytez_keys_mongodb_uri from env if not provided (optional)
        if self.bytez_keys_mongodb_uri is None:
            self.bytez_keys_mongodb_uri = os.getenv('BYTEZ_KEYS_MONGODB_URI')
    
    @classmethod
    def from_env(cls) -> 'GeneratorConfig':
        """
        Load configuration from environment variables
        
        Returns:
            GeneratorConfig instance
        """
        load_dotenv()
        
        return cls(
            mongodb_uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            bytez_keys_mongodb_uri=os.getenv('BYTEZ_KEYS_MONGODB_URI'),  # Optional, falls back to mongodb_uri
            db_name=os.getenv('DB_NAME', 'auto_image_generator'),
            bytez_keys_db_name=os.getenv('BYTEZ_KEYS_DB_NAME', 'bytez_keys_manager'),
            generator_name=os.getenv('GENERATOR_NAME', 'images-auto-generator'),
            chat_uuid=os.getenv('CHAT_UUID'),
            chat_title=os.getenv('CHAT_TITLE'),
            prompt_file_name=os.getenv('PROMPT_FILE_NAME', 'prompt.txt'),
        )
    
    @property
    def prompt_file_path(self) -> str:
        """Get full path to prompt file"""
        return os.path.join(self.prompts_dir, self.prompt_file_name)


# Model Configuration
TEXT_MODEL = "openai/gpt-5.1"
IMAGE_MODEL = "google/imagen-4.0-ultra-generate-001"
