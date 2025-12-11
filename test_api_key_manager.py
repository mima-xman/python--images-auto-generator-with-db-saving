"""
Test script for ApiKeyManager
Tests key acquisition, release, logging, and expiration
"""

from api_key_manager import ApiKeyManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_sanitize_model_name():
    """Test model name sanitization"""
    print("\n" + "="*60)
    print("TEST 1: Model Name Sanitization")
    print("="*60)
    
    test_cases = [
        ("google/imagen-4.0-ultra-generate-001", "google__imagen-4__0-ultra-generate-001"),
        ("openai/gpt-5.1", "openai__gpt-5__1"),
        ("test\\model.name", "test__model__name")
    ]
    
    for original, expected in test_cases:
        result = ApiKeyManager.sanitize_model_name(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} {original} -> {result}")
        if result != expected:
            print(f"   Expected: {expected}")

def test_key_acquisition():
    """Test acquiring a key from database"""
    print("\n" + "="*60)
    print("TEST 2: Key Acquisition")
    print("="*60)
    
    try:
        manager = ApiKeyManager("test-generator")
        
        # Try to acquire a text generation key
        api_key_id, api_key = manager.acquire_key("openai/gpt-5.1", "text")
        
        if api_key:
            print(f"✅ Successfully acquired key: {api_key[:8]}...")
            print(f"   Key ID: {api_key_id}")
            
            # Release the key
            manager.release_key(api_key)
            print(f"✅ Successfully released key")
        else:
            print("❌ No keys available (this is expected if database is empty)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_usage_logging():
    """Test usage logging"""
    print("\n" + "="*60)
    print("TEST 3: Usage Logging")
    print("="*60)
    
    try:
        manager = ApiKeyManager("test-generator")
        
        # Acquire a key
        api_key_id, api_key = manager.acquire_key("openai/gpt-5.1", "text")
        
        if api_key:
            # Log successful usage
            used_by = f"{manager.generator_name} - text generation"
            log_id = manager.log_usage(
                api_key_id, 
                api_key, 
                used_by, 
                "openai/gpt-5.1", 
                True, 
                None
            )
            
            if log_id:
                print(f"✅ Successfully logged usage: {log_id}")
            else:
                print("❌ Failed to log usage")
            
            # Release the key
            manager.release_key(api_key)
        else:
            print("⚠️ Skipping test - no keys available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_expiration_handling():
    """Test key expiration and release"""
    print("\n" + "="*60)
    print("TEST 4: Expiration Handling")
    print("="*60)
    
    try:
        manager = ApiKeyManager("test-generator")
        
        # Acquire a key
        api_key_id, api_key = manager.acquire_key("google/imagen-4.0-ultra-generate-001", "image")
        
        if api_key:
            # Mark as expired and release (atomic operation)
            success = manager.mark_key_expired_and_release(api_key, "google/imagen-4.0-ultra-generate-001")
            
            if success:
                print(f"✅ Successfully marked key as expired and released")
            else:
                print("❌ Failed to mark key as expired")
        else:
            print("⚠️ Skipping test - no keys available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_cleanup():
    """Test releasing all keys"""
    print("\n" + "="*60)
    print("TEST 5: Cleanup (Release All Keys)")
    print("="*60)
    
    try:
        manager = ApiKeyManager("test-generator")
        
        # Acquire multiple keys
        keys_acquired = []
        for i in range(2):
            api_key_id, api_key = manager.acquire_key("openai/gpt-5.1", "text")
            if api_key:
                keys_acquired.append(api_key)
        
        print(f"📊 Acquired {len(keys_acquired)} keys")
        
        # Release all
        count = manager.release_all_keys()
        print(f"✅ Released {count} keys")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# API KEY MANAGER TEST SUITE")
    print("#"*60)
    
    test_sanitize_model_name()
    test_key_acquisition()
    test_usage_logging()
    test_expiration_handling()
    test_cleanup()
    
    print("\n" + "#"*60)
    print("# TESTS COMPLETE")
    print("#"*60 + "\n")
