import React, { useState } from 'react';
import { apiService } from '../services/api';
import { 
  Download, 
  FileText, 
  File, 
  Image,
  X,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';
import toast from 'react-hot-toast';

const ExportModal = ({ isOpen, onClose, data, type = 'results' }) => {
  const [selectedFormat, setSelectedFormat] = useState('json');
  const [includeImages, setIncludeImages] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen) return null;

  const formatOptions = type === 'results' 
    ? [
        { value: 'json', label: 'JSON', icon: FileText, description: 'Structured data format' },
        { value: 'csv', label: 'CSV', icon: File, description: 'Spreadsheet compatible' },
        { value: 'pdf', label: 'PDF', icon: FileText, description: 'Professional report' }
      ]
    : [
        { value: 'json', label: 'JSON', icon: FileText, description: 'Structured data format' },
        { value: 'csv', label: 'CSV', icon: File, description: 'Spreadsheet compatible' }
      ];

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      let response;
      let filename;
      
      if (type === 'results') {
        response = await apiService.export.exportResults({
          results: data,
          format: selectedFormat,
          include_images: includeImages
        });
        filename = `face_recognition_results_${new Date().toISOString().slice(0, 19)}.${selectedFormat}`;
      } else if (type === 'database') {
        response = await apiService.export.exportDatabase(selectedFormat);
        filename = `face_database_${new Date().toISOString().slice(0, 19)}.${selectedFormat}`;
      }

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success(`Export completed successfully!`);
      onClose();
      
    } catch (error) {
      console.error('Export error:', error);
      const errorMessage = error.response?.data?.message || 'Export failed';
      toast.error(errorMessage);
    } finally {
      setIsExporting(false);
    }
  };

  const downloadImage = async (imagePath) => {
    try {
      const response = await apiService.export.downloadImage(imagePath);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `face_recognition_${imagePath.split('/').pop()}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Image downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download image');
    }
  };

  return (
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
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '80vh',
        overflowY: 'auto',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ margin: 0, color: '#1f2937' }}>
            Export {type === 'results' ? 'Recognition Results' : 'Face Database'}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '0.5rem',
              borderRadius: '6px',
              color: '#6b7280'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Format Selection */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', color: '#374151', fontSize: '1rem' }}>Select Format</h3>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {formatOptions.map((format) => {
              const Icon = format.icon;
              return (
                <label
                  key={format.value}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '1rem',
                    border: selectedFormat === format.value ? '2px solid #667eea' : '1px solid #e5e7eb',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    background: selectedFormat === format.value ? '#f0f4ff' : 'white',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <input
                    type="radio"
                    name="format"
                    value={format.value}
                    checked={selectedFormat === format.value}
                    onChange={(e) => setSelectedFormat(e.target.value)}
                    style={{ marginRight: '0.75rem' }}
                  />
                  <Icon size={20} style={{ marginRight: '0.75rem', color: '#6b7280' }} />
                  <div>
                    <div style={{ fontWeight: '500', color: '#1f2937' }}>{format.label}</div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{format.description}</div>
                  </div>
                </label>
              );
            })}
          </div>
        </div>

        {/* Options */}
        {type === 'results' && (
          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#374151', fontSize: '1rem' }}>Export Options</h3>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={includeImages}
                onChange={(e) => setIncludeImages(e.target.checked)}
              />
              <span style={{ fontSize: '0.875rem', color: '#374151' }}>
                Include image paths in export
              </span>
            </label>
          </div>
        )}

        {/* Image Downloads */}
        {type === 'results' && data?.image_path && (
          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#374151', fontSize: '1rem' }}>Download Images</h3>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => downloadImage(data.image_path)}
                className="btn btn-secondary"
                style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
              >
                <Image size={14} style={{ marginRight: '0.5rem' }} />
                Original Image
              </button>
              {data.annotated_image_path && (
                <button
                  onClick={() => downloadImage(data.annotated_image_path)}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}
                >
                  <Image size={14} style={{ marginRight: '0.5rem' }} />
                  Annotated Image
                </button>
              )}
            </div>
          </div>
        )}

        {/* Export Summary */}
        <div style={{
          padding: '1rem',
          background: '#f9fafb',
          borderRadius: '8px',
          marginBottom: '2rem',
          border: '1px solid #e5e7eb'
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#374151', fontSize: '0.875rem' }}>Export Summary</h4>
          <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
            {type === 'results' ? (
              <>
                <div>• {data?.total_faces_detected || 0} faces detected</div>
                <div>• {data?.total_faces_recognized || 0} faces recognized</div>
                <div>• Processing time: {data?.processing_time?.toFixed(2) || 0}s</div>
              </>
            ) : (
              <div>• Complete face database export</div>
            )}
            <div>• Format: {selectedFormat.toUpperCase()}</div>
            {type === 'results' && includeImages && <div>• Including image paths</div>}
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            className="btn btn-secondary"
            disabled={isExporting}
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            className="btn btn-primary"
            disabled={isExporting}
            style={{ minWidth: '120px' }}
          >
            {isExporting ? (
              <>
                <Loader size={16} style={{ marginRight: '0.5rem', animation: 'spin 1s linear infinite' }} />
                Exporting...
              </>
            ) : (
              <>
                <Download size={16} style={{ marginRight: '0.5rem' }} />
                Export
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;
