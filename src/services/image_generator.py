"""
Image Generator Service
Handles image generation using AI
"""

from bytez import Bytez
from src.config.settings import IMAGE_MODEL


class ImageGeneratorService:
    """Service for generating images using AI"""
    
    def __init__(self, api_key_manager):
        """
        Initialize image generator service
        
        Args:
            api_key_manager: API key manager instance
        """
        self.api_key_manager = api_key_manager
        self.model_name = IMAGE_MODEL
        self.generator_type = "image"
    
    def generate_image(self, prompt: str):
        """
        Generate image using AI
        
        Args:
            prompt: Image generation prompt
            
        Returns:
            Tuple of (image_link, error, api_key)
        """
        api_key_id = None
        api_key = None
        
        try:
            print(f"🎨 Generating image...")
            
            # Retry loop
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Acquire key
                    api_key_id, api_key = self.api_key_manager.acquire_key(self.model_name, self.generator_type)
                    
                    if not api_key:
                        print("❌ No available image API keys!")
                        return None, "No available image API keys", None
                    
                    sdk = Bytez(api_key)
                    image_model = sdk.model(self.model_name)
                    
                    # Generate
                    image_link, error, _ = image_model.run(prompt)
                    
                    if error:
                        print(f"❌ Error with key: {error}")
                        
                        # Log failed usage
                        used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                        self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, False, str(error))
                        
                        # Mark expired and release
                        self.api_key_manager.mark_key_expired_and_release(api_key, self.model_name)
                        continue
                    
                    print(f"✅ Image generated: {image_link}")
                    
                    # Log success and release
                    used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                    self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, True, None)
                    self.api_key_manager.release_key(api_key)
                    
                    return image_link, None, api_key
                    
                except Exception as e:
                    print(f"❌ Exception during generation: {e}")
                    
                    if api_key:
                        used_by = f"{self.api_key_manager.generator_name} - {self.generator_type} generation"
                        self.api_key_manager.log_usage(api_key_id, api_key, used_by, self.model_name, False, str(e))
                        self.api_key_manager.release_key(api_key)
                    continue
            
            print("❌ All retry attempts failed!")
            return None, "All retry attempts exhausted", None
            
        except Exception as e:
            print(f"❌ Unexpected error in generate_image: {e}")
            if api_key:
                self.api_key_manager.release_key(api_key)
            return None, str(e), None
