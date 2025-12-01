import { useState } from 'react';
import type { TopicDetail } from '../api/client';
import { topicsApi } from '../api/client';
import { Card, Button, TextArea, Badge, Heading } from './ui';

interface TopicDetailProps {
  topic: TopicDetail;
  onDocumentClick: (documentId: number) => void;
}

export const TopicDetailComponent: React.FC<TopicDetailProps> = ({
  topic,
  onDocumentClick,
}) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<{ answer: string; citations: Array<{ document_id: number; title: string; preview: string }> } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAskQuestion = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const response = await topicsApi.askQuestion(topic.id, question);
      setAnswer(response.data);
    } catch (error) {
      console.error('Failed to get answer:', error);
      alert('Failed to get answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderAnswerWithCitations = (text: string, citations: Array<{ document_id: number; title: string; preview: string }>) => {
    const parts = text.split(/(\[Doc\d+\])/g);
    return parts.map((part, index) => {
      const citationMatch = part.match(/\[Doc(\d+)\]/);
      if (citationMatch) {
        const docIndex = parseInt(citationMatch[1]) - 1;
        const citation = citations[docIndex];
        if (citation) {
          return (
            <span
              key={index}
              className="text-blue-600 underline cursor-pointer hover:text-blue-800"
              onClick={() => onDocumentClick(citation.document_id)}
              title={citation.title}
            >
              {part}
            </span>
          );
        }
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <Card padding="lg" shadow="lg" className="space-y-6">
      <div>
        <Heading level={2}>{topic.name}</Heading>
        <p className="text-sm text-gray-500 mt-1">
          {topic.document_count} documents • Size score: {topic.size_score.toFixed(2)}
        </p>
      </div>

      {topic.insights && (
        <div className="space-y-4">
          {topic.insights.summary && (
            <div>
              <Heading level={3} className="mb-2">Summary</Heading>
              <p className="text-gray-600">{topic.insights.summary}</p>
            </div>
          )}

          {topic.insights.themes && topic.insights.themes.length > 0 && (
            <div>
              <Heading level={3} className="mb-2">Key Themes</Heading>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {topic.insights.themes.map((theme, idx) => (
                  <li key={idx}>{theme}</li>
                ))}
              </ul>
            </div>
          )}

          {topic.insights.common_questions && topic.insights.common_questions.length > 0 && (
            <div>
              <Heading level={3} className="mb-2">Common Questions</Heading>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {topic.insights.common_questions.map((q, idx) => (
                  <li key={idx}>{q}</li>
                ))}
              </ul>
            </div>
          )}

          {topic.insights.related_concepts && topic.insights.related_concepts.length > 0 && (
            <div>
              <Heading level={3} className="mb-2">Related Concepts</Heading>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {topic.insights.related_concepts.map((concept, idx) => (
                  <li key={idx}>{concept}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div>
        <Heading level={3} className="mb-3">Documents</Heading>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {topic.documents.map((doc) => (
            <div
              key={doc.id}
              className="border border-gray-200 rounded p-3 hover:bg-gray-50 cursor-pointer"
              onClick={() => onDocumentClick(doc.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800">{doc.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{doc.content_preview}</p>
                </div>
                <div className="ml-4 flex flex-col items-end space-y-1">
                  {doc.is_primary && (
                    <Badge variant="primary" size="sm">
                      Primary
                    </Badge>
                  )}
                  <span className="text-xs text-gray-500">
                    Relevance: {(doc.relevance_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {topic.related_topics && topic.related_topics.length > 0 && (
        <div>
          <Heading level={3} className="mb-2">Related Topics</Heading>
          <div className="flex flex-wrap gap-2">
            {topic.related_topics.map((rt) => (
              <Badge key={rt.id} variant="default" size="md">
                {rt.name} ({(rt.similarity_score * 100).toFixed(0)}%)
              </Badge>
            ))}
          </div>
        </div>
      )}

      <div className="border-t pt-4">
        <Heading level={3} className="mb-3">Ask a Question</Heading>
        <div className="space-y-3">
          <TextArea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this topic..."
            rows={3}
          />
          <Button
            variant="primary"
            onClick={handleAskQuestion}
            disabled={loading || !question.trim()}
            isLoading={loading}
          >
            Ask Question
          </Button>
        </div>

        {answer && (
          <div className="mt-4 p-4 bg-blue-50 rounded-md">
            <h4 className="font-semibold text-gray-800 mb-2">Answer:</h4>
            <p className="text-gray-700 whitespace-pre-wrap">
              {renderAnswerWithCitations(answer.answer, answer.citations)}
            </p>
            {answer.citations && answer.citations.length > 0 && (
              <div className="mt-3 pt-3 border-t border-blue-200">
                <p className="text-sm font-semibold text-gray-700 mb-2">Citations:</p>
                <ul className="space-y-1">
                  {answer.citations.map((citation, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer"
                      onClick={() => onDocumentClick(citation.document_id)}
                    >
                      [{idx + 1}] {citation.title}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

