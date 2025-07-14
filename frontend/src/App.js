import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, Users, Camera, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);
  const [knownFaces, setKnownFaces] = useState([]);
  const [tolerance, setTolerance] = useState(0.5);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadKnownFaces();
  }, []);

  const loadKnownFaces = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/known-faces`);
      setKnownFaces(response.data);
    } catch (error) {
      showMessage('Error loading known faces', 'error');
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      showMessage('Please select an image first', 'error');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('tolerance', tolerance);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResults(response.data);
        showMessage('Image processed successfully!', 'success');
      } else {
        showMessage(response.data.error || 'Error processing image', 'error');
      }
    } catch (error) {
      showMessage('Network error: ' + error.message, 'error');
    } finally {
      setUploading(false);
    }
  };

  const refreshEncodings = async () => {
    try {
      await axios.post(`${API_BASE_URL}/refresh-encodings`);
      showMessage('Face database refreshed successfully!', 'success');
      loadKnownFaces();
    } catch (error) {
      showMessage('Error refreshing database', 'error');
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>
          <Camera className="icon" />
          Face Recognition Web App
        </h1>
        <p>Upload a group photo to identify people using AI</p>
      </header>

      {message && (
        <div className={`message ${message.type}`}>
          {message.type === 'success' ? (
            <CheckCircle className="message-icon" />
          ) : (
            <AlertCircle className="message-icon" />
          )}
          {message.text}
        </div>
      )}

      <div className="main-content">
        <div className="upload-section">
          <div className="card">
            <h2>
              <Upload className="icon" />
              Upload Group Photo
            </h2>
            
            <div className="upload-area">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input"
                id="fileInput"
              />
              <label htmlFor="fileInput" className="upload-label">
                <Upload className="upload-icon" />
                <p>
                  {selectedFile ? selectedFile.name : 'Click to select or drag and drop your image'}
                </p>
              </label>
            </div>

            <div className="tolerance-control">
              <label>Recognition Tolerance: {tolerance}</label>
              <input
                type="range"
                min="0.3"
                max="1.0"
                step="0.1"
                value={tolerance}
                onChange={(e) => setTolerance(parseFloat(e.target.value))}
                className="tolerance-slider"
              />
              <small>Lower = More Strict</small>
            </div>

            <div className="buttons">
              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                className="btn btn-primary"
              >
                {uploading ? 'Processing...' : 'Process Image'}
              </button>
              <button onClick={refreshEncodings} className="btn btn-secondary">
                <RefreshCw className="icon" />
                Refresh Database
              </button>
            </div>
          </div>
        </div>

        <div className="known-faces-section">
          <div className="card">
            <h2>
              <Users className="icon" />
              Known Faces Database
            </h2>
            
            {knownFaces.total_faces > 0 ? (
              <div>
                <div className="stats">
                  <div className="stat">
                    <span className="stat-value">{knownFaces.total_faces}</span>
                    <span className="stat-label">Known Faces</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{knownFaces.encodings_cached ? '✅' : '❌'}</span>
                    <span className="stat-label">Cached</span>
                  </div>
                </div>
                
                <div className="faces-grid">
                  {knownFaces.faces?.map((face, index) => (
                    <div key={index} className="face-card">
                      <h4>{face.name}</h4>
                      {face.metadata ? (
                        <div className="face-metadata">
                          <p><strong>Role:</strong> {face.metadata.role}</p>
                          <p><strong>Department:</strong> {face.metadata.department}</p>
                        </div>
                      ) : (
                        <p>No metadata available</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <p>No known faces found. Please add images to the 'known_faces' directory.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {results && (
        <div className="results-section">
          <div className="card">
            <h2>Recognition Results</h2>
            
            <div className="results-stats">
              <div className="stat">
                <span className="stat-value">{results.statistics.total_faces_detected}</span>
                <span className="stat-label">Total Faces</span>
              </div>
              <div className="stat">
                <span className="stat-value">{results.statistics.known_faces}</span>
                <span className="stat-label">Known Faces</span>
              </div>
              <div className="stat">
                <span className="stat-value">{results.statistics.unknown_faces}</span>
                <span className="stat-label">Unknown Faces</span>
              </div>
            </div>

            <div className="people-results">
              {results.recognized_people.map((person, index) => (
                <div key={index} className={`person-card ${person.status === 'unknown' ? 'unknown' : ''}`}>
                  <h3>{person.name}</h3>
                  {person.status === 'unknown' ? (
                    <p>⚠️ Unknown person</p>
                  ) : (
                    <div className="person-details">
                      <p><strong>Role:</strong> {person.role}</p>
                      <p><strong>Department:</strong> {person.department}</p>
                      <p><strong>Email:</strong> {person.email}</p>
                      <p><strong>Employee ID:</strong> {person.employee_id}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {results.annotated_image_url && (
              <div className="annotated-image-section">
                <h3>Annotated Image</h3>
                <img
                  src={`http://localhost:5000${results.annotated_image_url}`}
                  alt="Annotated group photo"
                  className="annotated-image"
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
