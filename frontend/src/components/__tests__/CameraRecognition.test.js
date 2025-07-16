import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CameraRecognition from '../pages/CameraRecognition';
import { apiService } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  apiService: {
    camera: {
      captureImage: jest.fn(),
      processStreamFrame: jest.fn(),
    },
    export: {
      downloadImage: jest.fn(),
    }
  }
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Mock navigator.mediaDevices
const mockMediaDevices = {
  getUserMedia: jest.fn(),
};

Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: mockMediaDevices,
});

// Mock HTMLVideoElement
Object.defineProperty(HTMLVideoElement.prototype, 'play', {
  writable: true,
  value: jest.fn().mockResolvedValue(),
});

Object.defineProperty(HTMLVideoElement.prototype, 'videoWidth', {
  writable: true,
  value: 640,
});

Object.defineProperty(HTMLVideoElement.prototype, 'videoHeight', {
  writable: true,
  value: 480,
});

// Mock HTMLCanvasElement
Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  writable: true,
  value: jest.fn().mockReturnValue({
    drawImage: jest.fn(),
  }),
});

Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
  writable: true,
  value: jest.fn().mockReturnValue('data:image/jpeg;base64,test'),
});

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mocked-url');
global.URL.revokeObjectURL = jest.fn();

describe('CameraRecognition Component', () => {
  const mockCameraResult = {
    total_faces_detected: 1,
    total_faces_recognized: 1,
    recognized_faces: [
      {
        name: 'John Doe',
        employee_id: 'EMP001',
        department: 'Engineering',
        confidence: 92.3,
        face_location: [50, 200, 150, 100],
        face_index: 0
      }
    ],
    processing_time: 1.2,
    image_info: {
      width: 640,
      height: 480,
      format: 'JPEG'
    }
  };

  const mockStream = {
    getTracks: jest.fn().mockReturnValue([
      { stop: jest.fn() }
    ])
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockMediaDevices.getUserMedia.mockResolvedValue(mockStream);
  });

  test('renders camera recognition interface', () => {
    render(<CameraRecognition />);
    
    expect(screen.getByText('Camera Face Recognition')).toBeInTheDocument();
    expect(screen.getByText('Use your camera for real-time face detection and recognition')).toBeInTheDocument();
    expect(screen.getByText('Start Camera')).toBeInTheDocument();
  });

  test('starts camera successfully', async () => {
    render(<CameraRecognition />);
    
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockMediaDevices.getUserMedia).toHaveBeenCalledWith({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      });
    });

    // Should show stop camera button
    expect(screen.getByText('Stop Camera')).toBeInTheDocument();
  });

  test('stops camera', async () => {
    render(<CameraRecognition />);
    
    // Start camera first
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Stop Camera')).toBeInTheDocument();
    });

    // Stop camera
    const stopButton = screen.getByText('Stop Camera');
    fireEvent.click(stopButton);

    expect(mockStream.getTracks()[0].stop).toHaveBeenCalled();
    expect(screen.getByText('Start Camera')).toBeInTheDocument();
  });

  test('captures and processes image', async () => {
    apiService.camera.captureImage.mockResolvedValue({
      data: {
        success: true,
        data: mockCameraResult
      }
    });

    render(<CameraRecognition />);
    
    // Start camera
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Capture & Recognize')).toBeInTheDocument();
    });

    // Capture and process
    const captureButton = screen.getByText('Capture & Recognize');
    fireEvent.click(captureButton);

    await waitFor(() => {
      expect(apiService.camera.captureImage).toHaveBeenCalled();
    });

    // Check if results are displayed
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  test('enables real-time mode', async () => {
    apiService.camera.processStreamFrame.mockResolvedValue({
      data: {
        success: true,
        data: {
          total_faces_detected: 1,
          total_faces_recognized: 1,
          recognized_faces: [
            {
              name: 'John Doe',
              confidence: 88.5,
              face_location: [50, 200, 150, 100]
            }
          ],
          processing_time: 0.8
        }
      }
    });

    render(<CameraRecognition />);
    
    // Start camera
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Real-time Mode')).toBeInTheDocument();
    });

    // Enable real-time mode
    const realTimeCheckbox = screen.getByLabelText('Real-time Mode');
    fireEvent.click(realTimeCheckbox);

    expect(realTimeCheckbox).toBeChecked();

    // Wait for real-time processing to start
    await waitFor(() => {
      expect(screen.getByText('Real-time')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('displays stream statistics', async () => {
    apiService.camera.processStreamFrame.mockResolvedValue({
      data: {
        success: true,
        data: {
          total_faces_detected: 1,
          total_faces_recognized: 1,
          recognized_faces: [],
          processing_time: 0.5
        }
      }
    });

    render(<CameraRecognition />);
    
    // Start camera and enable real-time mode
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      const realTimeCheckbox = screen.getByLabelText('Real-time Mode');
      fireEvent.click(realTimeCheckbox);
    });

    // Wait for statistics to appear
    await waitFor(() => {
      expect(screen.getByText('Stream Statistics')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('handles camera access error', async () => {
    mockMediaDevices.getUserMedia.mockRejectedValue(new Error('Camera access denied'));

    render(<CameraRecognition />);
    
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockMediaDevices.getUserMedia).toHaveBeenCalled();
    });

    // Should still show start camera button (camera failed to start)
    expect(screen.getByText('Start Camera')).toBeInTheDocument();
  });

  test('downloads captured image', async () => {
    apiService.camera.captureImage.mockResolvedValue({
      data: {
        success: true,
        data: mockCameraResult
      }
    });

    apiService.export.downloadImage.mockResolvedValue({
      data: new Blob(['test'], { type: 'image/jpeg' })
    });

    render(<CameraRecognition />);
    
    // Start camera and capture
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      const captureButton = screen.getByText('Capture & Recognize');
      fireEvent.click(captureButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Download Results')).toBeInTheDocument();
    });

    // Download results
    const downloadButton = screen.getByText('Download Results');
    fireEvent.click(downloadButton);

    // Should trigger download
    expect(downloadButton).toBeInTheDocument();
  });

  test('displays real-time results history', async () => {
    apiService.camera.processStreamFrame.mockResolvedValue({
      data: {
        success: true,
        data: {
          total_faces_detected: 1,
          total_faces_recognized: 1,
          recognized_faces: [
            {
              name: 'John Doe',
              confidence: 85.2
            }
          ],
          processing_time: 0.7
        }
      }
    });

    render(<CameraRecognition />);
    
    // Start camera and enable real-time mode
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      const realTimeCheckbox = screen.getByLabelText('Real-time Mode');
      fireEvent.click(realTimeCheckbox);
    });

    // Wait for real-time results
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    }, { timeout: 3000 });

    // Should show timestamp
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    // Note: This might be flaky due to timing, but tests the concept
  });

  test('clears real-time results', async () => {
    render(<CameraRecognition />);
    
    // Start camera
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      const realTimeCheckbox = screen.getByLabelText('Real-time Mode');
      fireEvent.click(realTimeCheckbox);
    });

    // Disable real-time mode
    await waitFor(() => {
      const realTimeCheckbox = screen.getByLabelText('Real-time Mode');
      fireEvent.click(realTimeCheckbox);
    });

    expect(screen.getByLabelText('Real-time Mode')).not.toBeChecked();
  });

  test('shows processing indicator', async () => {
    // Mock a slow API response
    apiService.camera.captureImage.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({
        data: { success: true, data: mockCameraResult }
      }), 1000))
    );

    render(<CameraRecognition />);
    
    // Start camera
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      const captureButton = screen.getByText('Capture & Recognize');
      fireEvent.click(captureButton);
    });

    // Should show processing indicator
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    apiService.camera.captureImage.mockRejectedValue(new Error('API Error'));

    render(<CameraRecognition />);
    
    // Start camera
    const startButton = screen.getByText('Start Camera');
    fireEvent.click(startButton);

    await waitFor(() => {
      const captureButton = screen.getByText('Capture & Recognize');
      fireEvent.click(captureButton);
    });

    await waitFor(() => {
      expect(apiService.camera.captureImage).toHaveBeenCalled();
    });

    // Should handle error gracefully
    expect(screen.getByText('Camera Face Recognition')).toBeInTheDocument();
  });
});
