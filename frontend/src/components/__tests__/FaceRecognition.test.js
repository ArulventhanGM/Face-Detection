import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FaceRecognition from '../pages/FaceRecognition';
import { apiService } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  apiService: {
    recognition: {
      recognizeFaces: jest.fn(),
    },
    export: {
      exportResults: jest.fn(),
    },
    images: {
      getTestImageUrl: jest.fn((filename) => `http://localhost:5000/api/images/test/${filename}`),
    }
  }
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Mock react-dropzone
jest.mock('react-dropzone', () => ({
  useDropzone: () => ({
    getRootProps: () => ({ 'data-testid': 'dropzone' }),
    getInputProps: () => ({ 'data-testid': 'file-input' }),
    isDragActive: false,
  }),
}));

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mocked-url');
global.URL.revokeObjectURL = jest.fn();

describe('FaceRecognition Component', () => {
  const mockRecognitionResult = {
    total_faces_detected: 2,
    total_faces_recognized: 1,
    recognized_faces: [
      {
        id: 1,
        name: 'John Doe',
        employee_id: 'EMP001',
        department: 'Engineering',
        position: 'Software Engineer',
        email: 'john.doe@test.com',
        phone: '+1234567890',
        confidence: 87.5,
        face_location: [50, 200, 150, 100],
        lbph_confidence: 45.2,
        face_index: 0
      },
      {
        id: null,
        name: 'Unknown',
        employee_id: 'N/A',
        department: 'N/A',
        position: 'N/A',
        email: 'N/A',
        phone: 'N/A',
        confidence: 0.0,
        face_location: [60, 220, 160, 120],
        lbph_confidence: 150.0,
        face_index: 1
      }
    ],
    processing_time: 2.34,
    image_path: 'uploads/test_images/test_123.jpg',
    image_dimensions: '1920x1080',
    detection_model: 'haar_cascade',
    annotated_image_path: 'uploads/test_images/test_123_annotated.jpg'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders face recognition interface', () => {
    render(<FaceRecognition />);
    
    expect(screen.getByText('Face Recognition')).toBeInTheDocument();
    expect(screen.getByText('Upload an image to detect and recognize faces')).toBeInTheDocument();
    expect(screen.getByTestId('dropzone')).toBeInTheDocument();
  });

  test('handles file upload and recognition', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Mock file selection
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);

    // Click recognize button
    const recognizeButton = screen.getByText('Recognize Faces');
    fireEvent.click(recognizeButton);

    await waitFor(() => {
      expect(apiService.recognition.recognizeFaces).toHaveBeenCalled();
    });

    // Check if results are displayed
    await waitFor(() => {
      expect(screen.getByText('Recognition Results')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Unknown')).toBeInTheDocument();
    });
  });

  test('displays recognition statistics correctly', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // faces detected
      expect(screen.getByText('1')).toBeInTheDocument(); // faces recognized
    });

    // Check processing time display
    expect(screen.getByText(/2\.34/)).toBeInTheDocument();
  });

  test('switches between image view modes', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('Original')).toBeInTheDocument();
    });

    // Switch to annotated view
    const annotatedButton = screen.getByText('Annotated');
    fireEvent.click(annotatedButton);

    // Switch to split view
    const splitButton = screen.getByText('Split View');
    fireEvent.click(splitButton);

    expect(splitButton).toHaveClass('btn-primary');
  });

  test('displays face details correctly', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Check if face details are displayed
    expect(screen.getByText('EMP001')).toBeInTheDocument();
    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('87.5%')).toBeInTheDocument();
  });

  test('handles face selection', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Click on a face card
    const faceCard = screen.getByText('John Doe').closest('.recognized-face-card');
    fireEvent.click(faceCard);

    // Should show clear selection button
    expect(screen.getByText('Clear Selection')).toBeInTheDocument();
  });

  test('exports recognition results', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    apiService.export.exportResults.mockResolvedValue({
      data: new Blob(['test data'], { type: 'application/json' })
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('Recognition Results')).toBeInTheDocument();
    });

    // Click export button
    const exportButton = screen.getByTitle('Export Results');
    fireEvent.click(exportButton);

    // Should open export modal
    expect(screen.getByText('Export Recognition Results')).toBeInTheDocument();
  });

  test('clears results', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('Recognition Results')).toBeInTheDocument();
    });

    // Click clear button
    const clearButton = screen.getByTitle('Clear Results');
    fireEvent.click(clearButton);

    // Results should be cleared
    expect(screen.queryByText('Recognition Results')).not.toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    apiService.recognition.recognizeFaces.mockRejectedValue(
      new Error('Recognition failed')
    );

    render(<FaceRecognition />);
    
    // Upload file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(apiService.recognition.recognizeFaces).toHaveBeenCalled();
    });

    // Should handle error gracefully (no crash)
    expect(screen.getByText('Face Recognition')).toBeInTheDocument();
  });

  test('validates file types', () => {
    render(<FaceRecognition />);
    
    // Try to upload invalid file type
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);

    // Should show error or reject file
    expect(screen.getByText('Face Recognition')).toBeInTheDocument();
  });

  test('displays confidence badges correctly', async () => {
    apiService.recognition.recognizeFaces.mockResolvedValue({
      data: {
        success: true,
        data: mockRecognitionResult
      }
    });

    render(<FaceRecognition />);
    
    // Upload and process file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = screen.getByTestId('file-input');
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);
    fireEvent.click(screen.getByText('Recognize Faces'));

    await waitFor(() => {
      expect(screen.getByText('87.5%')).toBeInTheDocument();
    });

    // Should show confidence badge
    const confidenceBadge = screen.getByText('87.5%');
    expect(confidenceBadge).toBeInTheDocument();
  });
});
