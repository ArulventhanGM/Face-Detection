import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../services/api';
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
  RefreshCw
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminPanel = () => {
  const [knownFaces, setKnownFaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
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

        {/* Upload Section */}
        {!showAddForm ? (
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
      </div>
    </div>
  );
};

export default AdminPanel;
