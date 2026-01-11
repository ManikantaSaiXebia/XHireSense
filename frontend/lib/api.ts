const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Job {
  id: number;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeAnalysis {
  id: number;
  match_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  bonus_skills: string[];
  reasoning: string;
  created_at: string;
}

export interface EmailStatus {
  id: number;
  status: 'NOT_SENT' | 'SENT' | 'RESPONSE_RECEIVED';
  form_link: string | null;
  sent_at: string | null;
  response_received_at: string | null;
}

export type BucketType = 'STRONG_FIT' | 'POTENTIAL' | 'REJECT';

export interface Resume {
  id: number;
  job_id: number;
  filename: string;
  bucket: BucketType;
  uploaded_at: string;
}

export interface ResumeWithAnalysis {
  resume: Resume;
  analysis: ResumeAnalysis | null;
  email_status: EmailStatus | null;
}

export interface JobDashboard {
  job_id: number;
  total_resumes: number;
  strong_fit_count: number;
  potential_count: number;
  reject_count: number;
  average_match_percentage: number | null;
  pending_screening_responses: number;
}

// Jobs API
export async function createJob(title: string, description: string): Promise<Job> {
  const response = await fetch(`${API_URL}/api/jobs/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, description }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create job');
  }
  
  return response.json();
}

export async function getJobs(): Promise<Job[]> {
  const response = await fetch(`${API_URL}/api/jobs/`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch jobs');
  }
  
  const data = await response.json();
  return data.jobs;
}

export async function getJob(id: number): Promise<Job> {
  const response = await fetch(`${API_URL}/api/jobs/${id}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch job');
  }
  
  return response.json();
}

export async function deleteJob(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/jobs/${id}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete job');
  }
}

export async function getJobDashboard(jobId: number): Promise<JobDashboard> {
  const response = await fetch(`${API_URL}/api/jobs/${jobId}/dashboard`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard');
  }
  
  return response.json();
}

// Resumes API
export async function uploadResume(
  jobId: number,
  file: File
): Promise<ResumeWithAnalysis> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('job_id', jobId.toString());
  
  const response = await fetch(`${API_URL}/api/resumes/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload resume');
  }
  
  return response.json();
}

export async function getResumes(
  jobId: number,
  bucket?: BucketType,
  minMatch?: number
): Promise<ResumeWithAnalysis[]> {
  const params = new URLSearchParams();
  if (bucket) params.append('bucket', bucket);
  if (minMatch !== undefined) params.append('min_match', minMatch.toString());
  
  const queryString = params.toString();
  const url = `${API_URL}/api/resumes/job/${jobId}${queryString ? `?${queryString}` : ''}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Failed to fetch resumes');
  }
  
  return response.json();
}

export async function updateBucket(
  resumeId: number,
  bucket: BucketType
): Promise<Resume> {
  const response = await fetch(`${API_URL}/api/resumes/${resumeId}/bucket`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ bucket }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update bucket');
  }
  
  return response.json();
}

export async function sendScreeningForm(
  resumeId: number,
  candidateEmail: string
): Promise<EmailStatus> {
  const formData = new FormData();
  formData.append('candidate_email', candidateEmail);
  
  const response = await fetch(`${API_URL}/api/resumes/${resumeId}/send-screening-form`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('Failed to send screening form');
  }
  
  return response.json();
}

export async function updateEmailStatus(
  resumeId: number,
  status: 'NOT_SENT' | 'SENT' | 'RESPONSE_RECEIVED',
  formLink?: string
): Promise<EmailStatus> {
  const response = await fetch(`${API_URL}/api/resumes/${resumeId}/email-status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status, form_link: formLink }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update email status');
  }
  
  return response.json();
}
