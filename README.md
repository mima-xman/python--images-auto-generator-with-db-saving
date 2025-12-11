# AI Image Generator

Modular AI image generation system with database-based API key management.

## Features

- 🤖 AI-powered image generation using Bytez API
- 🔑 Database-managed API keys with automatic rotation
- 💾 MongoDB storage for images, chats, and messages
- � Separate MongoDB instances support (app data vs API keys)
- �📊 Usage logging and expiration tracking
- ⚙️ Smart configuration with .env fallback
- 🏗️ Modular architecture for easy maintenance

## Project Structure

```
src/
├── config/
│   └── settings.py          # Configuration management
├── database/
│   ├── connection.py        # MongoDB connection
│   └── repositories.py      # Database operations
├── services/
│   ├── api_key_manager.py   # API key management
│   ├── text_generator.py    # Metadata generation
│   ├── image_generator.py   # Image generation
│   └── chat_manager.py      # Chat/prompt management
├── utils/
│   ├── token_estimator.py   # Token utilities
│   └── text_extractor.py    # Metadata extraction
└── main.py                  # Main application
run.py                       # CLI entry point
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

## Usage

### Method 1: Using .env (Simple)

```bash
# Edit .env file with your settings
python run.py
```

### Method 2: Programmatic (Advanced)

**Option A: Minimal Override (Recommended)**

Only specify what you want to customize - other values auto-load from `.env`:

```python
from src.main import ImageGeneratorApp
from src.config.settings import GeneratorConfig

# Only override what you need - mongodb_uri loads from .env automatically
config = GeneratorConfig(
    generator_name="my-custom-generator",
    chat_title="My Custom Chat",
    prompt_file_name="custom-prompt.txt"
)

# Run generator
app = ImageGeneratorApp(config)
results = app.run(delay=2)
```

**Option B: Full Override**

Specify all configuration programmatically:

```python
# Create custom configuration
config = GeneratorConfig(
    mongodb_uri="mongodb://localhost:27017/",
    bytez_keys_mongodb_uri="mongodb://keys-db:27017/",  # Optional, separate DB for API keys
    generator_name="my-custom-generator",
    chat_uuid="abc-123",
    chat_title="My Custom Chat",
    prompt_file_name="custom-prompt.txt"
)

# Run generator
app = ImageGeneratorApp(config)
results = app.run(delay=2)
```

## Configuration

### Environment Variables

- `MONGODB_URI` - MongoDB connection string for application data (images, chats, messages)
- `BYTEZ_KEYS_MONGODB_URI` - MongoDB connection string for API keys (optional, defaults to MONGODB_URI)
- `DB_NAME` - Database name (default: auto_image_generator)
- `BYTEZ_KEYS_DB_NAME` - Keys database name (default: bytez_keys_manager)
- `GENERATOR_NAME` - Generator identifier (default: images-auto-generator)
- `CHAT_UUID` - Continue existing chat (optional)
- `CHAT_TITLE` - Chat title (optional)
- `PROMPT_FILE_NAME` - Prompt filename (default: prompt.txt)

> **Note**: You can use separate MongoDB instances for application data and API key management by setting `BYTEZ_KEYS_MONGODB_URI`. If not set, both will use `MONGODB_URI` (backward compatible).

### Programmatic Configuration

All settings can be passed directly to `GeneratorConfig`:

```python
config = GeneratorConfig(
    mongodb_uri="mongodb://app-cluster:27017/",
    bytez_keys_mongodb_uri="mongodb://keys-cluster:27017/",  # Optional, separate DB for API keys
    db_name="...",
    bytez_keys_db_name="...",
    generator_name="...",
    chat_uuid="...",
    chat_title="...",
    prompt_file_name="...",
    enable_history_trimming=True,
    max_history_messages=400,
    max_tokens_limit=260000
)
```

## Architecture

### Modular Design

- **Config**: Centralized configuration with dual support
- **Database**: Repository pattern for clean data access
- **Services**: Business logic separated by concern
- **Utils**: Reusable utility functions

### Benefits

✅ **Maintainable** - Clear separation of concerns  
✅ **Testable** - Each module can be tested independently  
✅ **Scalable** - Easy to add new features  
✅ **Flexible** - Supports both env and programmatic config  

## Development

### Running Tests

```bash
python test_api_key_manager.py
```

### Adding New Features

1. Create new service in `src/services/`
2. Add to `src/main.py` initialization
3. Use in generation loop

## License

MIT
