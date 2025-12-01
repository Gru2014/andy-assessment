from flask import Blueprint, request, jsonify
from app import db
from app.models import Collection, Topic, TopicRelationship, DocumentTopic, TopicInsight
from app.services.genai_service import GenAIService

bp = Blueprint('topics', __name__, url_prefix='')
genai_service = GenAIService()

@bp.route('/collections/<int:collection_id>/topics/graph', methods=['GET'])
def get_topic_graph(collection_id):
    """Get topic graph JSON for a collection"""
    collection = Collection.query.get_or_404(collection_id)
    topics = Topic.query.filter_by(collection_id=collection_id).all()
    relationships = TopicRelationship.query.join(
        Topic, TopicRelationship.source_topic_id == Topic.id
    ).filter(Topic.collection_id == collection_id).all()
    
    # Build nodes
    nodes = []
    for topic in topics:
        nodes.append({
            'id': f't{topic.id}',
            'label': topic.name,
            'size_score': topic.size_score,
            'document_count': topic.document_count,
            'avg_confidence': topic.avg_confidence,
            'color': topic.color or '#3498db'
        })
    
    # Build edges
    edges = []
    for rel in relationships:
        edges.append({
            'source': f't{rel.source_topic_id}',
            'target': f't{rel.target_topic_id}',
            'weight': rel.similarity_score,
            'type': rel.relationship_type
        })
    
    return jsonify({
        'nodes': nodes,
        'edges': edges
    })

@bp.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    """Get topic drill-down view"""
    topic = Topic.query.get_or_404(topic_id)
    
    # Get insights
    insight = TopicInsight.query.filter_by(topic_id=topic_id).first()
    
    # Get documents ranked by relevance
    assignments = DocumentTopic.query.filter_by(topic_id=topic_id).order_by(
        DocumentTopic.relevance_score.desc()
    ).all()
    
    documents = []
    for assignment in assignments:
        doc = assignment.document
        documents.append({
            'id': doc.id,
            'title': doc.title,
            'content_preview': doc.content[:200] if doc.content else '',
            'relevance_score': assignment.relevance_score,
            'is_primary': assignment.is_primary
        })
    
    # Get related topics
    related_topics = []
    relationships = TopicRelationship.query.filter(
        ((TopicRelationship.source_topic_id == topic_id) |
         (TopicRelationship.target_topic_id == topic_id))
    ).all()
    
    for rel in relationships:
        related_topic_id = rel.target_topic_id if rel.source_topic_id == topic_id else rel.source_topic_id
        related_topic = Topic.query.get(related_topic_id)
        if related_topic:
            related_topics.append({
                'id': related_topic.id,
                'name': related_topic.name,
                'similarity_score': rel.similarity_score,
                'relationship_type': rel.relationship_type
            })
    
    # Sort by similarity
    related_topics.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return jsonify({
        'id': topic.id,
        'name': topic.name,
        'document_count': topic.document_count,
        'size_score': topic.size_score,
        'insights': {
            'summary': insight.summary if insight else None,
            'themes': insight.themes if insight else [],
            'common_questions': insight.common_questions if insight else [],
            'related_concepts': insight.related_concepts if insight else []
        } if insight else None,
        'documents': documents,
        'related_topics': related_topics
    })

@bp.route('/topics/<int:topic_id>/qa', methods=['POST'])
def topic_qa(topic_id):
    """Topic-scoped Q&A with citations"""
    topic = Topic.query.get_or_404(topic_id)
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Get relevant documents
    assignments = DocumentTopic.query.filter_by(topic_id=topic_id).order_by(
        DocumentTopic.relevance_score.desc()
    ).limit(5).all()
    
    documents = [assignment.document for assignment in assignments]
    doc_texts = [f"Document {i+1}:\n{doc.content[:1000]}" for i, doc in enumerate(documents)]
    context = "\n\n".join(doc_texts)
    
    # Generate answer with citations
    prompt = f"""You are answering a question about the topic "{topic.name}".

Context from relevant documents:
{context[:4000]}

Question: {question}

Provide a comprehensive answer with inline citations. Format citations as [Doc1], [Doc2], etc. where Doc1 refers to the first document, Doc2 to the second, etc.

Answer:"""
    
    try:
        answer = genai_service.chat_completion([
            {'role': 'system', 'content': 'You are a helpful assistant that provides detailed answers with citations.'},
            {'role': 'user', 'content': prompt}
        ])
        
        # Extract citations from answer
        import re
        citation_pattern = r'\[Doc(\d+)\]'
        citations = re.findall(citation_pattern, answer)
        citation_doc_ids = [int(c) - 1 for c in citations if int(c) <= len(documents)]
        
        # Map citations to document IDs
        cited_documents = []
        for idx in set(citation_doc_ids):
            if 0 <= idx < len(documents):
                cited_documents.append({
                    'document_id': documents[idx].id,
                    'title': documents[idx].title,
                    'preview': documents[idx].content[:200]
                })
        
        return jsonify({
            'answer': answer,
            'citations': cited_documents,
            'topic_id': topic_id,
            'topic_name': topic.name
        })
    except Exception as e:
        return jsonify({'error': f'Failed to generate answer: {str(e)}'}), 500

