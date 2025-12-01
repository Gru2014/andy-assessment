from typing import List, Dict, Any
from app import db
from app.models import Collection, Topic, TopicRelationship, DocumentTopic
from app.services.genai_service import GenAIService
import numpy as np

class RelationshipService:
    """Service for building topic relationships"""
    
    def __init__(self):
        self.genai = GenAIService()
    
    def build_relationships(self, collection_id: int) -> List[TopicRelationship]:
        """Build relationships between topics in a collection"""
        topics = Topic.query.filter_by(collection_id=collection_id).all()
        
        if len(topics) < 2:
            return []
        
        relationships = []
        
        # Get topic embeddings (average of document embeddings in each topic)
        topic_embeddings = {}
        for topic in topics:
            assignments = DocumentTopic.query.filter_by(topic_id=topic.id).all()
            if not assignments:
                continue
            
            doc_embeddings = []
            for assignment in assignments:
                from app.models import DocumentEmbedding
                embedding = DocumentEmbedding.query.filter_by(document_id=assignment.document_id).first()
                if embedding:
                    doc_embeddings.append(embedding.embedding)
            
            if doc_embeddings:
                topic_embeddings[topic.id] = np.mean(doc_embeddings, axis=0).tolist()
        
        # Calculate relationships
        topic_list = list(topics)
        for i, topic1 in enumerate(topic_list):
            if topic1.id not in topic_embeddings:
                continue
            
            for topic2 in topic_list[i+1:]:
                if topic2.id not in topic_embeddings:
                    continue
                
                # Calculate similarity
                similarity = self.genai.cosine_similarity(
                    topic_embeddings[topic1.id],
                    topic_embeddings[topic2.id]
                )
                
                # Count common documents
                doc_ids_1 = {dt.document_id for dt in DocumentTopic.query.filter_by(topic_id=topic1.id).all()}
                doc_ids_2 = {dt.document_id for dt in DocumentTopic.query.filter_by(topic_id=topic2.id).all()}
                common_count = len(doc_ids_1 & doc_ids_2)
                
                # Only create relationship if similarity is above threshold
                if similarity > 0.3:  # Threshold for relationships
                    # Check if relationship exists
                    existing = TopicRelationship.query.filter(
                        ((TopicRelationship.source_topic_id == topic1.id) & 
                         (TopicRelationship.target_topic_id == topic2.id)) |
                        ((TopicRelationship.source_topic_id == topic2.id) & 
                         (TopicRelationship.target_topic_id == topic1.id))
                    ).first()
                    
                    if existing:
                        existing.similarity_score = similarity
                        existing.common_document_count = common_count
                        existing.relationship_type = self._determine_relationship_type(similarity, common_count)
                    else:
                        relationship = TopicRelationship(
                            source_topic_id=topic1.id,
                            target_topic_id=topic2.id,
                            similarity_score=similarity,
                            relationship_type=self._determine_relationship_type(similarity, common_count),
                            common_document_count=common_count
                        )
                        db.session.add(relationship)
                        relationships.append(relationship)
        
        db.session.commit()
        return relationships
    
    def _determine_relationship_type(self, similarity: float, common_count: int) -> str:
        """Determine the type of relationship based on similarity and common documents"""
        if similarity > 0.7:
            return "STRONGLY_RELATED"
        elif similarity > 0.5:
            return "RELATED"
        elif common_count > 0:
            return "SHARED_DOCUMENTS"
        else:
            return "SIMILAR"

