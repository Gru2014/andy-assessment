import axios from 'axios';

// Get API URL from environment variables
// Vite requires VITE_ prefix for environment variables to be exposed to the client
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Log in development to help with debugging
if (import.meta.env.DEV) {
  console.log('API Base URL:', API_BASE_URL);
  console.log('Environment:', import.meta.env.VITE_ENV || 'development');
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Add request interceptor for logging in development
if (import.meta.env.DEV) {
  apiClient.interceptors.request.use(
    (config) => {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // Add response interceptor for logging in development
  apiClient.interceptors.response.use(
    (response) => {
      console.log(`[API Response] ${response.status} ${response.config.url}`);
      return response;
    },
    (error) => {
      console.error('[API Response Error]', error.response?.status, error.response?.data || error.message);
      return Promise.reject(error);
    }
  );
}

export interface Collection {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
  document_count: number;
  topic_count: number;
}

export interface Document {
  id: number;
  title: string;
  content_preview?: string;
  content?: string;
  file_type?: string;
  created_at?: string;
}

export interface TopicNode {
  id: string;
  label: string;
  size_score: number;
  document_count: number;
  avg_confidence: number;
  color: string;
}

export interface TopicEdge {
  source: string;
  target: string;
  weight: number;
  type: string;
}

export interface TopicGraph {
  nodes: TopicNode[];
  edges: TopicEdge[];
}

export interface TopicDetail {
  id: number;
  name: string;
  document_count: number;
  size_score: number;
  insights: {
    summary?: string;
    themes: string[];
    common_questions: string[];
    related_concepts: string[];
  } | null;
  documents: Array<{
    id: number;
    title: string;
    content_preview: string;
    relevance_score: number;
    is_primary: boolean;
  }>;
  related_topics: Array<{
    id: number;
    name: string;
    similarity_score: number;
    relationship_type: string;
  }>;
}

export interface JobStatus {
  job_id: number;
  status: 'PENDING' | 'RUNNING' | 'FAILED' | 'SUCCEEDED';
  progress: number;
  current_step?: string;
  error_message?: string;
  created_at?: string;
  completed_at?: string;
}

export const collectionsApi = {
  list: () => apiClient.get<Collection[]>('/collections'),
  get: (id: number) => apiClient.get<Collection>(`/collections/${id}`),
  create: (data: { name: string; description?: string }) =>
    apiClient.post<Collection>('/collections', data),
  startDiscovery: (id: number, incremental?: boolean) =>
    apiClient.post<{ job_id: number; rq_job_id: string; status: string; collection_id: number }>(
      `/collections/${id}/discover`,
      { incremental }
    ),
  getDiscoveryStatus: (id: number) =>
    apiClient.get<JobStatus>(`/collections/${id}/discover/status`),
  addDocuments: (id: number, documents: Array<{ content: string; title?: string }>, triggerDiscovery?: boolean) =>
    apiClient.post<{ documents_added: number; document_ids: number[]; incremental_discovery_triggered: boolean }>(
      `/collections/${id}/documents`,
      { documents, trigger_discovery: triggerDiscovery !== false }
    ),
  getDocument: (id: number, docId: number) =>
    apiClient.get<Document>(`/collections/${id}/documents/${docId}`),
};

export const topicsApi = {
  getGraph: (collectionId: number) =>
    apiClient.get<TopicGraph>(`/collections/${collectionId}/topics/graph`),
  getTopic: (topicId: number) =>
    apiClient.get<TopicDetail>(`/topics/${topicId}`),
  askQuestion: (topicId: number, question: string) =>
    apiClient.post<{ answer: string; citations: Array<{ document_id: number; title: string; preview: string }>; topic_id: number; topic_name: string }>(
      `/topics/${topicId}/qa`,
      { question }
    ),
};

export const jobsApi = {
  get: (jobId: number) => apiClient.get<JobStatus>(`/jobs/${jobId}`),
  health: () => apiClient.get<{ status: string; service: string }>('/jobs/health'),
};

