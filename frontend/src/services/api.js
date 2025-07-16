import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    } else if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data?.message || 'Internal server error');
    }
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // System stats
  getStats: () => api.get('/stats'),

  // Admin panel APIs
  admin: {
    // Upload known face
    uploadFace: (formData) => {
      return api.post('/admin/upload-face', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },

    // Get all known faces
    getKnownFaces: () => api.get('/admin/faces'),

    // Delete known face
    deleteFace: (faceId) => api.delete(`/admin/faces/${faceId}`),

    // Bulk upload faces
    bulkUploadFaces: (formData) => {
      return api.post('/admin/bulk-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },

    // Search faces with filters
    searchFaces: (params) => api.get('/admin/search', { params }),

    // Get departments
    getDepartments: () => api.get('/admin/departments'),

    // Get positions
    getPositions: () => api.get('/admin/positions'),

    // Get face statistics
    getStatistics: () => api.get('/admin/statistics'),
  },

  // Face recognition APIs
  recognition: {
    // Recognize faces in image
    recognizeFaces: (formData) => {
      return api.post('/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },

    // Get recognition history
    getHistory: (limit = 50) => api.get(`/recognition-history?limit=${limit}`),

    // Search history with filters
    searchHistory: (params) => api.get('/history/search', { params }),

    // Get history statistics
    getHistoryStatistics: () => api.get('/history/statistics'),
  },

  // Camera APIs
  camera: {
    // Process captured image from camera
    captureImage: (data) => {
      return api.post('/camera/capture', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
    },

    // Process stream frame for real-time recognition
    processStreamFrame: (data) => {
      return api.post('/camera/stream-frame', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
    },
  },

  // Export APIs
  export: {
    // Export recognition results
    exportResults: (data) => {
      return api.post('/export/results', data, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    },

    // Export face database
    exportDatabase: (format = 'json') => {
      return api.get(`/export/database?format=${format}`, {
        responseType: 'blob',
      });
    },

    // Download image
    downloadImage: (imagePath) => {
      return api.get(`/download/image/${imagePath}`, {
        responseType: 'blob',
      });
    },
  },

  // Image serving
  images: {
    getKnownFaceImageUrl: (filename) => `${API_BASE_URL}/images/known/${filename}`,
    getTestImageUrl: (filename) => `${API_BASE_URL}/images/test/${filename}`,
  },
};

export default api;
