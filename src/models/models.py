# src/models/models.py
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    description = Column(Text)
    parent_id = Column(String(36), ForeignKey('prompts.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'version': self.version,
            'description': self.description,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PromptInstance(Base):
    __tablename__ = "prompt_instances"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String(36), ForeignKey('prompts.id'), nullable=False)
    formatted_text = Column(Text, nullable=False)
    context = Column(Text)  # JSON as string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt_id': self.prompt_id,
            'formatted_text': self.formatted_text,
            'context': self.context,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_instance_id = Column(String(36), ForeignKey('prompt_instances.id'), nullable=False)
    content = Column(Text, nullable=False)
    response_metadata = Column(Text)  # ✅ CHANGED: renamed from 'metadata' to 'response_metadata'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt_instance_id': self.prompt_instance_id,
            'content': self.content,
            'response_metadata': self.response_metadata,  # ✅ CHANGED: updated here too
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id = Column(String(36), ForeignKey('responses.id'), nullable=False)
    score = Column(DECIMAL(3,2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'response_id': self.response_id,
            'score': float(self.score),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OptimizationJob(Base):
    __tablename__ = "optimization_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String(36), ForeignKey('prompts.id'), nullable=False)
    status = Column(String(20), default='queued')
    strategy = Column(String(50), default='simple_ai')
    progress = Column(Integer, default=0)
    result = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt_id': self.prompt_id,
            'status': self.status,
            'strategy': self.strategy,
            'progress': self.progress,
            'result': self.result,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }