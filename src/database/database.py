# src/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from src.models.models import Base, Prompt, PromptInstance, Response, Feedback, OptimizationJob

class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,   # ← שורה חדשה
            bind=self.engine,
        )
    
    def create_tables(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

class Database:
    """Simple database operations class"""
    
    def __init__(self, database_url: str = None):
        self.db_manager = DatabaseManager(database_url)
    
    def initialize(self):
        """Initialize database - create tables if they don't exist"""
        self.db_manager.create_tables()
    
    # Prompt operations
    def create_prompt(self, text: str, description: str = "") -> Prompt:
        with self.db_manager.get_session() as session:
            prompt = Prompt(text=text, description=description)
            session.add(prompt)
            session.commit()  # Commit to get the ID
            session.refresh(prompt)  # Refresh to get all data
            
            # Create a detached copy to return
            prompt_dict = prompt.to_dict()
            session.expunge(prompt)  # Detach from session
            return prompt
    
    def get_prompt(self, prompt_id: str) -> Prompt:
        with self.db_manager.get_session() as session:
            prompt = session.query(Prompt).filter(Prompt.id == prompt_id).first()
            if prompt:
                # Access all attributes while session is active
                _ = prompt.to_dict()  # This forces all attributes to load
                session.expunge(prompt)  # Detach from session
            return prompt
    
    def list_prompts(self, limit: int = 50, offset: int = 0) -> list[Prompt]:
        with self.db_manager.get_session() as session:
            prompts = session.query(Prompt).offset(offset).limit(limit).all()
            # Detach all objects from session
            for prompt in prompts:
                _ = prompt.to_dict()  # Force attribute loading
                session.expunge(prompt)
            return prompts
    
    # Instance operations
    def create_instance(self, prompt_id: str, formatted_text: str, context: str = None) -> PromptInstance:
        with self.db_manager.get_session() as session:
            instance = PromptInstance(
                prompt_id=prompt_id,
                formatted_text=formatted_text,
                context=context
            )
            session.add(instance)
            session.commit()
            session.refresh(instance)
            
            # Detach from session
            _ = instance.to_dict()
            session.expunge(instance)
            return instance
    
    def get_instance(self, instance_id: str) -> PromptInstance:
        with self.db_manager.get_session() as session:
            instance = session.query(PromptInstance).filter(PromptInstance.id == instance_id).first()
            if instance:
                _ = instance.to_dict()
                session.expunge(instance)
            return instance
    
    # Response operations
    def create_response(self, prompt_instance_id: str, content: str, metadata: str = None) -> Response:
        with self.db_manager.get_session() as session:
            response = Response(
                prompt_instance_id=prompt_instance_id,
                content=content,
                metadata=metadata
            )
            session.add(response)
            session.commit()
            session.refresh(response)
            
            # Detach from session
            _ = response.to_dict()
            session.expunge(response)
            return response
    
    def get_response(self, response_id: str) -> Response:
        with self.db_manager.get_session() as session:
            response = session.query(Response).filter(Response.id == response_id).first()
            if response:
                _ = response.to_dict()
                session.expunge(response)
            return response
    
    # Feedback operations
    def create_feedback(self, response_id: str, score: float) -> Feedback:
        with self.db_manager.get_session() as session:
            feedback = Feedback(response_id=response_id, score=score)
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            
            # Detach from session
            _ = feedback.to_dict()
            session.expunge(feedback)
            return feedback
    
    def get_feedback_for_prompt(self, prompt_id: str) -> list[dict]:
        """Get all feedback for a prompt with joined data"""
        with self.db_manager.get_session() as session:
            results = session.query(
                Feedback, Response, PromptInstance
            ).join(
                Response, Feedback.response_id == Response.id
            ).join(
                PromptInstance, Response.prompt_instance_id == PromptInstance.id
            ).filter(
                PromptInstance.prompt_id == prompt_id
            ).all()
            
            feedback_list = []
            for feedback, response, instance in results:
                # Convert to dict immediately while session is active
                feedback_list.append({
                    'feedback': feedback.to_dict(),
                    'response': response.to_dict(),
                    'instance': instance.to_dict()
                })
            
            return feedback_list