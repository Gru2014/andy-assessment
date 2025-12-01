from app import db
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, Enum, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class JobStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship('Document', back_populates='collection', cascade='all, delete-orphan')
    topics = relationship('Topic', back_populates='collection', cascade='all, delete-orphan')
    discovery_jobs = relationship('DiscoveryJob', back_populates='collection', cascade='all, delete-orphan')

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    file_path = Column(String(1000))
    file_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    collection = relationship('Collection', back_populates='documents')
    topic_assignments = relationship('DocumentTopic', back_populates='document', cascade='all, delete-orphan')
    embeddings = relationship('DocumentEmbedding', back_populates='document', cascade='all, delete-orphan', uselist=False)

class DocumentEmbedding(db.Model):
    __tablename__ = 'document_embeddings'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, unique=True)
    embedding = Column(ARRAY(Float))  # Vector embedding
    model = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship('Document', back_populates='embeddings')

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    name = Column(String(255), nullable=False)
    cluster_id = Column(Integer)  # For incremental updates
    document_count = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    color = Column(String(7))  # Hex color
    size_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    collection = relationship('Collection', back_populates='topics')
    document_assignments = relationship('DocumentTopic', back_populates='topic', cascade='all, delete-orphan')
    insights = relationship('TopicInsight', back_populates='topic', cascade='all, delete-orphan', uselist=False)
    source_relationships = relationship('TopicRelationship', foreign_keys='TopicRelationship.source_topic_id', back_populates='source_topic', cascade='all, delete-orphan')
    target_relationships = relationship('TopicRelationship', foreign_keys='TopicRelationship.target_topic_id', back_populates='target_topic', cascade='all, delete-orphan')

class DocumentTopic(db.Model):
    __tablename__ = 'document_topics'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    relevance_score = Column(Float, default=0.0)
    is_primary = Column(Boolean, default=False)
    
    document = relationship('Document', back_populates='topic_assignments')
    topic = relationship('Topic', back_populates='document_assignments')
    
    __table_args__ = (db.UniqueConstraint('document_id', 'topic_id', name='_document_topic_uc'),)

class TopicRelationship(db.Model):
    __tablename__ = 'topic_relationships'
    
    id = Column(Integer, primary_key=True)
    source_topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    target_topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    similarity_score = Column(Float, default=0.0)
    relationship_type = Column(String(50))  # RELATED, SIMILAR, etc.
    common_document_count = Column(Integer, default=0)
    
    source_topic = relationship('Topic', foreign_keys=[source_topic_id], back_populates='source_relationships')
    target_topic = relationship('Topic', foreign_keys=[target_topic_id], back_populates='target_relationships')
    
    __table_args__ = (db.UniqueConstraint('source_topic_id', 'target_topic_id', name='_topic_relationship_uc'),)

class TopicInsight(db.Model):
    __tablename__ = 'topic_insights'
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False, unique=True)
    summary = Column(Text)
    themes = Column(ARRAY(String))  # List of themes
    common_questions = Column(ARRAY(String))  # List of questions
    related_concepts = Column(ARRAY(String))  # List of concepts
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    topic = relationship('Topic', back_populates='insights')

class DiscoveryJob(db.Model):
    __tablename__ = 'discovery_jobs'
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    current_step = Column(String(255))
    error_message = Column(Text)
    rq_job_id = Column(String(255))  # RQ job ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    collection = relationship('Collection', back_populates='discovery_jobs')

