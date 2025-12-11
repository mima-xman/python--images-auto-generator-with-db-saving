from src.main import ImageGeneratorApp
from src.config.settings import GeneratorConfig

# Only override what you need - mongodb_uri loads from .env automatically
config = GeneratorConfig(
    generator_name="01_remote_work_freelancing_stock_prompt",
    chat_title="Chat For 01_remote_work_freelancing_stock_prompt.txt",
    prompt_file_name="01_remote_work_freelancing_stock_prompt.txt"
)

# Run generator
app = ImageGeneratorApp(config)
results = app.run(delay=2)