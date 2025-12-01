from typing import List, Dict, Any
from app import db
from app.models import Topic, TopicInsight, DocumentTopic, Document
from app.services.genai_service import GenAIService
import json

class InsightService:
    """Service for generating topic insights"""
    
    def __init__(self):
        self.genai = GenAIService()
    
    def generate_insights(self, topic_id: int) -> TopicInsight:
        """Generate insights for a topic"""
        topic = Topic.query.get_or_404(topic_id)
        
        # Get documents for this topic
        assignments = DocumentTopic.query.filter_by(topic_id=topic_id).order_by(
            DocumentTopic.relevance_score.desc()
        ).limit(10).all()
        
        documents = [assignment.document for assignment in assignments]
        
        # Prepare document excerpts
        doc_texts = [doc.content[:500] for doc in documents[:5]]
        combined_text = "\n\n---\n\n".join(doc_texts)
        
        prompt = f"""Analyze the following documents related to the topic "{topic.name}" and provide insights in JSON format.

Documents:
{combined_text[:3000]}

Provide a JSON response with the following structure:
{{
  "summary": "2-3 sentence summary of the topic",
  "themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
  "common_questions": ["question1", "question2", "question3", "question4", "question5"],
  "related_concepts": ["concept1", "concept2", "concept3", "concept4", "concept5"]
}}

Return only valid JSON, no other text:"""
        
        try:
            response = self.genai.chat_completion([
                {'role': 'system', 'content': 'You are a helpful assistant that analyzes documents and provides structured insights in JSON format.'},
                {'role': 'user', 'content': prompt}
            ])
            
            # Parse JSON response
            insights_data = json.loads(response)
            
            # Get or create insight
            insight = TopicInsight.query.filter_by(topic_id=topic_id).first()
            if not insight:
                insight = TopicInsight(topic_id=topic_id)
                db.session.add(insight)
            
            insight.summary = insights_data.get('summary', '')
            insight.themes = insights_data.get('themes', [])[:5]
            insight.common_questions = insights_data.get('common_questions', [])[:5]
            insight.related_concepts = insights_data.get('related_concepts', [])[:5]
            
            db.session.commit()
            return insight
            
        except Exception as e:
            # Create fallback insight
            insight = TopicInsight.query.filter_by(topic_id=topic_id).first()
            if not insight:
                insight = TopicInsight(
                    topic_id=topic_id,
                    summary=f"Topic: {topic.name}",
                    themes=[],
                    common_questions=[],
                    related_concepts=[]
                )
                db.session.add(insight)
                db.session.commit()
            return insight
    
    def generate_insights_batch(self, topic_ids: List[int]) -> List[TopicInsight]:
        """Generate insights for multiple topics"""
        insights = []
        for topic_id in topic_ids:
            try:
                insight = self.generate_insights(topic_id)
                insights.append(insight)
            except Exception as e:
                # Continue with other topics even if one fails
                print(f"Failed to generate insights for topic {topic_id}: {str(e)}")
                continue
        return insights

