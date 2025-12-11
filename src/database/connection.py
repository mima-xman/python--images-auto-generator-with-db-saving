"""
MongoDB Connection Management
"""

from pymongo import MongoClient
from typing import Tuple
from src.config.settings import GeneratorConfig


class DatabaseConnection:
    """Manages MongoDB connection"""
    
    def __init__(self, config: GeneratorConfig):
        """
        Initialize database connection
        
        Args:
            config: Generator configuration
        """
        self.config = config
        self._client = None
        self._db = None
        self._keys_db = None
    
    def connect(self) -> None:
        """Establish MongoDB connection"""
        if self._client is None:
            self._client = MongoClient(self.config.mongodb_uri)
            self._db = self._client[self.config.db_name]
            self._keys_db = self._client[self.config.bytez_keys_db_name]
            print(f"✅ Connected to MongoDB: {self.config.db_name}")
    
    def get_collections(self) -> Tuple:
        """
        Get all required collections
        
        Returns:
            Tuple of (images_collection, chats_collection, messages_collection)
        """
        if self._db is None:
            self.connect()
        
        return (
            self._db[self.config.collection_images],
            self._db[self.config.collection_chats],
            self._db[self.config.collection_chat_messages]
        )
    
    def get_keys_db(self):
        """Get keys database"""
        if self._keys_db is None:
            self.connect()
        return self._keys_db
    
    def close(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            print("🔌 Closed MongoDB connection")
