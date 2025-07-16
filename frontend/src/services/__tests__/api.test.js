import { apiService } from '../api';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Face Recognition API', () => {
    test('recognizeFaces calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            total_faces_detected: 2,
            total_faces_recognized: 1,
            recognized_faces: []
          }
        }
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const formData = new FormData();
      formData.append('image', new File(['test'], 'test.jpg'));

      const result = await apiService.recognition.recognizeFaces(formData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      expect(result).toEqual(mockResponse);
    });

    test('getHistory calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: []
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.recognition.getHistory(25);

      expect(mockedAxios.get).toHaveBeenCalledWith('/recognition-history?limit=25');
      expect(result).toEqual(mockResponse);
    });

    test('searchHistory calls correct endpoint with params', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            history: [],
            total_count: 0
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const params = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        limit: 20
      };

      const result = await apiService.recognition.searchHistory(params);

      expect(mockedAxios.get).toHaveBeenCalledWith('/history/search', { params });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Admin API', () => {
    test('getFaces calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: [
            {
              id: 1,
              name: 'John Doe',
              employee_id: 'EMP001'
            }
          ]
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.admin.getFaces();

      expect(mockedAxios.get).toHaveBeenCalledWith('/admin/faces');
      expect(result).toEqual(mockResponse);
    });

    test('uploadFace calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            face_id: 1,
            name: 'John Doe'
          }
        }
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const formData = new FormData();
      formData.append('image', new File(['test'], 'test.jpg'));
      formData.append('name', 'John Doe');

      const result = await apiService.admin.uploadFace(formData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/admin/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      expect(result).toEqual(mockResponse);
    });

    test('deleteFace calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Face deleted successfully'
        }
      };

      mockedAxios.delete.mockResolvedValue(mockResponse);

      const result = await apiService.admin.deleteFace(1);

      expect(mockedAxios.delete).toHaveBeenCalledWith('/admin/faces/1');
      expect(result).toEqual(mockResponse);
    });

    test('searchFaces calls correct endpoint with params', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            faces: [],
            total_count: 0
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const params = {
        q: 'john',
        department: 'engineering',
        limit: 20,
        offset: 0
      };

      const result = await apiService.admin.searchFaces(params);

      expect(mockedAxios.get).toHaveBeenCalledWith('/admin/search', { params });
      expect(result).toEqual(mockResponse);
    });

    test('getDepartments calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: ['Engineering', 'Marketing']
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.admin.getDepartments();

      expect(mockedAxios.get).toHaveBeenCalledWith('/admin/departments');
      expect(result).toEqual(mockResponse);
    });

    test('getStatistics calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            total_faces: 100,
            departments: [],
            positions: []
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.admin.getStatistics();

      expect(mockedAxios.get).toHaveBeenCalledWith('/admin/statistics');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Camera API', () => {
    test('captureImage calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            total_faces_detected: 1,
            recognized_faces: []
          }
        }
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const data = {
        image: 'data:image/jpeg;base64,test'
      };

      const result = await apiService.camera.captureImage(data);

      expect(mockedAxios.post).toHaveBeenCalledWith('/camera/capture', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockResponse);
    });

    test('processStreamFrame calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            total_faces_detected: 1,
            recognized_faces: []
          }
        }
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const data = {
        frame: 'data:image/jpeg;base64,test'
      };

      const result = await apiService.camera.processStreamFrame(data);

      expect(mockedAxios.post).toHaveBeenCalledWith('/camera/stream-frame', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Export API', () => {
    test('exportResults calls correct endpoint', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/json' });
      const mockResponse = {
        data: mockBlob
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const data = {
        results: { total_faces_detected: 1 },
        format: 'json'
      };

      const result = await apiService.export.exportResults(data);

      expect(mockedAxios.post).toHaveBeenCalledWith('/export/results', data, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockResponse);
    });

    test('exportDatabase calls correct endpoint', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/json' });
      const mockResponse = {
        data: mockBlob
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.export.exportDatabase('csv');

      expect(mockedAxios.get).toHaveBeenCalledWith('/export/database?format=csv', {
        responseType: 'blob',
      });
      expect(result).toEqual(mockResponse);
    });

    test('downloadImage calls correct endpoint', async () => {
      const mockBlob = new Blob(['test'], { type: 'image/jpeg' });
      const mockResponse = {
        data: mockBlob
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.export.downloadImage('test.jpg');

      expect(mockedAxios.get).toHaveBeenCalledWith('/download/image/test.jpg', {
        responseType: 'blob',
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('System API', () => {
    test('getStats calls correct endpoint', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            known_faces_count: 100,
            total_recognitions: 500
          }
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await apiService.system.getStats();

      expect(mockedAxios.get).toHaveBeenCalledWith('/system/stats');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Image URLs', () => {
    test('getKnownFaceImageUrl returns correct URL', () => {
      const url = apiService.images.getKnownFaceImageUrl('test.jpg');
      expect(url).toBe('http://localhost:5000/api/images/known/test.jpg');
    });

    test('getTestImageUrl returns correct URL', () => {
      const url = apiService.images.getTestImageUrl('test.jpg');
      expect(url).toBe('http://localhost:5000/api/images/test/test.jpg');
    });
  });

  describe('Error Handling', () => {
    test('handles network errors', async () => {
      const networkError = new Error('Network Error');
      mockedAxios.get.mockRejectedValue(networkError);

      await expect(apiService.admin.getFaces()).rejects.toThrow('Network Error');
    });

    test('handles API errors with response', async () => {
      const apiError = {
        response: {
          status: 400,
          data: {
            success: false,
            message: 'Bad Request'
          }
        }
      };
      mockedAxios.post.mockRejectedValue(apiError);

      await expect(apiService.recognition.recognizeFaces(new FormData())).rejects.toEqual(apiError);
    });
  });
});
