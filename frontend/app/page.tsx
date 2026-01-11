'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getJobs, deleteJob, Job } from '@/lib/api';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<number | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  async function loadJobs() {
    try {
      setLoading(true);
      const data = await getJobs();
      setJobs(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(jobId: number) {
    try {
      setDeletingJobId(jobId);
      setError(null);
      await deleteJob(jobId);
      // Remove the job from the UI immediately
      setJobs(prevJobs => prevJobs.filter(job => job.id !== jobId));
      setConfirmDeleteId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete job posting');
    } finally {
      setDeletingJobId(null);
    }
  }

  return (
    <div className="container">
      <header style={{ marginBottom: '2rem', paddingBottom: '2rem', borderBottom: '2px solid #e5e7eb' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          XHireSense
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Explainable AI for Smarter Hiring Decisions
        </p>
      </header>

      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.875rem', fontWeight: '600' }}>Job Postings</h2>
        <Link href="/jobs" className="btn btn-primary">
          Create New Job
        </Link>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
            No jobs yet. Create your first job posting to get started.
          </p>
          <Link href="/jobs" className="btn btn-primary">
            Create First Job
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-2">
            {jobs.map((job) => (
              <div key={job.id} style={{ position: 'relative' }}>
                <Link href={`/jobs/${job.id}`}>
                  <div className="card" style={{ cursor: 'pointer', transition: 'transform 0.2s, box-shadow 0.2s' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)';
                    }}
                  >
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setConfirmDeleteId(job.id);
                      }}
                      style={{
                        position: 'absolute',
                        top: '1rem',
                        right: '1rem',
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '1.25rem',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.375rem',
                        transition: 'background-color 0.2s',
                        zIndex: 10
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#fee2e2';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                      disabled={deletingJobId === job.id}
                      title="Delete job posting"
                    >
                      🗑
                    </button>
                    <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '0.5rem', paddingRight: '2.5rem' }}>
                      {job.title}
                    </h3>
                    <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '1rem' }}>
                      Created {new Date(job.created_at).toLocaleDateString()}
                    </p>
                    <div style={{ 
                      color: '#4b5563', 
                      fontSize: '0.9rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical'
                    }}>
                      {job.description}
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>

          {/* Confirmation Dialog */}
          {confirmDeleteId && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}
            onClick={() => setConfirmDeleteId(null)}
            >
              <div className="card" style={{
                maxWidth: '400px',
                width: '90%',
                margin: '0 auto'
              }}
              onClick={(e) => e.stopPropagation()}
              >
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
                  Confirm Deletion
                </h3>
                <p style={{ color: '#4b5563', marginBottom: '1.5rem' }}>
                  Are you sure you want to delete this job posting? This action cannot be undone.
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setConfirmDeleteId(null)}
                    disabled={deletingJobId === confirmDeleteId}
                  >
                    Cancel
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleDelete(confirmDeleteId)}
                    disabled={deletingJobId === confirmDeleteId}
                  >
                    {deletingJobId === confirmDeleteId ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
