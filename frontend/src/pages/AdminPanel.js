import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
import ExportModal from '../components/ExportModal';
import {
  Upload,
  Users,
  Trash2,
  Plus,
  User,
  Mail,
  Phone,
  Building,
  Badge,
  RefreshCw,
  FileText,
  Download,
  CheckCircle,
  AlertCircle,
  X,
  Share
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminPanel = () => {
  const [knownFaces, setKnownFaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [bulkFiles, setBulkFiles] = useState([]);
  const [bulkUploadProgress, setBulkUploadProgress] = useState({});
  const [showExportModal, setShowExportModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    employee_id: '',
    department: '',
    position: '',
    email: '',
    phone: ''
  });

  useEffect(() => {
    loadKnownFaces();
  }, []);

  const loadKnownFaces = async () => {
    setLoading(true);
    try {
      const response = await apiService.admin.getKnownFaces();
      setKnownFaces(response.data.data);
    } catch (error) {
      console.error('Error loading known faces:', error);
      toast.error('Failed to load known faces');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setShowAddForm(true);
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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      toast.error('Please select an image file');
      return;
    }

    if (!formData.name.trim()) {
      toast.error('Name is required');
      return;
    }

    setUploading(true);
    
    try {
      const uploadData = new FormData();
      uploadData.append('image', selectedFile);
      uploadData.append('name', formData.name.trim());
      uploadData.append('employee_id', formData.employee_id.trim());
      uploadData.append('department', formData.department.trim());
      uploadData.append('position', formData.position.trim());
      uploadData.append('email', formData.email.trim());
      uploadData.append('phone', formData.phone.trim());

      const response = await apiService.admin.uploadFace(uploadData);
      
      toast.success(response.data.message);
      
      // Reset form
      setSelectedFile(null);
      setFormData({
        name: '',
        employee_id: '',
        department: '',
        position: '',
        email: '',
        phone: ''
      });
      setShowAddForm(false);
      
      // Reload faces
      loadKnownFaces();
      
    } catch (error) {
      console.error('Error uploading face:', error);
      const errorMessage = error.response?.data?.message || 'Failed to upload face';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (faceId, faceName) => {
    if (!window.confirm(`Are you sure you want to delete ${faceName}?`)) {
      return;
    }

    try {
      const response = await apiService.admin.deleteFace(faceId);
      toast.success(response.data.message);
      loadKnownFaces();
    } catch (error) {
      console.error('Error deleting face:', error);
      const errorMessage = error.response?.data?.message || 'Failed to delete face';
      toast.error(errorMessage);
    }
  };

  const cancelAdd = () => {
    setSelectedFile(null);
    setFormData({
      name: '',
      employee_id: '',
      department: '',
      position: '',
      email: '',
      phone: ''
    });
    setShowAddForm(false);
  };

  // Bulk upload functionality
  const onBulkDrop = useCallback((acceptedFiles) => {
    const imageFiles = acceptedFiles.filter(file =>
      file.type.startsWith('image/') && file.size <= 10 * 1024 * 1024 // 10MB limit
    );

    if (imageFiles.length !== acceptedFiles.length) {
      toast.error(`${acceptedFiles.length - imageFiles.length} files were rejected (not images or too large)`);
    }

    setBulkFiles(prev => [...prev, ...imageFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      name: file.name.split('.')[0].replace(/[^a-zA-Z0-9\s]/g, '').trim(),
      employee_id: '',
      department: '',
      position: '',
      email: '',
      phone: '',
      status: 'pending', // pending, uploading, success, error
      error: null
    }))]);
  }, []);

  const { getRootProps: getBulkRootProps, getInputProps: getBulkInputProps, isDragActive: isBulkDragActive } = useDropzone({
    onDrop: onBulkDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const updateBulkFileData = (fileId, field, value) => {
    setBulkFiles(prev => prev.map(file =>
      file.id === fileId ? { ...file, [field]: value } : file
    ));
  };

  const removeBulkFile = (fileId) => {
    setBulkFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const processBulkUpload = async () => {
    if (bulkFiles.length === 0) {
      toast.error('No files to upload');
      return;
    }

    // Validate all files have required data
    const invalidFiles = bulkFiles.filter(file => !file.name.trim());
    if (invalidFiles.length > 0) {
      toast.error('All files must have a name');
      return;
    }

    setUploading(true);
    let successCount = 0;
    let errorCount = 0;

    // Process files one by one to avoid overwhelming the server
    for (const fileData of bulkFiles) {
      if (fileData.status !== 'pending') continue;

      try {
        // Update status to uploading
        setBulkFiles(prev => prev.map(f =>
          f.id === fileData.id ? { ...f, status: 'uploading' } : f
        ));

        const uploadData = new FormData();
        uploadData.append('image', fileData.file);
        uploadData.append('name', fileData.name.trim());
        uploadData.append('employee_id', fileData.employee_id.trim());
        uploadData.append('department', fileData.department.trim());
        uploadData.append('position', fileData.position.trim());
        uploadData.append('email', fileData.email.trim());
        uploadData.append('phone', fileData.phone.trim());

        await apiService.admin.uploadFace(uploadData);

        // Update status to success
        setBulkFiles(prev => prev.map(f =>
          f.id === fileData.id ? { ...f, status: 'success' } : f
        ));

        successCount++;

        // Small delay to prevent overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 500));

      } catch (error) {
        console.error(`Error uploading ${fileData.name}:`, error);
        const errorMessage = error.response?.data?.message || 'Upload failed';

        // Update status to error
        setBulkFiles(prev => prev.map(f =>
          f.id === fileData.id ? { ...f, status: 'error', error: errorMessage } : f
        ));

        errorCount++;
      }
    }

    setUploading(false);

    if (successCount > 0) {
      toast.success(`Successfully uploaded ${successCount} face(s)`);
      loadKnownFaces(); // Refresh the faces list
    }

    if (errorCount > 0) {
      toast.error(`Failed to upload ${errorCount} face(s)`);
    }
  };

  const clearBulkUpload = () => {
    setBulkFiles([]);
    setBulkUploadProgress({});
  };

  const downloadBulkTemplate = () => {
    const csvContent = "name,employee_id,department,position,email,phone\n" +
                      "John Doe,EMP001,Engineering,Software Engineer,john.doe@company.com,+1234567890\n" +
                      "Jane Smith,EMP002,Marketing,Marketing Manager,jane.smith@company.com,+1234567891";

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'bulk_upload_template.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="admin-panel">
      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 className="card-title">Admin Panel</h1>
              <p className="card-description">
                Manage known faces in the recognition system
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setShowExportModal(true)}
                className="btn btn-secondary"
                disabled={loading}
              >
                <Share size={16} />
                Export Database
              </button>
              <button
                onClick={loadKnownFaces}
                className="btn btn-secondary"
                disabled={loading}
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Upload Mode Toggle */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button
              onClick={() => {
                setShowAddForm(false);
                setShowBulkUpload(false);
                setSelectedFile(null);
                clearBulkUpload();
              }}
              className={`btn ${!showAddForm && !showBulkUpload ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Plus size={16} />
              Single Upload
            </button>
            <button
              onClick={() => {
                setShowAddForm(false);
                setShowBulkUpload(true);
                setSelectedFile(null);
              }}
              className={`btn ${showBulkUpload ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Upload size={16} />
              Bulk Upload
            </button>
            {showBulkUpload && (
              <button
                onClick={downloadBulkTemplate}
                className="btn btn-secondary"
                style={{ marginLeft: 'auto' }}
              >
                <Download size={16} />
                Download Template
              </button>
            )}
          </div>
        </div>

        {/* Upload Section */}
        {!showAddForm && !showBulkUpload ? (
          <div className="upload-section">
            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
              <input {...getInputProps()} />
              <div className="dropzone-content">
                <Upload className="dropzone-icon" />
                <p className="dropzone-text">
                  {isDragActive ? 'Drop the image here' : 'Drag & drop an image here'}
                </p>
                <p className="dropzone-subtext">
                  or click to select a file (max 16MB)
                </p>
                <button type="button" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                  <Plus size={16} />
                  Add New Face
                </button>
              </div>
            </div>
          </div>
        ) : showBulkUpload ? (
          <div className="bulk-upload-section">
            <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>Bulk Upload Faces</h3>

            {/* Bulk Upload Dropzone */}
            <div {...getBulkRootProps()} className={`dropzone ${isBulkDragActive ? 'active' : ''}`} style={{ marginBottom: '2rem' }}>
              <input {...getBulkInputProps()} />
              <div className="dropzone-content">
                <Upload className="dropzone-icon" />
                <p className="dropzone-text">
                  {isBulkDragActive ? 'Drop the images here' : 'Drag & drop multiple images here'}
                </p>
                <p className="dropzone-subtext">
                  or click to select files (max 10MB each)
                </p>
                <button type="button" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                  <Upload size={16} />
                  Select Multiple Images
                </button>
              </div>
            </div>

            {/* Bulk Files List */}
            {bulkFiles.length > 0 && (
              <div style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h4>Files to Upload ({bulkFiles.length})</h4>
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                      onClick={processBulkUpload}
                      className="btn btn-primary"
                      disabled={uploading || bulkFiles.every(f => f.status !== 'pending')}
                    >
                      {uploading ? 'Uploading...' : 'Upload All'}
                    </button>
                    <button
                      onClick={clearBulkUpload}
                      className="btn btn-secondary"
                      disabled={uploading}
                    >
                      Clear All
                    </button>
                  </div>
                </div>

                <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                  {bulkFiles.map((fileData) => (
                    <div key={fileData.id} style={{
                      padding: '1rem',
                      borderBottom: '1px solid #e2e8f0',
                      background: fileData.status === 'success' ? '#f0fff4' :
                                 fileData.status === 'error' ? '#fef2f2' :
                                 fileData.status === 'uploading' ? '#fefcbf' : '#ffffff'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {/* File Preview */}
                        <img
                          src={URL.createObjectURL(fileData.file)}
                          alt="Preview"
                          style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '4px' }}
                        />

                        {/* File Info and Form */}
                        <div style={{ flex: 1 }}>
                          <div className="grid grid-3" style={{ gap: '0.5rem', marginBottom: '0.5rem' }}>
                            <input
                              type="text"
                              placeholder="Name *"
                              value={fileData.name}
                              onChange={(e) => updateBulkFileData(fileData.id, 'name', e.target.value)}
                              disabled={fileData.status !== 'pending'}
                              style={{ padding: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                            />
                            <input
                              type="text"
                              placeholder="Employee ID"
                              value={fileData.employee_id}
                              onChange={(e) => updateBulkFileData(fileData.id, 'employee_id', e.target.value)}
                              disabled={fileData.status !== 'pending'}
                              style={{ padding: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                            />
                            <input
                              type="text"
                              placeholder="Department"
                              value={fileData.department}
                              onChange={(e) => updateBulkFileData(fileData.id, 'department', e.target.value)}
                              disabled={fileData.status !== 'pending'}
                              style={{ padding: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                            />
                          </div>
                          <div className="grid grid-3" style={{ gap: '0.5rem' }}>
                            <input
                              type="text"
                              placeholder="Position"
                              value={fileData.position}
                              onChange={(e) => updateBulkFileData(fileData.id, 'position', e.target.value)}
                              disabled={fileData.status !== 'pending'}
                              style={{ padding: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                            />
                            <input
                              type="email"
                              placeholder="Email"
                              value={fileData.email}
                              onChange={(e) => updateBulkFileData(fileData.id, 'email', e.target.value)}
                              disabled={fileData.status !== 'pending'}
                              style={{ padding: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                            />
                            <input
                              type="tel"
                              placeholder="Phone"
                              value={fileData.phone}
                              onChange={(e) => updateBulkFileData(fileData.id, 'phone', e.target.value)}
                              disabled={fileData.status !== 'pending'}
                              style={{ padding: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '4px' }}
                            />
                          </div>

                          {/* Status and Error */}
                          <div style={{ marginTop: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              {fileData.status === 'success' && <CheckCircle size={16} color="#10b981" />}
                              {fileData.status === 'error' && <AlertCircle size={16} color="#ef4444" />}
                              {fileData.status === 'uploading' && <div className="loading-spinner" style={{ width: '16px', height: '16px' }}></div>}
                              <span style={{
                                fontSize: '0.875rem',
                                color: fileData.status === 'success' ? '#10b981' :
                                       fileData.status === 'error' ? '#ef4444' :
                                       fileData.status === 'uploading' ? '#f59e0b' : '#6b7280'
                              }}>
                                {fileData.status === 'pending' && 'Ready to upload'}
                                {fileData.status === 'uploading' && 'Uploading...'}
                                {fileData.status === 'success' && 'Uploaded successfully'}
                                {fileData.status === 'error' && `Error: ${fileData.error}`}
                              </span>
                            </div>

                            {fileData.status === 'pending' && (
                              <button
                                onClick={() => removeBulkFile(fileData.id)}
                                className="btn btn-secondary"
                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                              >
                                <X size={12} />
                                Remove
                              </button>
                            )}
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
          <div className="add-face-form">
            <h3 style={{ marginBottom: '1rem', color: '#2d3748' }}>Add New Face</h3>
            
            {selectedFile && (
              <div className="image-preview" style={{ marginBottom: '1.5rem' }}>
                <img 
                  src={URL.createObjectURL(selectedFile)} 
                  alt="Preview" 
                  style={{ maxWidth: '200px', borderRadius: '8px' }}
                />
                <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#718096' }}>
                  {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">
                    <User size={16} style={{ marginRight: '0.5rem' }} />
                    Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter full name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Badge size={16} style={{ marginRight: '0.5rem' }} />
                    Employee ID
                  </label>
                  <input
                    type="text"
                    name="employee_id"
                    value={formData.employee_id}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter employee ID"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Building size={16} style={{ marginRight: '0.5rem' }} />
                    Department
                  </label>
                  <input
                    type="text"
                    name="department"
                    value={formData.department}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter department"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Position</label>
                  <input
                    type="text"
                    name="position"
                    value={formData.position}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter position/title"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Mail size={16} style={{ marginRight: '0.5rem' }} />
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter email address"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    <Phone size={16} style={{ marginRight: '0.5rem' }} />
                    Phone
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter phone number"
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={uploading}
                >
                  {uploading ? (
                    <>
                      <div className="loading-spinner"></div>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload size={16} />
                      Add Face
                    </>
                  )}
                </button>
                <button 
                  type="button" 
                  onClick={cancelAdd}
                  className="btn btn-secondary"
                  disabled={uploading}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Known Faces Grid */}
        <div className="known-faces-section" style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ color: '#2d3748' }}>
              <Users size={20} style={{ marginRight: '0.5rem' }} />
              Known Faces ({knownFaces.length})
            </h2>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div className="loading-spinner"></div>
              <p style={{ marginTop: '1rem' }}>Loading known faces...</p>
            </div>
          ) : knownFaces.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '3rem',
              background: '#f7fafc',
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <Users size={48} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
              <h3 style={{ color: '#4a5568', marginBottom: '0.5rem' }}>No faces added yet</h3>
              <p style={{ color: '#718096' }}>Upload your first face to get started</p>
            </div>
          ) : (
            <div className="grid grid-3">
              {knownFaces.map((face) => (
                <div key={face.id} className="face-card">
                  <img 
                    src={apiService.images.getKnownFaceImageUrl(face.image_path.split('/').pop())}
                    alt={face.name}
                    className="face-image"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjdGQUZDIi8+CjxwYXRoIGQ9Ik0xMDAgODBDMTA4LjI4NCA4MCA5NSA3My4yODQgOTUgNjVDOTUgNTYuNzE2IDEwMS43MTYgNTAgMTEwIDUwQzExOC4yODQgNTAgMTI1IDU2LjcxNiAxMjUgNjVDMTI1IDczLjI4NCAxMTguMjg0IDgwIDExMCA4MEgxMDBaIiBmaWxsPSIjQTBBRUMwIi8+CjxwYXRoIGQ9Ik04MCAyNUMxNjUuMiAyNSAxMjUgMTQ1IDEwMCAxNDVDNzUgMTQ1IDM0LjggMTI1IDgwIDI1WiIgZmlsbD0iI0EwQUVDMCIvPgo8L3N2Zz4K';
                    }}
                  />
                  <div className="face-info">
                    <h3 className="face-name">{face.name}</h3>
                    <div className="face-details">
                      {face.employee_id && (
                        <span className="face-detail">ID: {face.employee_id}</span>
                      )}
                      {face.department && (
                        <span className="face-detail">Dept: {face.department}</span>
                      )}
                      {face.position && (
                        <span className="face-detail">Position: {face.position}</span>
                      )}
                      {face.email && (
                        <span className="face-detail">Email: {face.email}</span>
                      )}
                      {face.phone && (
                        <span className="face-detail">Phone: {face.phone}</span>
                      )}
                    </div>
                  </div>
                  <div className="face-actions">
                    <button 
                      onClick={() => handleDelete(face.id, face.name)}
                      className="btn btn-danger"
                      style={{ width: '100%' }}
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Export Modal */}
        <ExportModal
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          data={null}
          type="database"
        />
      </div>
    </div>
  );
};

export default AdminPanel;
