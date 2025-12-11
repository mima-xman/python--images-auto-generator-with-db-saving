from src.main import ImageGeneratorApp
from src.config.settings import GeneratorConfig

# Only override what you need - mongodb_uri loads from .env automatically
config = GeneratorConfig(
    generator_name="06_mobile_app_ui_mockup_stock_prompt",
    chat_title="Chat For 06_mobile_app_ui_mockup_stock_prompt.txt",
    prompt_file_name="06_mobile_app_ui_mockup_stock_prompt.txt"
)

# Run generator
app = ImageGeneratorApp(config)
results = app.run(delay=2)