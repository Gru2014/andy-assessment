import type { JobStatus } from '../api/client';
import { Card, ProgressBar, Badge } from './ui';

interface JobProgressProps {
  jobStatus: JobStatus | null;
}

const getStatusVariant = (status: string): 'primary' | 'success' | 'danger' => {
  switch (status) {
    case 'SUCCEEDED':
      return 'success';
    case 'FAILED':
      return 'danger';
    case 'RUNNING':
      return 'primary';
    default:
      return 'primary';
  }
};

export const JobProgressComponent: React.FC<JobProgressProps> = ({ jobStatus }) => {
  if (!jobStatus) return null;

  const statusVariant = getStatusVariant(jobStatus.status);

  return (
    <Card className="mb-4" padding="md" shadow="md">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <Badge variant={statusVariant} size="sm" className="mr-2">
            {jobStatus.status}
          </Badge>
          <span className="font-semibold text-gray-700">Status: {jobStatus.status}</span>
        </div>
        <span className="text-sm text-gray-500">
          {Math.round(jobStatus.progress * 100)}%
        </span>
      </div>
      {jobStatus.current_step && (
        <p className="text-sm text-gray-600 mb-2">{jobStatus.current_step}</p>
      )}
      <ProgressBar
        progress={jobStatus.progress}
        variant={statusVariant}
        showLabel={false}
      />
      {jobStatus.error_message && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          Error: {jobStatus.error_message}
        </div>
      )}
    </Card>
  );
};

