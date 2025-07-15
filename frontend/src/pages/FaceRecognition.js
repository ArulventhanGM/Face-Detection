import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
import { 
  Upload, 
  Camera, 
  Users, 
  Clock,
  CheckCircle,
  XCircle,
  Eye
} from 'lucide-react';
import toast from 'react-hot-toast';

const FaceRecognition = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showOriginal, setShowOriginal] = useState(true);

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

  const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
  };

  const getConfidenceText = (confidence) => {
    const level = getConfidenceLevel(confidence);
    const percentage = (confidence * 100).toFixed(1);
    return `${percentage}% ${level.toUpperCase()}`;
  };

  const clearResults = () => {
    setSelectedFile(null);
    setRecognitionResult(null);
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
            <div className="result-header">
              <div>
                <h2>Recognition Results</h2>
                <p>Processing completed in {recognitionResult.processing_time?.toFixed(2)} seconds</p>
              </div>
              <div className="result-stats">
                <div className="result-stat">
                  <div className="result-stat-value">{recognitionResult.total_faces_detected}</div>
                  <div className="result-stat-label">Faces Detected</div>
                </div>
                <div className="result-stat">
                  <div className="result-stat-value">{recognitionResult.total_faces_recognized}</div>
                  <div className="result-stat-label">Faces Recognized</div>
                </div>
                <div className="result-stat">
                  <div className="result-stat-value">
                    {recognitionResult.total_faces_detected - recognitionResult.total_faces_recognized}
                  </div>
                  <div className="result-stat-label">Unknown Faces</div>
                </div>
              </div>
            </div>

            {/* Image Toggle */}
            {recognitionResult.annotated_image_path && (
              <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                <div style={{ display: 'inline-flex', background: '#f7fafc', padding: '0.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <button 
                    onClick={() => setShowOriginal(true)}
                    className={`btn ${showOriginal ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ marginRight: '0.25rem' }}
                  >
                    Original Image
                  </button>
                  <button 
                    onClick={() => setShowOriginal(false)}
                    className={`btn ${!showOriginal ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    Annotated Result
                  </button>
                </div>
              </div>
            )}

            {/* Result Image */}
            <div className="result-image" style={{ textAlign: 'center', marginBottom: '2rem' }}>
              <img 
                src={showOriginal 
                  ? URL.createObjectURL(selectedFile)
                  : apiService.images.getTestImageUrl(recognitionResult.annotated_image_path.split('/').pop())
                }
                alt={showOriginal ? "Original" : "Annotated Result"}
                style={{ 
                  maxWidth: '100%', 
                  maxHeight: '500px', 
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                }}
              />
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#718096' }}>
                {showOriginal ? 'Original uploaded image' : 'Processed image with face detection boxes'}
              </p>
            </div>

            {/* Recognized Faces List */}
            <div className="recognized-faces">
              <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>
                Detected Faces ({recognitionResult.recognized_faces.length})
              </h3>

              {recognitionResult.recognized_faces.length === 0 ? (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '2rem',
                  background: '#f7fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <Users size={48} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
                  <p style={{ color: '#718096' }}>No faces detected in the image</p>
                </div>
              ) : (
                <div className="recognized-faces-grid">
                  {recognitionResult.recognized_faces.map((face, index) => (
                    <div 
                      key={index} 
                      className={`recognized-face-card ${face.name === 'Unknown' ? 'unknown' : ''}`}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {face.name === 'Unknown' ? (
                            <XCircle size={20} color="#e53e3e" />
                          ) : (
                            <CheckCircle size={20} color="#38a169" />
                          )}
                          <h4 style={{ margin: 0, color: '#2d3748' }}>{face.name}</h4>
                        </div>
                        {face.name !== 'Unknown' && (
                          <span className={`confidence-badge confidence-${getConfidenceLevel(face.confidence)}`}>
                            {getConfidenceText(face.confidence)}
                          </span>
                        )}
                      </div>

                      <div className="face-details">
                        {face.employee_id && face.employee_id !== 'N/A' && (
                          <p className="face-detail">
                            <strong>Employee ID:</strong> {face.employee_id}
                          </p>
                        )}
                        {face.department && face.department !== 'N/A' && (
                          <p className="face-detail">
                            <strong>Department:</strong> {face.department}
                          </p>
                        )}
                        {face.position && face.position !== 'N/A' && (
                          <p className="face-detail">
                            <strong>Position:</strong> {face.position}
                          </p>
                        )}
                        {face.email && face.email !== 'N/A' && (
                          <p className="face-detail">
                            <strong>Email:</strong> {face.email}
                          </p>
                        )}
                        {face.phone && face.phone !== 'N/A' && (
                          <p className="face-detail">
                            <strong>Phone:</strong> {face.phone}
                          </p>
                        )}
                      </div>

                      {face.face_location && (
                        <div style={{ 
                          marginTop: '1rem', 
                          padding: '0.75rem', 
                          background: '#f7fafc', 
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                          color: '#718096'
                        }}>
                          <strong>Face Location:</strong> Top: {face.face_location[0]}, 
                          Right: {face.face_location[1]}, 
                          Bottom: {face.face_location[2]}, 
                          Left: {face.face_location[3]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceRecognition;
