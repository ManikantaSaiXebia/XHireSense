'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { 
  getJob, 
  getResumes, 
  uploadResume, 
  getJobDashboard,
  updateBucket,
  sendScreeningForm,
  Job,
  ResumeWithAnalysis,
  JobDashboard,
  BucketType
} from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';

type TabType = 'all' | 'STRONG_FIT' | 'POTENTIAL' | 'REJECT';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = parseInt(params.id as string);

  const [job, setJob] = useState<Job | null>(null);
  const [resumes, setResumes] = useState<ResumeWithAnalysis[]>([]);
  const [dashboard, setDashboard] = useState<JobDashboard | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    if (jobId) {
      loadData();
    }
  }, [jobId, activeTab]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      
      const [jobData, resumesData, dashboardData] = await Promise.all([
        getJob(jobId),
        getResumes(jobId, activeTab === 'all' ? undefined : activeTab),
        getJobDashboard(jobId)
      ]);
      
      setJob(jobData);
      setResumes(resumesData);
      setDashboard(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      await uploadResume(jobId, file);
      setShowUpload(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload resume');
    } finally {
      setUploading(false);
      // Reset file input
      e.target.value = '';
    }
  }

  async function handleBucketChange(resumeId: number, newBucket: BucketType) {
    try {
      await updateBucket(resumeId, newBucket);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update bucket');
    }
  }

  async function handleSendScreeningForm(resumeId: number) {
    const email = prompt('Enter candidate email address:');
    if (!email) return;

    try {
      await sendScreeningForm(resumeId, email);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send screening form');
    }
  }

  if (loading && !job) {
    return (
      <div className="container">
        <div className="loading">Loading job details...</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="container">
        <div className="error">Job not found</div>
        <Link href="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>
          Back to Jobs
        </Link>
      </div>
    );
  }

  return (
    <div className="container">
      <header style={{ marginBottom: '2rem' }}>
        <Link href="/" style={{ color: '#2563eb', marginBottom: '1rem', display: 'inline-block' }}>
          ← Back to Jobs
        </Link>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          {job.title}
        </h1>
      </header>

      {error && <div className="error">{error}</div>}

      {/* Dashboard Stats */}
      {dashboard && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1.5rem' }}>
            Dashboard
          </h2>
          <div className="grid grid-3">
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2563eb' }}>
                {dashboard.total_resumes}
              </div>
              <div style={{ color: '#6b7280' }}>Total Resumes</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
                {dashboard.strong_fit_count}
              </div>
              <div style={{ color: '#6b7280' }}>Strong Fit</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                {dashboard.potential_count}
              </div>
              <div style={{ color: '#6b7280' }}>Potential</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>
                {dashboard.reject_count}
              </div>
              <div style={{ color: '#6b7280' }}>Reject</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2563eb' }}>
                {dashboard.average_match_percentage?.toFixed(1) ?? 'N/A'}%
              </div>
              <div style={{ color: '#6b7280' }}>Avg Match</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#8b5cf6' }}>
                {dashboard.pending_screening_responses}
              </div>
              <div style={{ color: '#6b7280' }}>Pending Responses</div>
            </div>
          </div>
        </div>
      )}

      {/* Job Description */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem' }}>
          Job Description
        </h2>
        <div style={{ color: '#4b5563', lineHeight: '1.6' }}>
          <ReactMarkdown>{job.description}</ReactMarkdown>
        </div>
      </div>

      {/* Resume Upload */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600' }}>
            Resumes
          </h2>
          {!showUpload && (
            <button
              className="btn btn-primary"
              onClick={() => setShowUpload(true)}
            >
              Upload Resume
            </button>
          )}
        </div>

        {showUpload && (
          <div style={{ 
            padding: '1.5rem', 
            backgroundColor: '#f9fafb', 
            borderRadius: '0.5rem',
            marginBottom: '1rem'
          }}>
            <label htmlFor="resume-upload" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Select PDF file:
            </label>
            <input
              id="resume-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ marginBottom: '1rem' }}
            />
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setShowUpload(false)}
                disabled={uploading}
              >
                Cancel
              </button>
              {uploading && <span style={{ color: '#6b7280' }}>Uploading and analyzing...</span>}
            </div>
          </div>
        )}

        {/* Bucket Tabs */}
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All ({dashboard?.total_resumes || 0})
          </button>
          <button
            className={`tab ${activeTab === 'STRONG_FIT' ? 'active' : ''}`}
            onClick={() => setActiveTab('STRONG_FIT')}
          >
            Strong Fit ({dashboard?.strong_fit_count || 0})
          </button>
          <button
            className={`tab ${activeTab === 'POTENTIAL' ? 'active' : ''}`}
            onClick={() => setActiveTab('POTENTIAL')}
          >
            Potential ({dashboard?.potential_count || 0})
          </button>
          <button
            className={`tab ${activeTab === 'REJECT' ? 'active' : ''}`}
            onClick={() => setActiveTab('REJECT')}
          >
            Reject ({dashboard?.reject_count || 0})
          </button>
        </div>

        {/* Resume List */}
        {loading ? (
          <div className="loading">Loading resumes...</div>
        ) : resumes.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
            No resumes found. Upload resumes to get started.
          </div>
        ) : (
          <div className="grid grid-2">
            {resumes.map((item) => (
              <ResumeCard
                key={item.resume.id}
                resume={item}
                onBucketChange={handleBucketChange}
                onSendScreeningForm={handleSendScreeningForm}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ResumeCard({
  resume,
  onBucketChange,
  onSendScreeningForm,
}: {
  resume: ResumeWithAnalysis;
  onBucketChange: (resumeId: number, bucket: BucketType) => void;
  onSendScreeningForm: (resumeId: number) => void;
}) {
  const getBucketBadgeClass = (bucket: string) => {
    switch (bucket) {
      case 'STRONG_FIT':
        return 'badge-strong';
      case 'POTENTIAL':
        return 'badge-potential';
      case 'REJECT':
        return 'badge-reject';
      default:
        return '';
    }
  };

  const getBucketLabel = (bucket: string) => {
    switch (bucket) {
      case 'STRONG_FIT':
        return 'Strong Fit';
      case 'POTENTIAL':
        return 'Potential';
      case 'REJECT':
        return 'Reject';
      default:
        return bucket;
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
            {resume.resume.filename}
          </h3>
          <span className={`badge ${getBucketBadgeClass(resume.resume.bucket)}`}>
            {getBucketLabel(resume.resume.bucket)}
          </span>
        </div>
        {resume.analysis && (
          <div style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold',
            color: resume.analysis.match_percentage >= 80 ? '#10b981' :
                   resume.analysis.match_percentage >= 60 ? '#f59e0b' : '#ef4444'
          }}>
            {resume.analysis.match_percentage.toFixed(1)}%
          </div>
        )}
      </div>

      {resume.analysis ? (
        <div>
          {/* Reasoning */}
          <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
            <p style={{ fontSize: '0.9rem', color: '#4b5563', lineHeight: '1.6' }}>
              {resume.analysis.reasoning}
            </p>
          </div>

          {/* Skills */}
          {resume.analysis.matched_skills.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontWeight: '500', marginBottom: '0.5rem', color: '#10b981' }}>
                ✔ Matched Skills
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {resume.analysis.matched_skills.map((skill, idx) => (
                  <span key={idx} style={{ 
                    padding: '0.25rem 0.75rem', 
                    backgroundColor: '#d1fae5', 
                    color: '#065f46',
                    borderRadius: '9999px',
                    fontSize: '0.875rem'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {resume.analysis.missing_skills.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontWeight: '500', marginBottom: '0.5rem', color: '#f59e0b' }}>
                ⚠ Missing Skills
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {resume.analysis.missing_skills.map((skill, idx) => (
                  <span key={idx} style={{ 
                    padding: '0.25rem 0.75rem', 
                    backgroundColor: '#fef3c7', 
                    color: '#92400e',
                    borderRadius: '9999px',
                    fontSize: '0.875rem'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {resume.analysis.bonus_skills.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontWeight: '500', marginBottom: '0.5rem', color: '#8b5cf6' }}>
                ⭐ Bonus Skills
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {resume.analysis.bonus_skills.map((skill, idx) => (
                  <span key={idx} style={{ 
                    padding: '0.25rem 0.75rem', 
                    backgroundColor: '#ede9fe', 
                    color: '#5b21b6',
                    borderRadius: '9999px',
                    fontSize: '0.875rem'
                  }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>
          Analysis pending...
        </div>
      )}

      {/* Actions */}
      <div style={{ 
        marginTop: '1rem', 
        paddingTop: '1rem', 
        borderTop: '1px solid #e5e7eb',
        display: 'flex',
        gap: '0.5rem',
        flexWrap: 'wrap'
      }}>
        <button
          className="btn btn-success"
          style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
          onClick={() => onSendScreeningForm(resume.resume.id)}
          disabled={resume.email_status?.status === 'SENT' || resume.email_status?.status === 'RESPONSE_RECEIVED'}
        >
          {resume.email_status?.status === 'SENT' || resume.email_status?.status === 'RESPONSE_RECEIVED' 
            ? 'Screening Form Sent' 
            : 'Send Screening Form'}
        </button>
        
        <select
          value={resume.resume.bucket}
          onChange={(e) => onBucketChange(resume.resume.id, e.target.value as BucketType)}
          style={{ 
            padding: '0.5rem 1rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.5rem',
            fontSize: '0.875rem',
            cursor: 'pointer'
          }}
        >
          <option value="STRONG_FIT">Strong Fit</option>
          <option value="POTENTIAL">Potential</option>
          <option value="REJECT">Reject</option>
        </select>
      </div>

      {resume.email_status && resume.email_status.status !== 'NOT_SENT' && (
        <div style={{ 
          marginTop: '0.5rem', 
          fontSize: '0.875rem', 
          color: '#6b7280' 
        }}>
          Email Status: {resume.email_status.status === 'SENT' ? 'Sent' : 'Response Received'}
        </div>
      )}
    </div>
  );
}
