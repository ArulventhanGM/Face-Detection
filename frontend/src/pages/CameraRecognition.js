import React, { useState, useRef, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { 
  Camera, 
  Square, 
  Play, 
  Pause, 
  Download,
  Users,
  Eye,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const CameraRecognition = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [streamStats, setStreamStats] = useState({
    framesProcessed: 0,
    avgProcessingTime: 0,
    lastProcessingTime: 0
  });
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [realTimeResults, setRealTimeResults] = useState([]);

  // Camera constraints
  const constraints = {
    video: {
      width: { ideal: 1280 },
      height: { ideal: 720 },
      facingMode: 'user'
    }
  };

  // Start camera stream
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
      setIsStreaming(true);
      toast.success('Camera started successfully');
    } catch (error) {
      console.error('Error accessing camera:', error);
      toast.error('Failed to access camera. Please check permissions.');
    }
  };

  // Stop camera stream
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setIsStreaming(false);
    setRealTimeMode(false);
    toast.success('Camera stopped');
  };

  // Capture single frame
  const captureFrame = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageData);

    return imageData;
  }, []);

  // Process captured image
  const processCapturedImage = async () => {
    if (!capturedImage) {
      toast.error('No image captured');
      return;
    }

    setIsProcessing(true);
    setRecognitionResult(null);

    try {
      const response = await apiService.camera.captureImage({ image: capturedImage });
      setRecognitionResult(response.data.data);
      toast.success('Image processed successfully!');
    } catch (error) {
      console.error('Error processing image:', error);
      const errorMessage = error.response?.data?.message || 'Failed to process image';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  // Capture and process in one step
  const captureAndProcess = async () => {
    try {
      const imageData = await captureFrame();
      if (!imageData) return;

      setIsProcessing(true);
      const response = await apiService.camera.captureImage({ image: imageData });
      setRecognitionResult(response.data.data);
      toast.success('Face recognition completed!');
    } catch (error) {
      console.error('Error in capture and process:', error);
      const errorMessage = error.response?.data?.message || 'Failed to process image';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  // Real-time processing
  const processRealTimeFrame = useCallback(async () => {
    if (!realTimeMode || !videoRef.current || !canvasRef.current || isProcessing) return;

    try {
      const imageData = await captureFrame();
      if (!imageData) return;

      setIsProcessing(true);
      const startTime = Date.now();
      
      const response = await apiService.camera.processStreamFrame({ frame: imageData });
      const processingTime = Date.now() - startTime;
      
      const result = response.data.data;
      
      // Update stream stats
      setStreamStats(prev => ({
        framesProcessed: prev.framesProcessed + 1,
        lastProcessingTime: processingTime,
        avgProcessingTime: (prev.avgProcessingTime * prev.framesProcessed + processingTime) / (prev.framesProcessed + 1)
      }));

      // Update real-time results (keep last 10 results)
      setRealTimeResults(prev => {
        const newResults = [{ ...result, timestamp: new Date() }, ...prev];
        return newResults.slice(0, 10);
      });

    } catch (error) {
      console.error('Error in real-time processing:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [realTimeMode, isProcessing, captureFrame]);

  // Real-time processing interval
  useEffect(() => {
    let interval;
    if (realTimeMode && isStreaming) {
      interval = setInterval(processRealTimeFrame, 2000); // Process every 2 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [realTimeMode, isStreaming, processRealTimeFrame]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const downloadResult = () => {
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

  return (
    <div className="camera-recognition">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Camera Face Recognition</h1>
          <p className="card-description">
            Use your camera for real-time face detection and recognition
          </p>
        </div>

        {/* Camera Controls */}
        <div className="camera-controls" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
            {!isStreaming ? (
              <button onClick={startCamera} className="btn btn-primary">
                <Camera size={16} />
                Start Camera
              </button>
            ) : (
              <button onClick={stopCamera} className="btn btn-secondary">
                <Square size={16} />
                Stop Camera
              </button>
            )}

            {isStreaming && (
              <>
                <button 
                  onClick={captureAndProcess} 
                  className="btn btn-primary"
                  disabled={isProcessing}
                >
                  <Eye size={16} />
                  {isProcessing ? 'Processing...' : 'Capture & Recognize'}
                </button>

                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="checkbox"
                    checked={realTimeMode}
                    onChange={(e) => setRealTimeMode(e.target.checked)}
                    disabled={isProcessing}
                  />
                  Real-time Mode
                </label>
              </>
            )}

            {recognitionResult && (
              <button onClick={downloadResult} className="btn btn-secondary">
                <Download size={16} />
                Download Results
              </button>
            )}
          </div>
        </div>

        {/* Camera Feed and Results */}
        <div className="grid grid-2" style={{ gap: '2rem' }}>
          {/* Camera Feed */}
          <div className="camera-feed">
            <h3 style={{ marginBottom: '1rem' }}>Camera Feed</h3>
            <div style={{ 
              position: 'relative', 
              background: '#000', 
              borderRadius: '8px', 
              overflow: 'hidden',
              aspectRatio: '16/9'
            }}>
              <video
                ref={videoRef}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
                muted
                playsInline
              />
              
              {/* Status Overlay */}
              <div style={{
                position: 'absolute',
                top: '10px',
                left: '10px',
                background: 'rgba(0,0,0,0.7)',
                color: 'white',
                padding: '0.5rem',
                borderRadius: '4px',
                fontSize: '0.875rem'
              }}>
                {isStreaming ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <CheckCircle size={16} color="#10b981" />
                    Live
                    {realTimeMode && (
                      <span style={{ color: '#f59e0b' }}>• Real-time</span>
                    )}
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={16} color="#ef4444" />
                    Camera Off
                  </div>
                )}
              </div>

              {/* Processing Indicator */}
              {isProcessing && (
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  background: 'rgba(0,0,0,0.8)',
                  color: 'white',
                  padding: '1rem',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div className="loading-spinner" style={{ marginBottom: '0.5rem' }}></div>
                  Processing...
                </div>
              )}
            </div>

            {/* Hidden canvas for image capture */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            {/* Stream Statistics */}
            {realTimeMode && streamStats.framesProcessed > 0 && (
              <div style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                background: '#f7fafc', 
                borderRadius: '8px',
                border: '1px solid #e2e8f0'
              }}>
                <h4 style={{ marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '600' }}>
                  Stream Statistics
                </h4>
                <div className="grid grid-3" style={{ gap: '1rem', fontSize: '0.875rem' }}>
                  <div>
                    <strong>Frames:</strong> {streamStats.framesProcessed}
                  </div>
                  <div>
                    <strong>Last:</strong> {streamStats.lastProcessingTime}ms
                  </div>
                  <div>
                    <strong>Avg:</strong> {Math.round(streamStats.avgProcessingTime)}ms
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="results-panel">
            <h3 style={{ marginBottom: '1rem' }}>Recognition Results</h3>
            
            {realTimeMode ? (
              // Real-time results
              <div>
                {realTimeResults.length === 0 ? (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '2rem',
                    background: '#f7fafc',
                    borderRadius: '8px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <Clock size={32} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
                    <p style={{ color: '#718096' }}>Waiting for real-time results...</p>
                  </div>
                ) : (
                  <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                    {realTimeResults.map((result, index) => (
                      <div key={index} style={{
                        marginBottom: '1rem',
                        padding: '1rem',
                        background: index === 0 ? '#e6fffa' : '#f7fafc',
                        borderRadius: '8px',
                        border: `1px solid ${index === 0 ? '#38b2ac' : '#e2e8f0'}`
                      }}>
                        <div style={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          marginBottom: '0.5rem'
                        }}>
                          <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>
                            {result.timestamp.toLocaleTimeString()}
                          </span>
                          <span style={{ fontSize: '0.75rem', color: '#718096' }}>
                            {result.processing_time?.toFixed(2)}s
                          </span>
                        </div>
                        <div style={{ fontSize: '0.875rem' }}>
                          <strong>Faces:</strong> {result.total_faces_detected} detected, {result.total_faces_recognized} recognized
                        </div>
                        {result.recognized_faces?.length > 0 && (
                          <div style={{ marginTop: '0.5rem' }}>
                            {result.recognized_faces.map((face, faceIndex) => (
                              <div key={faceIndex} style={{
                                fontSize: '0.75rem',
                                color: face.name === 'Unknown' ? '#e53e3e' : '#38a169',
                                marginLeft: '1rem'
                              }}>
                                • {face.name} {face.confidence > 0 && `(${face.confidence.toFixed(1)}%)`}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              // Single capture results
              recognitionResult ? (
                <div>
                  {/* Results Summary */}
                  <div className="stats-grid" style={{ marginBottom: '2rem' }}>
                    <div className="stat-card">
                      <div className="stat-value">
                        <Users size={20} style={{ marginBottom: '0.5rem', color: '#667eea' }} />
                        {recognitionResult.total_faces_detected}
                      </div>
                      <div className="stat-label">Faces Detected</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">
                        <CheckCircle size={20} style={{ marginBottom: '0.5rem', color: '#10b981' }} />
                        {recognitionResult.total_faces_recognized}
                      </div>
                      <div className="stat-label">Recognized</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value">
                        <Clock size={20} style={{ marginBottom: '0.5rem', color: '#f59e0b' }} />
                        {recognitionResult.processing_time?.toFixed(2)}s
                      </div>
                      <div className="stat-label">Processing Time</div>
                    </div>
                  </div>

                  {/* Recognized Faces */}
                  {recognitionResult.recognized_faces?.length > 0 && (
                    <div>
                      <h4 style={{ marginBottom: '1rem' }}>Recognized Faces</h4>
                      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        {recognitionResult.recognized_faces.map((face, index) => (
                          <div key={index} className="face-result-card" style={{
                            padding: '1rem',
                            marginBottom: '1rem',
                            background: face.name === 'Unknown' ? '#fed7d7' : '#c6f6d5',
                            borderRadius: '8px',
                            border: `1px solid ${face.name === 'Unknown' ? '#e53e3e' : '#38a169'}`
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div>
                                <h5 style={{ margin: 0, color: face.name === 'Unknown' ? '#e53e3e' : '#1a202c' }}>
                                  {face.name}
                                </h5>
                                {face.name !== 'Unknown' && (
                                  <div style={{ fontSize: '0.875rem', color: '#4a5568', marginTop: '0.25rem' }}>
                                    {face.employee_id && face.employee_id !== 'N/A' && (
                                      <div>ID: {face.employee_id}</div>
                                    )}
                                    {face.department && face.department !== 'N/A' && (
                                      <div>Dept: {face.department}</div>
                                    )}
                                  </div>
                                )}
                              </div>
                              <div style={{ textAlign: 'right' }}>
                                <div style={{ 
                                  fontSize: '1.25rem', 
                                  fontWeight: 'bold',
                                  color: face.name === 'Unknown' ? '#e53e3e' : '#38a169'
                                }}>
                                  {face.confidence?.toFixed(1)}%
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#718096' }}>
                                  Face #{index + 1}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '3rem',
                  background: '#f7fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <Camera size={48} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
                  <h3 style={{ color: '#4a5568', marginBottom: '0.5rem' }}>No results yet</h3>
                  <p style={{ color: '#718096' }}>Capture an image to see face recognition results</p>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CameraRecognition;
