from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Collection, Topic, TopicRelationship, DocumentTopic, TopicInsight, Document, DiscoveryJob
from app.services.genai_service import GenAIService
import json

bp = Blueprint('ui', __name__, url_prefix='')

genai_service = GenAIService()

@bp.route('/')
def index():
    """Main UI page"""
    collections = Collection.query.all()
    collection_id = request.args.get('collection_id', type=int)
    
    # Get graph data if collection is selected
    graph = None
    if collection_id:
        collection = Collection.query.get(collection_id)
        if collection:
            topics = Topic.query.filter_by(collection_id=collection_id).all()
            relationships = TopicRelationship.query.join(
                Topic, TopicRelationship.source_topic_id == Topic.id
            ).filter(Topic.collection_id == collection_id).all()
            
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
            
            edges = []
            for rel in relationships:
                edges.append({
                    'source': f't{rel.source_topic_id}',
                    'target': f't{rel.target_topic_id}',
                    'weight': rel.similarity_score,
                    'type': rel.relationship_type
                })
            
            graph = {'nodes': nodes, 'edges': edges}
    
    return render_template('index.html', 
                         collections=collections, 
                         collection_id=collection_id,
                         graph=graph)

@bp.route('/collections/<int:collection_id>/graph')
def get_graph(collection_id):
    """Get graph HTML fragment"""
    collection = Collection.query.get_or_404(collection_id)
    topics = Topic.query.filter_by(collection_id=collection_id).all()
    relationships = TopicRelationship.query.join(
        Topic, TopicRelationship.source_topic_id == Topic.id
    ).filter(Topic.collection_id == collection_id).all()
    
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
    
    edges = []
    for rel in relationships:
        edges.append({
            'source': f't{rel.source_topic_id}',
            'target': f't{rel.target_topic_id}',
            'weight': rel.similarity_score,
            'type': rel.relationship_type
        })
    
    graph = {'nodes': nodes, 'edges': edges}
    return render_template('graph.html', graph=graph)

@bp.route('/topics/<int:topic_id>')
def get_topic_detail(topic_id):
    """Get topic detail HTML fragment"""
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
    
    topic_data = {
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
    }
    
    return render_template('topic_detail.html', topic=topic_data)

@bp.route('/topics/<int:topic_id>/qa', methods=['POST'])
def topic_qa_html(topic_id):
    """Topic-scoped Q&A with citations (HTML response)"""
    topic = Topic.query.get_or_404(topic_id)
    question = request.form.get('question') or (request.get_json() or {}).get('question')
    
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
        
        return render_template('qa_answer.html', 
                             answer=answer, 
                             citations=cited_documents,
                             topic_id=topic_id,
                             topic_name=topic.name)
    except Exception as e:
        return jsonify({'error': f'Failed to generate answer: {str(e)}'}), 500

@bp.route('/documents/<int:document_id>/preview')
def document_preview(document_id):
    """Get document preview HTML fragment"""
    document = Document.query.get_or_404(document_id)
    return render_template('document_preview.html', document=document)

@bp.route('/collections/<int:collection_id>/discover/status')
def get_discovery_status_html(collection_id):
    """Get discovery job status HTML fragment"""
    job = DiscoveryJob.query.filter_by(collection_id=collection_id).order_by(
        DiscoveryJob.created_at.desc()
    ).first()
    
    if not job:
        return render_template('job_status.html', job=None, collection_id=collection_id)
    
    job_data = {
        'id': job.id,
        'status': job.status.value,
        'progress': job.progress,
        'current_step': job.current_step,
        'error_message': job.error_message,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    }
    
    return render_template('job_status.html', job=job_data, collection_id=collection_id)


