# test_database.py - Enhanced test with better error handling
import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

def check_environment():
    """Check if all required packages are installed"""
    print("🔍 Checking environment setup...")
    
    # Check Python version
    import sys
    print(f"🐍 Python version: {sys.version.split()[0]}")
    
    # Check conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'Unknown')
    print(f"🐍 Conda environment: {conda_env}")
    
    # Check required packages
    try:
        import sqlalchemy
        print("✅ sqlalchemy is installed")
    except ImportError:
        print("❌ sqlalchemy is not installed")
        return False
    
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
    except ImportError:
        print("❌ psycopg2 is not installed")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv is installed")
    except ImportError:
        print("❌ python-dotenv is not installed")
        return False
    
    # Try importing our modules
    try:
        from database.database import Database
        print("✅ Successfully imported all modules")
    except ImportError as e:
        print(f"❌ Failed to import modules: {e}")
        return False
    
    return True

def test_database():
    print("=" * 60)
    print("🚀 PromptCraft Database Test")
    print("=" * 60)
    
    if not check_environment():
        print("❌ Environment setup failed. Please check your installation.")
        return
    
    # Load environment variables
    load_dotenv()
    
    # Check DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        print("💡 Create a .env file with DATABASE_URL=postgresql://user:pass@localhost/promptcraft")
        return
    
    # Mask password in output
    masked_url = db_url.split('@')[0].split(':')[:-1]
    print(f"✅ DATABASE_URL found: {':'.join(masked_url)}:***@...")
    
    try:
        from database.database import Database
        
        print("\n🧪 Testing database setup...")
        
        # Initialize database
        db = Database()
        print("✅ Database instance created")
        
        db.initialize()
        print("✅ Database tables created/verified")
        
        # Test creating a prompt
        print("\n📝 Testing prompt creation...")
        prompt = db.create_prompt(
            text="Analyze the sentiment of: {input_text}",
            description="Simple sentiment analysis prompt"
        )
        print(f"✅ Created prompt: {prompt.id}")
        print(f"   Text: {prompt.text[:50]}...")
        
        # Test retrieving the prompt
        print("\n🔍 Testing prompt retrieval...")
        retrieved = db.get_prompt(prompt.id)
        if retrieved:
            print(f"✅ Retrieved prompt: {retrieved.id}")
            print(f"   Text matches: {retrieved.text == prompt.text}")
        else:
            print("❌ Failed to retrieve prompt")
            return
        
        # Test creating an instance
        print("\n📋 Testing instance creation...")
        instance = db.create_instance(
            prompt_id=prompt.id,
            formatted_text="Analyze the sentiment of: This movie is great!",
            context='{"source": "test"}'
        )
        print(f"✅ Created instance: {instance.id}")
        print(f"   Linked to prompt: {instance.prompt_id}")
        
        # Test creating a response
        print("\n💬 Testing response creation...")
        response = db.create_response(
            prompt_instance_id=instance.id,
            content="Positive sentiment detected",
            metadata='{"confidence": 0.95}'
        )
        print(f"✅ Created response: {response.id}")
        print(f"   Content: {response.content}")
        
        # Test creating feedback
        print("\n⭐ Testing feedback creation...")
        feedback = db.create_feedback(
            response_id=response.id,
            score=0.9
        )
        print(f"✅ Created feedback: {feedback.id}")
        print(f"   Score: {feedback.score}")
        
        # Test feedback retrieval
        print("\n📊 Testing feedback retrieval...")
        all_feedback = db.get_feedback_for_prompt(prompt.id)
        print(f"✅ Retrieved {len(all_feedback)} feedback items")
        
        if all_feedback:
            first_feedback = all_feedback[0]
            print(f"   Sample feedback score: {first_feedback['feedback']['score']}")
        
        print("\n🎉 All tests passed! Database setup is working correctly.")
        print("✅ Ready for Person B to start building FastAPI endpoints!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("💡 Check your database connection and credentials")
        
        # Additional debugging info
        if "could not connect" in str(e).lower():
            print("💡 PostgreSQL might not be running. Try:")
            print("   - Start PostgreSQL service")
            print("   - Check your DATABASE_URL credentials")
        elif "does not exist" in str(e).lower():
            print("💡 Database might not exist. Try:")
            print("   - createdb promptcraft")

if __name__ == "__main__":
    test_database()