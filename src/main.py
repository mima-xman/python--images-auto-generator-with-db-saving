"""
Main Application
Image Generator with modular architecture
"""

import time
from datetime import datetime, timezone
from src.config.settings import GeneratorConfig
from src.database.connection import DatabaseConnection
from src.database.repositories import ChatRepository, MessageRepository, ImageRepository
from src.services.api_key_manager import ApiKeyManager
from src.services.chat_manager import ChatManager
from src.services.text_generator import TextGeneratorService
from src.services.image_generator import ImageGeneratorService


def get_current_time():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class ImageGeneratorApp:
    """Main image generator application"""
    
    def __init__(self, config: GeneratorConfig):
        """
        Initialize application
        
        Args:
            config: Generator configuration
        """
        self.config = config
        
        # Initialize database
        self.db_connection = DatabaseConnection(config)
        self.db_connection.connect()
        images_coll, chats_coll, messages_coll = self.db_connection.get_collections()
        
        # Initialize repositories
        self.chat_repo = ChatRepository(chats_coll, config)
        self.message_repo = MessageRepository(messages_coll, chats_coll, config)
        self.image_repo = ImageRepository(images_coll)
        
        # Initialize services
        self.api_key_manager = ApiKeyManager(
            config.generator_name,
            mongodb_uri=config.bytez_keys_mongodb_uri or config.mongodb_uri
        )
        self.chat_manager = ChatManager(config)
        self.text_generator = TextGeneratorService(
            self.api_key_manager,
            self.message_repo,
            self.chat_manager,
            config
        )
        self.image_generator = ImageGeneratorService(self.api_key_manager)
        
        # State
        self.chat_uuid = None
        self.chat_title = None
        self.chat_history = []
    
    def run(self, delay: int = None):
        """
        Run infinite generation loop
        
        Args:
            delay: Delay between generations (uses config if not provided)
            
        Returns:
            List of generated results
        """
        delay = delay or self.config.delay_between_generations
        results = []
        
        try:
            # Get or create chat
            self.chat_uuid, self.chat_title = self.chat_repo.get_or_create_chat(
                self.config.chat_uuid,
                self.config.chat_title
            )
            
            if not self.chat_uuid:
                print("❌ Cannot proceed without chat!")
                return []
            
            # Load chat history
            self.chat_history = self.message_repo.load_chat_history(self.chat_uuid)
            
            # Print header
            self._print_header()
            
            image_count = 0
            
            while True:
                try:
                    image_count += 1
                    print(f"\n{'='*60}")
                    print(f"--- Image #{image_count} ---")
                    print(f"{'='*60}\n")
                    
                    result = self._generate_single_image()
                    
                    if result:
                        results.append(result)
                        print(f"✅ #{image_count}. {result['title']}")
                    else:
                        print(f"❌ #{image_count}. Generation failed - continuing to next image")
                    
                    time.sleep(delay)
                    
                except KeyboardInterrupt:
                    print("\n\n⏹️  Generation stopped by user (Ctrl+C)")
                    break
                except Exception as e:
                    print(f"❌ Error in iteration #{image_count}: {e}")
                    time.sleep(delay)
                    continue
            
            # Print summary
            self._print_summary(image_count, results)
            
            return results
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Generation stopped by user (Ctrl+C)")
            return results
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return results
        finally:
            self._cleanup()
    
    def _generate_single_image(self):
        """
        Generate a single image
        
        Returns:
            Image document or None if failed
        """
        # Generate metadata
        metadata, error, self.chat_history, message_id, chat_api_key = self.text_generator.generate_metadata(
            self.chat_uuid,
            self.chat_history
        )
        
        if not metadata or not message_id:
            return None
        
        print(f"\n📊 Metadata:")
        print(f"  Title: {metadata['title']}")
        print(f"  Category: {metadata['category']}")
        print(f"  Keywords: {metadata.get('keywords', [])}\n")
        
        # Generate image
        image_link, error, image_api_key = self.image_generator.generate_image(metadata["prompt"])
        
        if not image_link:
            print(f"❌ Image generation failed")
            self.message_repo.delete_message(message_id)
            if len(self.chat_history) >= 2:
                self.chat_history.pop()
                self.chat_history.pop()
            return None
        
        # Save to database
        now = get_current_time()
        document = {
            "message_id": message_id,
            "prompt": metadata["prompt"],
            "title": metadata["title"],
            "category": metadata["category"],
            "description": metadata["description"],
            "keywords": metadata["keywords"],
            "image_link": image_link,
            "api_key": image_api_key,
            "prompt_file": self.config.prompt_file_name,
            "createdAt": now,
            "updatedAt": now
        }
        
        if self.image_repo.save_image(document):
            return document
        else:
            print(f"⚠️ Failed to save to database")
            self.message_repo.delete_message(message_id)
            if len(self.chat_history) >= 2:
                self.chat_history.pop()
                self.chat_history.pop()
            return None
    
    def _print_header(self):
        """Print application header"""
        print(f"\n{'#'*60}")
        print(f"♾️  INFINITE GENERATION MODE")
        print(f"🔑 Generator: {self.config.generator_name}")
        print(f"💬 Chat: {self.chat_title} ({self.chat_uuid})")
        print(f"📄 Prompt File: {self.config.prompt_file_path}")
        print(f"📝 History: {len(self.chat_history)} messages in memory")
        print(f"⚙️  History Trimming: {'ENABLED' if self.config.enable_history_trimming else 'DISABLED'}")
        if self.config.enable_history_trimming:
            print(f"📊 Max Messages: {self.config.max_history_messages} | Max Tokens: {self.config.max_tokens_limit:,}")
        print(f"⚠️  Press Ctrl+C to stop")
        print(f"{'#'*60}\n")
    
    def _print_summary(self, image_count: int, results: list):
        """Print generation summary"""
        print(f"\n{'#'*60}")
        print(f"📊 Final Summary:")
        print(f"  Generator: {self.config.generator_name}")
        print(f"  Chat: {self.chat_title} ({self.chat_uuid})")
        print(f"  Prompt File: {self.config.prompt_file_name}")
        print(f"  Total Attempts: {image_count}")
        print(f"  Successful: {len(results)}")
        print(f"  Failed: {image_count - len(results)}")
        print(f"  Final History Size: {len(self.chat_history)} messages")
        print(f"{'#'*60}\n")
        
        if results:
            print("\n🎨 Last 10 Generated Images:")
            for i, result in enumerate(results[-10:], 1):
                print(f"  {i}. [{result['category']}] {result['title']}")
        
        print(f"\n💡 To continue this chat, use: chat_uuid='{self.chat_uuid}'")
    
    def _cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")
        if self.api_key_manager:
            self.api_key_manager.release_all_keys()
        if self.db_connection:
            self.db_connection.close()
