from typing import List, Dict, Any, Tuple
from app import db
from app.models import Collection, Document, Topic, DocumentTopic, DocumentEmbedding
from app.services.genai_service import GenAIService
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

class TopicDiscoveryService:
    """Service for discovering topics from documents"""
    
    def __init__(self):
        self.genai = GenAIService()
    
    def discover_topics(self, collection_id: int, incremental: bool = False) -> Dict[str, Any]:
        """
        Discover topics for a collection.
        If incremental=True, only process new documents and update existing topics.
        """
        collection = Collection.query.get_or_404(collection_id)
        documents = Document.query.filter_by(collection_id=collection_id).all()
        
        if not documents:
            return {'topics': [], 'relationships': []}
        
        # Get or create embeddings
        embeddings_list = []
        doc_ids = []
        for doc in documents:
            embedding = DocumentEmbedding.query.filter_by(document_id=doc.id).first()
            if not embedding:
                # Generate embedding
                embedding_vec = self.genai.get_embedding(doc.content[:8000])  # Limit content length
                embedding = DocumentEmbedding(
                    document_id=doc.id,
                    embedding=embedding_vec,
                    model=self.genai.embedding_model
                )
                db.session.add(embedding)
                db.session.commit()
            embeddings_list.append(embedding.embedding)
            doc_ids.append(doc.id)
        
        embeddings_matrix = np.array(embeddings_list)
        
        # Determine number of clusters (topics)
        n_docs = len(documents)
        n_clusters = max(2, min(10, n_docs // 3))  # Adaptive clustering
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings_matrix)
        
        # Generate topics from clusters
        topics = []
        for cluster_id in range(n_clusters):
            cluster_docs = [documents[i] for i in range(len(documents)) if cluster_labels[i] == cluster_id]
            if not cluster_docs:
                continue
            
            # Generate topic name and details using LLM
            topic_name = self._generate_topic_name(cluster_docs)
            
            # Check if topic already exists (for incremental updates)
            existing_topic = None
            if incremental:
                existing_topic = Topic.query.filter_by(
                    collection_id=collection_id,
                    cluster_id=cluster_id
                ).first()
            
            if existing_topic:
                topic = existing_topic
                topic.name = topic_name
            else:
                topic = Topic(
                    collection_id=collection_id,
                    name=topic_name,
                    cluster_id=cluster_id,
                    document_count=len(cluster_docs),
                    size_score=len(cluster_docs) / n_docs
                )
                db.session.add(topic)
                db.session.flush()
            
            # Assign documents to topic
            for doc_idx, doc in enumerate(cluster_docs):
                if doc.id in doc_ids:
                    doc_idx_in_list = doc_ids.index(doc.id)
                    # Calculate relevance score (distance from cluster center)
                    cluster_center = kmeans.cluster_centers_[cluster_id]
                    doc_embedding = embeddings_matrix[doc_idx_in_list]
                    similarity = self.genai.cosine_similarity(cluster_center.tolist(), doc_embedding.tolist())
                    
                    # Check if assignment exists
                    assignment = DocumentTopic.query.filter_by(
                        document_id=doc.id,
                        topic_id=topic.id
                    ).first()
                    
                    if assignment:
                        assignment.relevance_score = similarity
                        assignment.is_primary = (cluster_labels[doc_idx_in_list] == cluster_id)
                    else:
                        assignment = DocumentTopic(
                            document_id=doc.id,
                            topic_id=topic.id,
                            relevance_score=similarity,
                            is_primary=(cluster_labels[doc_idx_in_list] == cluster_id)
                        )
                        db.session.add(assignment)
            
            topics.append(topic)
        
        db.session.commit()
        
        return {'topics': topics, 'cluster_labels': cluster_labels.tolist()}
    
    def _generate_topic_name(self, documents: List[Document]) -> str:
        """Generate a topic name from a cluster of documents"""
        # Sample documents for topic naming
        sample_texts = [doc.content[:500] for doc in documents[:5]]
        combined_text = "\n\n".join(sample_texts)
        
        prompt = f"""Analyze the following documents and generate a concise topic name (2-4 words) that captures the main theme.

Documents:
{combined_text[:2000]}

Generate only the topic name, nothing else:"""
        
        try:
            topic_name = self.genai.chat_completion([
                {'role': 'system', 'content': 'You are a helpful assistant that generates concise topic names.'},
                {'role': 'user', 'content': prompt}
            ])
            return topic_name.strip().strip('"').strip("'")
        except Exception as e:
            # Fallback to generic name
            return f"Topic {len(documents)}"
    
    def calculate_relevance_scores(self, collection_id: int):
        """Recalculate relevance scores for all document-topic assignments"""
        topics = Topic.query.filter_by(collection_id=collection_id).all()
        
        for topic in topics:
            assignments = DocumentTopic.query.filter_by(topic_id=topic.id).all()
            topic_embeddings = []
            doc_ids = []
            
            for assignment in assignments:
                doc = assignment.document
                embedding = DocumentEmbedding.query.filter_by(document_id=doc.id).first()
                if embedding:
                    topic_embeddings.append(embedding.embedding)
                    doc_ids.append(doc.id)
            
            if not topic_embeddings:
                continue
            
            # Calculate centroid
            centroid = np.mean(topic_embeddings, axis=0)
            
            # Update relevance scores
            for assignment in assignments:
                if assignment.document.id in doc_ids:
                    idx = doc_ids.index(assignment.document.id)
                    similarity = self.genai.cosine_similarity(
                        centroid.tolist(),
                        topic_embeddings[idx]
                    )
                    assignment.relevance_score = similarity

