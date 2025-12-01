import { useState, useEffect, useRef } from 'react';
import type { Collection, TopicGraph, TopicDetail, JobStatus } from './api/client';
import { collectionsApi, topicsApi } from './api/client';
import { TopicGraphComponent } from './components/TopicGraph';
import { TopicDetailComponent } from './components/TopicDetail';
import { JobProgressComponent } from './components/JobProgress';
import { Button, Select, Card, Heading } from './components/ui';

function App() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<number | null>(null);
  const [graph, setGraph] = useState<TopicGraph | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<TopicDetail | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [documentPreview, setDocumentPreview] = useState<{ id: number; title: string; content: string } | null>(null);
  const pollingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef<boolean>(false);

  useEffect(() => {
    loadCollections();
  }, []);

  useEffect(() => {
    if (selectedCollection) {
      loadGraph();
      startPolling();
    } else {
      stopPolling();
      setJobStatus(null);
    }

    // Cleanup: stop polling when collection changes or component unmounts
    return () => {
      stopPolling();
    };
  }, [selectedCollection]);

  const loadCollections = async () => {
    try {
      const response = await collectionsApi.list();
      setCollections(response.data);
      if (response.data.length > 0 && !selectedCollection) {
        setSelectedCollection(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load collections:', error);
    }
  };

  const loadGraph = async () => {
    if (!selectedCollection) return;
    try {
      const response = await topicsApi.getGraph(selectedCollection);
      setGraph(response.data);
    } catch (error) {
      console.error('Failed to load graph:', error);
    }
  };

  const stopPolling = () => {
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }
    isPollingRef.current = false;
  };

  const pollJobStatus = async () => {
    if (!selectedCollection || !isPollingRef.current) return;
    
    try {
      const response = await collectionsApi.getDiscoveryStatus(selectedCollection);
      setJobStatus(response.data);
      
      // Only continue polling if job is still running or pending
      if (response.data.status === 'RUNNING' || response.data.status === 'PENDING') {
        if (isPollingRef.current) {
          pollingTimeoutRef.current = setTimeout(() => pollJobStatus(), 2000);
        }
      } else {
        // Job completed or failed, stop polling
        stopPolling();
      }
    } catch (error: any) {
      // If job doesn't exist (404), stop polling
      if (error?.response?.status === 404) {
        stopPolling();
        setJobStatus(null);
      } else {
        console.error('Failed to poll job status:', error);
        // On other errors, stop polling to prevent infinite loop
        stopPolling();
      }
    }
  };

  const startPolling = () => {
    stopPolling(); // Clear any existing polling
    isPollingRef.current = true;
    pollJobStatus();
  };

  const handleStartDiscovery = async (incremental = false) => {
    if (!selectedCollection) return;
    setLoading(true);
    try {
      await collectionsApi.startDiscovery(selectedCollection, incremental);
      // Start polling after a short delay
      setTimeout(() => startPolling(), 1000);
    } catch (error) {
      console.error('Failed to start discovery:', error);
      alert('Failed to start discovery. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = async (nodeId: string) => {
    const topicId = parseInt(nodeId.replace('t', ''));
    try {
      const response = await topicsApi.getTopic(topicId);
      setSelectedTopic(response.data);
    } catch (error) {
      console.error('Failed to load topic:', error);
    }
  };

  const handleDocumentClick = async (documentId: number) => {
    if (!selectedCollection) return;
    try {
      const response = await collectionsApi.getDocument(selectedCollection, documentId);
      setDocumentPreview({
        id: response.data.id,
        title: response.data.title || 'Untitled',
        content: response.data.content || '',
      });
    } catch (error) {
      console.error('Failed to load document:', error);
    }
  };

  const handleAddDocuments = async () => {
    const content = prompt('Enter document content:');
    if (!content || !selectedCollection) return;
    setLoading(true);
    try {
      await collectionsApi.addDocuments(selectedCollection, [{ content }], true);
      setTimeout(() => {
        loadGraph();
        startPolling();
      }, 1000);
    } catch (error) {
      console.error('Failed to add document:', error);
      alert('Failed to add document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Heading level={1}>Topic Discovery System</Heading>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Select
              label="Collection:"
              value={selectedCollection || ''}
              onChange={(e) => setSelectedCollection(parseInt(e.target.value))}
              options={collections.map((c) => ({
                value: c.id,
                label: `${c.name} (${c.document_count} docs, ${c.topic_count} topics)`,
              }))}
              className="w-64"
            />
          </div>
          <div className="flex space-x-2">
            <Button
              variant="primary"
              onClick={() => handleStartDiscovery(false)}
              disabled={loading || !selectedCollection}
              isLoading={loading}
            >
              Full Discovery
            </Button>
            <Button
              variant="success"
              onClick={() => handleStartDiscovery(true)}
              disabled={loading || !selectedCollection}
              isLoading={loading}
            >
              Incremental Update
            </Button>
            <Button
              variant="info"
              onClick={handleAddDocuments}
              disabled={loading || !selectedCollection}
              isLoading={loading}
            >
              Add Document
            </Button>
          </div>
        </div>

        {jobStatus && <JobProgressComponent jobStatus={jobStatus} />}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card padding="md" shadow="lg">
              <Heading level={2} className="mb-4">Topic Graph</Heading>
              {graph && graph.nodes.length > 0 ? (
                <TopicGraphComponent
                  graph={graph}
                  onNodeClick={handleNodeClick}
                  width={800}
                  height={600}
                />
              ) : (
                <div className="flex items-center justify-center h-96 text-gray-500">
                  {graph ? 'No topics found. Start discovery to generate topics.' : 'Loading graph...'}
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-6">
            {selectedTopic && (
              <TopicDetailComponent
                topic={selectedTopic}
                onDocumentClick={handleDocumentClick}
              />
            )}

            {documentPreview && (
              <Card padding="lg" shadow="lg">
                <div className="flex items-center justify-between mb-4">
                  <Heading level={3}>{documentPreview.title}</Heading>
                  <button
                    onClick={() => setDocumentPreview(null)}
                    className="text-gray-500 hover:text-gray-700 text-xl font-bold"
                  >
                    ✕
                  </button>
                </div>
                <div className="max-h-96 overflow-y-auto text-gray-700 whitespace-pre-wrap">
                  {documentPreview.content}
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
