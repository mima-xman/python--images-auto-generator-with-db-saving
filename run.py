"""
CLI Entry Point
Runs image generator using .env configuration
"""

from src.main import ImageGeneratorApp
from src.config.settings import GeneratorConfig


if __name__ == "__main__":
    try:
        # Load configuration from .env
        config = GeneratorConfig.from_env()
        
        # Print startup info
        print(f"\n{'='*60}")
        print(f"🚀 AI Image Generator Worker Started")
        print(f"🔑 Generator: {config.generator_name}")
        print(f"📁 Prompts Directory: {config.prompts_dir}/")
        print(f"📄 Prompt File: {config.prompt_file_name}")
        print(f"💬 Chat UUID: {config.chat_uuid or 'New Chat (will be created)'}")
        if config.chat_title:
            print(f"📝 Chat Title: {config.chat_title}")
        print(f"{'='*60}\n")
        
        # Run application
        app = ImageGeneratorApp(config)
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
