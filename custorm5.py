from src.main import ImageGeneratorApp
from src.config.settings import GeneratorConfig

# Only override what you need - mongodb_uri loads from .env automatically
config = GeneratorConfig(
    generator_name="05_cybersecurity_data_protection_stock_prompt",
    chat_title="Chat For 05_cybersecurity_data_protection_stock_prompt.txt",
    prompt_file_name="05_cybersecurity_data_protection_stock_prompt.txt"
)

# Run generator
app = ImageGeneratorApp(config)
results = app.run(delay=2)