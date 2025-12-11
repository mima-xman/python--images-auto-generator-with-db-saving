"""
Database Repositories
Handles all database operations using Repository pattern
"""

from datetime import datetime, timezone
from typing import Optional, List, Tuple
import uuid
import os


def get_current_time():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class ChatRepository:
    """Repository for chat operations"""
    
    def __init__(self, chats_collection, config):
        self.chats_collection = chats_collection
        self.config = config
    
    def get_or_create_chat(self, chat_uuid: Optional[str] = None, chat_title: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Get existing chat or create new one
        
        Args:
            chat_uuid: UUID of existing chat (optional)
            chat_title: Title for new chat (optional)
            
        Returns:
            Tuple of (chat_uuid, chat_title)
        """
        try:
            # If chat_uuid provided, try to find it
            if chat_uuid:
                existing_chat = self.chats_collection.find_one({"chat_uuid": chat_uuid})
                if existing_chat:
                    print(f"✅ Found existing chat: {existing_chat['title']} ({chat_uuid})")
                    self.chats_collection.update_one(
                        {"chat_uuid": chat_uuid},
                        {"$set": {"updatedAt": get_current_time()}}
                    )
                    return chat_uuid, existing_chat['title']
                else:
                    print(f"⚠️ Chat UUID {chat_uuid} not found in database")
            
            # Create new chat
            new_chat_uuid = str(uuid.uuid4())
            
            # Set default title if not provided
            if not chat_title:
                prompt_base = os.path.splitext(self.config.prompt_file_name)[0]
                chat_title = f'Chat - {prompt_base}'
            
            now = get_current_time()
            chat_document = {
                "chat_uuid": new_chat_uuid,
                "title": chat_title,
                "prompt_file": self.config.prompt_file_name,
                "createdAt": now,
                "updatedAt": now
            }
            
            self.chats_collection.insert_one(chat_document)
            print(f"✅ Created new chat: {chat_title} ({new_chat_uuid})")
            print(f"📄 Using prompt file: {self.config.prompt_file_name}")
            
            return new_chat_uuid, chat_title
            
        except Exception as e:
            print(f"❌ Error in get_or_create_chat: {e}")
            return None, None


class MessageRepository:
    """Repository for message operations"""
    
    def __init__(self, messages_collection, chats_collection, config):
        self.messages_collection = messages_collection
        self.chats_collection = chats_collection
        self.config = config
    
    def load_chat_history(self, chat_uuid: str, limit: Optional[int] = None) -> List[dict]:
        """
        Load chat messages from database
        
        Args:
            chat_uuid: Chat UUID
            limit: Maximum number of messages to load
            
        Returns:
            List of chat history messages
        """
        try:
            query = {"chat_uuid": chat_uuid}
            
            # Determine limit
            effective_limit = limit
            if effective_limit is None and self.config.enable_history_trimming:
                effective_limit = self.config.max_history_messages + 20
            
            if effective_limit:
                total_count = self.messages_collection.count_documents(query)
                skip_count = max(0, total_count - effective_limit)
                
                messages = self.messages_collection.find(query).sort("createdAt", 1).skip(skip_count)
                
                if total_count > effective_limit:
                    print(f"📊 Loading last {effective_limit} of {total_count} chat messages from DB")
                else:
                    print(f"📊 Loading all {total_count} chat messages from DB")
            else:
                messages = self.messages_collection.find(query).sort("createdAt", 1)
                total_count = self.messages_collection.count_documents(query)
                print(f"📊 Loading all {total_count} chat messages from DB")
            
            chat_history = []
            for msg in messages:
                chat_history.append({"role": "user", "content": msg["message"]})
                chat_history.append({"role": "assistant", "content": msg["response"]})
            
            print(f"✅ Loaded {len(chat_history)} messages into memory")
            return chat_history
            
        except Exception as e:
            print(f"❌ Error loading chat history: {e}")
            return []
    
    def save_message(self, chat_uuid: str, message: str, response: str, api_key: str):
        """
        Save chat message to database
        
        Args:
            chat_uuid: Chat UUID
            message: User message
            response: AI response
            api_key: API key used
            
        Returns:
            Inserted message ID
        """
        try:
            now = get_current_time()
            message_document = {
                "chat_uuid": chat_uuid,
                "message": message,
                "response": response,
                "api_key": api_key,
                "createdAt": now,
                "updatedAt": now
            }
            
            result = self.messages_collection.insert_one(message_document)
            
            # Update chat's updatedAt
            self.chats_collection.update_one(
                {"chat_uuid": chat_uuid},
                {"$set": {"updatedAt": now}}
            )
            
            return result.inserted_id
            
        except Exception as e:
            print(f"❌ Error saving chat message: {e}")
            return None
    
    def delete_message(self, message_id):
        """
        Delete chat message from database
        
        Args:
            message_id: Message ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if message_id:
                result = self.messages_collection.delete_one({"_id": message_id})
                if result.deleted_count > 0:
                    print(f"🗑️ Deleted orphaned chat message: {message_id}")
                    return True
            return False
        except Exception as e:
            print(f"❌ Error deleting chat message: {e}")
            return False


class ImageRepository:
    """Repository for image operations"""
    
    def __init__(self, images_collection):
        self.images_collection = images_collection
    
    def save_image(self, data: dict):
        """
        Save image to MongoDB
        
        Args:
            data: Image document data
            
        Returns:
            Inserted image ID
        """
        try:
            print("💾 Saving image...")
            result = self.images_collection.insert_one(data)
            print(f"✅ Saved: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ Error saving to DB: {e}")
            return None
