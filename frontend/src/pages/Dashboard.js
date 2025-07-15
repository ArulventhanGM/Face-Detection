import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { 
  Users, 
  Camera, 
  Clock, 
  HardDrive,
  TrendingUp,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load system stats and health check in parallel
      const [statsResponse, healthResponse] = await Promise.all([
        apiService.getStats(),
        apiService.healthCheck()
      ]);

      setStats(statsResponse.data.data);
      setSystemHealth(healthResponse.data.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatUptime = (timestamp) => {
    const now = new Date();
    const uptime = new Date(timestamp);
    const diffMs = now - uptime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays} days`;
    if (diffHours > 0) return `${diffHours} hours`;
    return `${diffMins} minutes`;
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">System Dashboard</h1>
          <p className="card-description">
            Overview of your face recognition system status and statistics
          </p>
        </div>

        {/* System Health Status */}
        <div className="system-health" style={{ marginBottom: '2rem' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem',
            padding: '1rem',
            background: systemHealth?.status === 'healthy' ? '#c6f6d5' : '#fed7d7',
            borderRadius: '8px',
            border: `1px solid ${systemHealth?.status === 'healthy' ? '#38a169' : '#e53e3e'}`
          }}>
            {systemHealth?.status === 'healthy' ? (
              <CheckCircle size={20} color="#38a169" />
            ) : (
              <AlertCircle size={20} color="#e53e3e" />
            )}
            <span style={{ 
              fontWeight: '600',
              color: systemHealth?.status === 'healthy' ? '#22543d' : '#742a2a'
            }}>
              System Status: {systemHealth?.status === 'healthy' ? 'Healthy' : 'Error'}
            </span>
            {systemHealth?.known_faces_loaded !== undefined && (
              <span style={{ marginLeft: 'auto', fontSize: '0.875rem' }}>
                {systemHealth.known_faces_loaded} faces loaded
              </span>
            )}
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">
              <Users size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
              {stats?.known_faces_count || 0}
            </div>
            <div className="stat-label">Known Faces</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">
              <Camera size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
              {stats?.recent_recognitions || 0}
            </div>
            <div className="stat-label">Recent Recognitions</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">
              <HardDrive size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
              {stats?.total_storage_formatted || '0B'}
            </div>
            <div className="stat-label">Storage Used</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">
              <Clock size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
              {stats?.uptime ? formatUptime(stats.uptime) : 'N/A'}
            </div>
            <div className="stat-label">Uptime</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h2 style={{ marginBottom: '1rem', color: '#2d3748' }}>Quick Actions</h2>
          <div className="grid grid-2">
            <div className="action-card" style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Users size={32} style={{ marginBottom: '1rem' }} />
              <h3>Manage Known Faces</h3>
              <p style={{ marginBottom: '1rem', opacity: 0.9 }}>
                Add, edit, or remove known faces in the system
              </p>
              <a 
                href="/admin" 
                className="btn btn-secondary"
                style={{ textDecoration: 'none' }}
              >
                Go to Admin Panel
              </a>
            </div>

            <div className="action-card" style={{ 
              background: 'linear-gradient(135deg, #38a169 0%, #2f855a 100%)',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Camera size={32} style={{ marginBottom: '1rem' }} />
              <h3>Recognize Faces</h3>
              <p style={{ marginBottom: '1rem', opacity: 0.9 }}>
                Upload images to identify and recognize faces
              </p>
              <a 
                href="/recognize" 
                className="btn btn-secondary"
                style={{ textDecoration: 'none' }}
              >
                Start Recognition
              </a>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="recent-activity" style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem', color: '#2d3748' }}>
            System Information
          </h2>
          <div className="info-grid" style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '1rem' 
          }}>
            <div style={{ 
              padding: '1rem', 
              background: '#f7fafc', 
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ color: '#2d3748', marginBottom: '0.5rem' }}>
                Face Detection Engine
              </h4>
              <p style={{ color: '#718096', fontSize: '0.875rem' }}>
                Using advanced deep learning models for accurate face detection and recognition
              </p>
            </div>

            <div style={{ 
              padding: '1rem', 
              background: '#f7fafc', 
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ color: '#2d3748', marginBottom: '0.5rem' }}>
                Security & Privacy
              </h4>
              <p style={{ color: '#718096', fontSize: '0.875rem' }}>
                All face data is stored securely with encryption and access controls
              </p>
            </div>

            <div style={{ 
              padding: '1rem', 
              background: '#f7fafc', 
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ color: '#2d3748', marginBottom: '0.5rem' }}>
                Real-time Processing
              </h4>
              <p style={{ color: '#718096', fontSize: '0.875rem' }}>
                Fast and efficient processing of group photos and individual images
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
