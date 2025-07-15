import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { 
  History as HistoryIcon, 
  Calendar, 
  Clock, 
  Users, 
  Eye,
  RefreshCw,
  Image as ImageIcon
} from 'lucide-react';
import toast from 'react-hot-toast';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await apiService.recognition.getHistory(100);
      setHistory(response.data.data);
    } catch (error) {
      console.error('Error loading history:', error);
      toast.error('Failed to load recognition history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatProcessingTime = (seconds) => {
    return `${seconds?.toFixed(2)}s`;
  };

  const viewDetails = (record) => {
    setSelectedRecord(record);
  };

  const closeDetails = () => {
    setSelectedRecord(null);
  };

  return (
    <div className="history">
      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 className="card-title">Recognition History</h1>
              <p className="card-description">
                View all past face recognition results and analysis
              </p>
            </div>
            <button 
              onClick={loadHistory}
              className="btn btn-secondary"
              disabled={loading}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="loading-spinner"></div>
            <p style={{ marginTop: '1rem' }}>Loading history...</p>
          </div>
        ) : history.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '3rem',
            background: '#f7fafc',
            borderRadius: '8px',
            border: '1px solid #e2e8f0'
          }}>
            <HistoryIcon size={48} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
            <h3 style={{ color: '#4a5568', marginBottom: '0.5rem' }}>No recognition history</h3>
            <p style={{ color: '#718096' }}>Recognition results will appear here after processing images</p>
          </div>
        ) : (
          <>
            {/* Summary Stats */}
            <div className="stats-grid" style={{ marginBottom: '2rem' }}>
              <div className="stat-card">
                <div className="stat-value">
                  <HistoryIcon size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
                  {history.length}
                </div>
                <div className="stat-label">Total Sessions</div>
              </div>

              <div className="stat-card">
                <div className="stat-value">
                  <Users size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
                  {history.reduce((sum, record) => sum + record.total_faces_detected, 0)}
                </div>
                <div className="stat-label">Faces Detected</div>
              </div>

              <div className="stat-card">
                <div className="stat-value">
                  <Eye size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
                  {history.reduce((sum, record) => sum + record.total_faces_recognized, 0)}
                </div>
                <div className="stat-label">Faces Recognized</div>
              </div>

              <div className="stat-card">
                <div className="stat-value">
                  <Clock size={24} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
                  {history.length > 0 ? 
                    formatProcessingTime(
                      history.reduce((sum, record) => sum + (record.processing_time || 0), 0) / history.length
                    ) : '0s'
                  }
                </div>
                <div className="stat-label">Avg. Processing Time</div>
              </div>
            </div>

            {/* History Table */}
            <div style={{ overflowX: 'auto' }}>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Image</th>
                    <th>Faces Detected</th>
                    <th>Faces Recognized</th>
                    <th>Processing Time</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((record) => (
                    <tr key={record.id}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Calendar size={16} color="#718096" />
                          {formatDate(record.created_at)}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <ImageIcon size={16} color="#718096" />
                          {record.test_image_path ? 
                            record.test_image_path.split('/').pop() : 
                            'Unknown'
                          }
                        </div>
                      </td>
                      <td>
                        <span style={{ 
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          padding: '0.25rem 0.5rem',
                          background: '#e6fffa',
                          color: '#234e52',
                          borderRadius: '4px',
                          fontSize: '0.875rem',
                          fontWeight: '600'
                        }}>
                          <Users size={14} />
                          {record.total_faces_detected}
                        </span>
                      </td>
                      <td>
                        <span style={{ 
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          padding: '0.25rem 0.5rem',
                          background: record.total_faces_recognized > 0 ? '#c6f6d5' : '#fed7d7',
                          color: record.total_faces_recognized > 0 ? '#22543d' : '#742a2a',
                          borderRadius: '4px',
                          fontSize: '0.875rem',
                          fontWeight: '600'
                        }}>
                          <Eye size={14} />
                          {record.total_faces_recognized}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Clock size={16} color="#718096" />
                          {formatProcessingTime(record.processing_time)}
                        </div>
                      </td>
                      <td>
                        <button 
                          onClick={() => viewDetails(record)}
                          className="btn btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.5rem 0.75rem' }}
                        >
                          <Eye size={14} />
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Details Modal */}
      {selectedRecord && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem'
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            maxWidth: '800px',
            width: '100%',
            maxHeight: '90vh',
            overflow: 'auto',
            position: 'relative'
          }}>
            <div style={{
              padding: '1.5rem',
              borderBottom: '1px solid #e2e8f0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h2 style={{ margin: 0, color: '#2d3748' }}>Recognition Details</h2>
              <button 
                onClick={closeDetails}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#718096'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              {/* Session Info */}
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>Session Information</h3>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: '1rem',
                  padding: '1rem',
                  background: '#f7fafc',
                  borderRadius: '8px'
                }}>
                  <div>
                    <strong>Date & Time:</strong><br />
                    {formatDate(selectedRecord.created_at)}
                  </div>
                  <div>
                    <strong>Processing Time:</strong><br />
                    {formatProcessingTime(selectedRecord.processing_time)}
                  </div>
                  <div>
                    <strong>Faces Detected:</strong><br />
                    {selectedRecord.total_faces_detected}
                  </div>
                  <div>
                    <strong>Faces Recognized:</strong><br />
                    {selectedRecord.total_faces_recognized}
                  </div>
                </div>
              </div>

              {/* Test Image */}
              {selectedRecord.test_image_path && (
                <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                  <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>Test Image</h3>
                  <img 
                    src={apiService.images.getTestImageUrl(selectedRecord.test_image_path.split('/').pop())}
                    alt="Test"
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '300px', 
                      borderRadius: '8px',
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}

              {/* Recognized Faces */}
              <div>
                <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>
                  Recognized Faces ({selectedRecord.recognized_faces.length})
                </h3>
                {selectedRecord.recognized_faces.length === 0 ? (
                  <p style={{ color: '#718096', fontStyle: 'italic' }}>No faces were recognized in this image.</p>
                ) : (
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
                    gap: '1rem' 
                  }}>
                    {selectedRecord.recognized_faces.map((face, index) => (
                      <div 
                        key={index}
                        style={{
                          padding: '1rem',
                          background: face.name === 'Unknown' ? '#fed7d7' : '#c6f6d5',
                          borderRadius: '8px',
                          border: `1px solid ${face.name === 'Unknown' ? '#e53e3e' : '#38a169'}`
                        }}
                      >
                        <h4 style={{ 
                          margin: '0 0 0.5rem 0', 
                          color: face.name === 'Unknown' ? '#742a2a' : '#22543d'
                        }}>
                          {face.name}
                        </h4>
                        
                        {face.name !== 'Unknown' && (
                          <>
                            {face.employee_id && face.employee_id !== 'N/A' && (
                              <p style={{ margin: '0.25rem 0', fontSize: '0.875rem' }}>
                                <strong>ID:</strong> {face.employee_id}
                              </p>
                            )}
                            {face.department && face.department !== 'N/A' && (
                              <p style={{ margin: '0.25rem 0', fontSize: '0.875rem' }}>
                                <strong>Dept:</strong> {face.department}
                              </p>
                            )}
                            {face.confidence && (
                              <p style={{ margin: '0.25rem 0', fontSize: '0.875rem' }}>
                                <strong>Confidence:</strong> {(face.confidence * 100).toFixed(1)}%
                              </p>
                            )}
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;
