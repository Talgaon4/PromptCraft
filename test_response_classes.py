#!/usr/bin/env python3
"""
Test script to debug response classes
"""

from src.api.responses import PromptResult
from datetime import datetime

def test_prompt_result():
    """Test PromptResult.success with various data types"""
    
    # Test 1: Simple dict
    print("🧪 Test 1: Simple dict")
    try:
        simple_dict = {
            "id": "test-id-123",
            "text": "Test prompt",
            "description": "Test description"
        }
        result = PromptResult.success(simple_dict, "Test message")
        print(f"✅ Simple dict success: {result}")
    except Exception as e:
        print(f"❌ Simple dict failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Dict with datetime (like from your database)
    print("🧪 Test 2: Dict with datetime")
    try:
        datetime_dict = {
            "id": "test-id-456",
            "text": "Test prompt",
            "description": "Test description",
            "created_at": "2025-06-15T14:34:19.842978",  # String format
            "updated_at": "2025-06-15T14:34:19.842982"
        }
        result = PromptResult.success(datetime_dict, "Test message")
        print(f"✅ Datetime dict success: {result}")
    except Exception as e:
        print(f"❌ Datetime dict failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Dict with actual datetime objects
    print("🧪 Test 3: Dict with actual datetime objects")
    try:
        actual_datetime_dict = {
            "id": "test-id-789",
            "text": "Test prompt",
            "description": "Test description",
            "created_at": datetime.now(),  # Actual datetime object
            "updated_at": datetime.now()
        }
        result = PromptResult.success(actual_datetime_dict, "Test message")
        print(f"✅ Actual datetime dict success: {result}")
    except Exception as e:
        print(f"❌ Actual datetime dict failed: {e}")
        import traceback
        traceback.print_exc()

def test_direct_serialization():
    """Test direct JSON serialization"""
    from datetime import datetime
    import json
    
    print("🧪 Test 4: Direct JSON serialization")
    
    test_dict = {
        "id": "test-id-serialization",
        "text": "Test prompt",
        "description": "Test description",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    try:
        json_str = json.dumps(test_dict, default=str)
        print(f"✅ JSON serialization success: {json_str}")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing response classes...\n")
    
    test_prompt_result()
    
    print("\n" + "="*50 + "\n")
    
    test_direct_serialization()
    
    print("\n🎉 Response class tests completed!")