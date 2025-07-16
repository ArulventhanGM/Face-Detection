import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
import ExportModal from '../components/ExportModal';
import {
  Upload,
  Camera,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  Download,
  RotateCcw,
  ZoomIn,
  User,
  Mail,
  Phone,
  Building,
  Badge,
  Target,
  Share
} from 'lucide-react';
import toast from 'react-hot-toast';

const FaceRecognition = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFace, setSelectedFace] = useState(null);
  const [imageViewMode, setImageViewMode] = useState('original'); // 'original', 'annotated', 'split'
  const [showExportModal, setShowExportModal] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setRecognitionResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
    },
    maxFiles: 1,
    maxSize: 16 * 1024 * 1024 // 16MB
  });

  const handleRecognize = async () => {
    if (!selectedFile) {
      toast.error('Please select an image first');
      return;
    }

    setLoading(true);
    setRecognitionResult(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await apiService.recognition.recognizeFaces(formData);
      setRecognitionResult(response.data.data);
      toast.success('Face recognition completed successfully!');
    } catch (error) {
      console.error('Error recognizing faces:', error);
      const errorMessage = error.response?.data?.message || 'Failed to recognize faces';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setSelectedFile(null);
    setRecognitionResult(null);
    setSelectedFace(null);
    setImageViewMode('original');
  };

  const downloadResults = () => {
    if (!recognitionResult) return;

    const dataStr = JSON.stringify(recognitionResult, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `face_recognition_${new Date().toISOString().slice(0, 19)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return '#10b981'; // Green
    if (confidence >= 60) return '#f59e0b'; // Yellow
    if (confidence >= 40) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 80) return 'High';
    if (confidence >= 60) return 'Medium';
    if (confidence >= 40) return 'Low';
    return 'Very Low';
  };

  const handleFaceClick = (face, index) => {
    setSelectedFace({ ...face, index });
  };

  return (
    <div className="face-recognition">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Face Recognition</h1>
          <p className="card-description">
            Upload an image to detect and identify faces using the trained recognition system
          </p>
        </div>

        {/* Upload Section */}
        <div className="upload-section">
          {!selectedFile ? (
            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
              <input {...getInputProps()} />
              <div className="dropzone-content">
                <Camera className="dropzone-icon" />
                <p className="dropzone-text">
                  {isDragActive ? 'Drop the image here' : 'Drag & drop an image here'}
                </p>
                <p className="dropzone-subtext">
                  or click to select a file (max 16MB)
                </p>
                <p className="dropzone-subtext">
                  Supports: JPG, PNG, GIF, BMP
                </p>
              </div>
            </div>
          ) : (
            <div className="selected-image">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3>Selected Image</h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    onClick={handleRecognize}
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="loading-spinner"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Eye size={16} />
                        Recognize Faces
                      </>
                    )}
                  </button>
                  <button 
                    onClick={clearResults}
                    className="btn btn-secondary"
                    disabled={loading}
                  >
                    Clear
                  </button>
                </div>
              </div>

              <div className="image-preview">
                <img 
                  src={URL.createObjectURL(selectedFile)} 
                  alt="Selected" 
                  style={{ maxWidth: '100%', maxHeight: '400px', borderRadius: '8px' }}
                />
                <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#718096' }}>
                  <p><strong>File:</strong> {selectedFile.name}</p>
                  <p><strong>Size:</strong> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  <p><strong>Type:</strong> {selectedFile.type}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recognition Results */}
        {recognitionResult && (
          <div className="recognition-results">
            <div className="result-header" style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              marginBottom: '2rem',
              padding: '1.5rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '12px',
              color: 'white'
            }}>
              <div>
                <h2 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>Recognition Results</h2>
                <p style={{ margin: 0, opacity: 0.9 }}>
                  Processing completed in {recognitionResult.processing_time?.toFixed(2)} seconds
                </p>
                {recognitionResult.image_dimensions && (
                  <p style={{ margin: '0.25rem 0 0 0', opacity: 0.8, fontSize: '0.875rem' }}>
                    Image: {recognitionResult.image_dimensions} • Model: {recognitionResult.detection_model || 'hog'}
                  </p>
                )}
              </div>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div className="result-stats" style={{ display: 'flex', gap: '1.5rem' }}>
                  <div className="result-stat" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', lineHeight: 1 }}>
                      {recognitionResult.total_faces_detected}
                    </div>
                    <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>Faces Detected</div>
                  </div>
                  <div className="result-stat" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', lineHeight: 1, color: '#10b981' }}>
                      {recognitionResult.total_faces_recognized}
                    </div>
                    <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>Recognized</div>
                  </div>
                  <div className="result-stat" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', lineHeight: 1, color: '#f59e0b' }}>
                      {recognitionResult.total_faces_detected - recognitionResult.total_faces_recognized}
                    </div>
                    <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>Unknown</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => setShowExportModal(true)}
                    className="btn btn-secondary"
                    style={{ color: '#4a5568' }}
                    title="Export Results"
                  >
                    <Share size={16} />
                  </button>
                  <button
                    onClick={downloadResults}
                    className="btn btn-secondary"
                    style={{ color: '#4a5568' }}
                    title="Download JSON"
                  >
                    <Download size={16} />
                  </button>
                  <button
                    onClick={clearResults}
                    className="btn btn-secondary"
                    style={{ color: '#4a5568' }}
                    title="Clear Results"
                  >
                    <RotateCcw size={16} />
                  </button>
                </div>
              </div>
            </div>

            {/* Image View Mode Toggle */}
            {recognitionResult.annotated_image_path && (
              <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                <div style={{ display: 'inline-flex', background: '#f7fafc', padding: '0.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <button
                    onClick={() => setImageViewMode('original')}
                    className={`btn ${imageViewMode === 'original' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ marginRight: '0.25rem', padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                  >
                    <Eye size={14} style={{ marginRight: '0.25rem' }} />
                    Original
                  </button>
                  <button
                    onClick={() => setImageViewMode('annotated')}
                    className={`btn ${imageViewMode === 'annotated' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ marginRight: '0.25rem', padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                  >
                    <Target size={14} style={{ marginRight: '0.25rem' }} />
                    Annotated
                  </button>
                  <button
                    onClick={() => setImageViewMode('split')}
                    className={`btn ${imageViewMode === 'split' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                  >
                    <ZoomIn size={14} style={{ marginRight: '0.25rem' }} />
                    Split View
                  </button>
                </div>
              </div>
            )}

            {/* Result Image */}
            <div className="result-image" style={{ marginBottom: '2rem' }}>
              {imageViewMode === 'split' && recognitionResult.annotated_image_path ? (
                <div className="grid grid-2" style={{ gap: '1rem' }}>
                  <div style={{ textAlign: 'center' }}>
                    <img
                      src={URL.createObjectURL(selectedFile)}
                      alt="Original"
                      style={{
                        width: '100%',
                        maxHeight: '400px',
                        objectFit: 'contain',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#718096', fontWeight: '600' }}>
                      Original Image
                    </p>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <img
                      src={apiService.images.getTestImageUrl(recognitionResult.annotated_image_path.split('/').pop())}
                      alt="Annotated Result"
                      style={{
                        width: '100%',
                        maxHeight: '400px',
                        objectFit: 'contain',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#718096', fontWeight: '600' }}>
                      Annotated Result
                    </p>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center' }}>
                  <img
                    src={imageViewMode === 'original'
                      ? URL.createObjectURL(selectedFile)
                      : apiService.images.getTestImageUrl(recognitionResult.annotated_image_path.split('/').pop())
                    }
                    alt={imageViewMode === 'original' ? "Original" : "Annotated Result"}
                    style={{
                      maxWidth: '100%',
                      maxHeight: '500px',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                      cursor: selectedFace ? 'pointer' : 'default'
                    }}
                    onClick={() => setSelectedFace(null)}
                  />
                  <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#718096' }}>
                    {imageViewMode === 'original'
                      ? 'Original uploaded image'
                      : 'Processed image with face detection boxes and labels'
                    }
                  </p>
                </div>
              )}
            </div>

            {/* Recognized Faces List */}
            <div className="recognized-faces">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ margin: 0, color: '#2d3748' }}>
                  Detected Faces ({recognitionResult.recognized_faces.length})
                </h3>
                {selectedFace && (
                  <button
                    onClick={() => setSelectedFace(null)}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.875rem' }}
                  >
                    Clear Selection
                  </button>
                )}
              </div>

              {recognitionResult.recognized_faces.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '3rem',
                  background: '#f7fafc',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0'
                }}>
                  <Users size={64} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
                  <h4 style={{ color: '#4a5568', marginBottom: '0.5rem' }}>No faces detected</h4>
                  <p style={{ color: '#718096' }}>Try uploading an image with clear, well-lit faces</p>
                </div>
              ) : (
                <div className="recognized-faces-grid" style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                  gap: '1.5rem'
                }}>
                  {recognitionResult.recognized_faces.map((face, index) => (
                    <div
                      key={index}
                      className={`recognized-face-card ${face.name === 'Unknown' ? 'unknown' : 'known'} ${selectedFace?.index === index ? 'selected' : ''}`}
                      onClick={() => handleFaceClick(face, index)}
                      style={{
                        padding: '1.5rem',
                        borderRadius: '12px',
                        border: selectedFace?.index === index ? '2px solid #667eea' : '1px solid #e2e8f0',
                        background: selectedFace?.index === index ? '#f0f4ff' :
                                   face.name === 'Unknown' ? '#fef2f2' : '#f0fff4',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: selectedFace?.index === index ? '0 8px 25px rgba(102, 126, 234, 0.15)' : '0 2px 4px rgba(0, 0, 0, 0.1)'
                      }}
                    >
                      {/* Face Header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%',
                            background: face.name === 'Unknown' ? '#fee2e2' : '#dcfce7',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            {face.name === 'Unknown' ? (
                              <XCircle size={20} color="#dc2626" />
                            ) : (
                              <CheckCircle size={20} color="#16a34a" />
                            )}
                          </div>
                          <div>
                            <h4 style={{ margin: 0, color: '#1f2937', fontSize: '1.125rem', fontWeight: '600' }}>
                              {face.name}
                            </h4>
                            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#6b7280' }}>
                              Face #{index + 1}
                            </p>
                          </div>
                        </div>
                        {face.name !== 'Unknown' && (
                          <div style={{ textAlign: 'right' }}>
                            <div style={{
                              padding: '0.25rem 0.75rem',
                              borderRadius: '20px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              background: getConfidenceColor(face.confidence),
                              color: 'white'
                            }}>
                              {face.confidence?.toFixed(1)}%
                            </div>
                            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: '#6b7280' }}>
                              {getConfidenceBadge(face.confidence)}
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Face Details */}
                      {face.name !== 'Unknown' && (
                        <div className="face-details" style={{ marginBottom: '1rem' }}>
                          <div className="grid grid-2" style={{ gap: '0.75rem' }}>
                            {face.employee_id && face.employee_id !== 'N/A' && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Badge size={14} color="#6b7280" />
                                <div>
                                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#6b7280' }}>Employee ID</p>
                                  <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                                    {face.employee_id}
                                  </p>
                                </div>
                              </div>
                            )}
                            {face.department && face.department !== 'N/A' && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Building size={14} color="#6b7280" />
                                <div>
                                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#6b7280' }}>Department</p>
                                  <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                                    {face.department}
                                  </p>
                                </div>
                              </div>
                            )}
                            {face.position && face.position !== 'N/A' && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <User size={14} color="#6b7280" />
                                <div>
                                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#6b7280' }}>Position</p>
                                  <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                                    {face.position}
                                  </p>
                                </div>
                              </div>
                            )}
                            {face.email && face.email !== 'N/A' && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Mail size={14} color="#6b7280" />
                                <div>
                                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#6b7280' }}>Email</p>
                                  <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                                    {face.email}
                                  </p>
                                </div>
                              </div>
                            )}
                            {face.phone && face.phone !== 'N/A' && (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Phone size={14} color="#6b7280" />
                                <div>
                                  <p style={{ margin: 0, fontSize: '0.75rem', color: '#6b7280' }}>Phone</p>
                                  <p style={{ margin: 0, fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                                    {face.phone}
                                  </p>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Face Location and Technical Details */}
                      {face.face_location && (
                        <div style={{
                          padding: '0.75rem',
                          background: selectedFace?.index === index ? '#e0e7ff' : '#f9fafb',
                          borderRadius: '8px',
                          fontSize: '0.75rem',
                          color: '#6b7280',
                          border: '1px solid #e5e7eb'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                            <span style={{ fontWeight: '600', color: '#374151' }}>Detection Details</span>
                            {face.face_distance !== undefined && (
                              <span style={{
                                padding: '0.125rem 0.5rem',
                                background: '#ffffff',
                                borderRadius: '4px',
                                fontSize: '0.625rem',
                                fontWeight: '500'
                              }}>
                                Distance: {face.face_distance}
                              </span>
                            )}
                          </div>
                          <div className="grid grid-2" style={{ gap: '0.5rem' }}>
                            <div>
                              <strong>Position:</strong> ({face.face_location[3]}, {face.face_location[0]})
                            </div>
                            <div>
                              <strong>Size:</strong> {face.face_location[1] - face.face_location[3]} × {face.face_location[2] - face.face_location[0]}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Export Modal */}
        <ExportModal
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          data={recognitionResult}
          type="results"
        />
      </div>
    </div>
  );
};

export default FaceRecognition;
