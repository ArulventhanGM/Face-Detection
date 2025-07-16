import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminPanel from '../pages/AdminPanel';
import { apiService } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  apiService: {
    admin: {
      getFaces: jest.fn(),
      uploadFace: jest.fn(),
      deleteFace: jest.fn(),
      searchFaces: jest.fn(),
      getDepartments: jest.fn(),
      getPositions: jest.fn(),
      getStatistics: jest.fn(),
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

describe('AdminPanel Component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Mock successful API responses
    apiService.admin.getFaces.mockResolvedValue({
      data: {
        success: true,
        data: [
          {
            id: 1,
            name: 'John Doe',
            employee_id: 'EMP001',
            department: 'Engineering',
            position: 'Software Engineer',
            email: 'john.doe@test.com',
            phone: '+1234567890',
            image_path: 'uploads/known_faces/john_doe.jpg',
            created_at: '2024-01-15T10:30:00Z'
          }
        ]
      }
    });

    apiService.admin.getDepartments.mockResolvedValue({
      data: { success: true, data: ['Engineering', 'Marketing'] }
    });

    apiService.admin.getPositions.mockResolvedValue({
      data: { success: true, data: ['Software Engineer', 'Manager'] }
    });

    apiService.admin.getStatistics.mockResolvedValue({
      data: {
        success: true,
        data: {
          total_faces: 1,
          departments: [{ name: 'Engineering', count: 1 }],
          positions: [{ name: 'Software Engineer', count: 1 }],
          recent_additions: 1
        }
      }
    });
  });

  test('renders admin panel with known faces', async () => {
    render(<AdminPanel />);
    
    // Check if the main heading is present
    expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    
    // Wait for faces to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    // Check if face details are displayed
    expect(screen.getByText('EMP001')).toBeInTheDocument();
    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
  });

  test('displays upload form when add new face is clicked', async () => {
    render(<AdminPanel />);
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Single Upload')).toBeInTheDocument();
    });
    
    // Click on single upload (should be active by default)
    const uploadSection = screen.getByTestId('dropzone');
    expect(uploadSection).toBeInTheDocument();
  });

  test('handles face upload successfully', async () => {
    apiService.admin.uploadFace.mockResolvedValue({
      data: {
        success: true,
        data: { face_id: 2, name: 'Jane Smith' }
      }
    });

    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    });

    // Fill in the form (assuming form fields are rendered)
    const nameInput = screen.getByPlaceholderText('Full Name *');
    fireEvent.change(nameInput, { target: { value: 'Jane Smith' } });

    const employeeIdInput = screen.getByPlaceholderText('Employee ID');
    fireEvent.change(employeeIdInput, { target: { value: 'EMP002' } });

    // Mock file upload
    const fileInput = screen.getByTestId('file-input');
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);

    // Submit form
    const uploadButton = screen.getByText('Upload');
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(apiService.admin.uploadFace).toHaveBeenCalled();
    });
  });

  test('handles face deletion', async () => {
    apiService.admin.deleteFace.mockResolvedValue({
      data: { success: true }
    });

    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Find and click delete button
    const deleteButton = screen.getByTitle('Delete face');
    fireEvent.click(deleteButton);

    // Confirm deletion
    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(apiService.admin.deleteFace).toHaveBeenCalledWith(1);
    });
  });

  test('displays error message when API fails', async () => {
    apiService.admin.getFaces.mockRejectedValue(new Error('API Error'));

    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    });

    // Should handle error gracefully
    expect(apiService.admin.getFaces).toHaveBeenCalled();
  });

  test('filters faces by search query', async () => {
    apiService.admin.searchFaces.mockResolvedValue({
      data: {
        success: true,
        data: {
          faces: [
            {
              id: 1,
              name: 'John Doe',
              employee_id: 'EMP001',
              department: 'Engineering'
            }
          ],
          total_count: 1
        }
      }
    });

    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    });

    // Find search input and enter query
    const searchInput = screen.getByPlaceholderText('Search faces...');
    fireEvent.change(searchInput, { target: { value: 'John' } });

    await waitFor(() => {
      expect(apiService.admin.searchFaces).toHaveBeenCalledWith(
        expect.objectContaining({ q: 'John' })
      );
    });
  });

  test('switches between single and bulk upload modes', async () => {
    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Single Upload')).toBeInTheDocument();
    });

    // Click bulk upload button
    const bulkUploadButton = screen.getByText('Bulk Upload');
    fireEvent.click(bulkUploadButton);

    // Should show bulk upload interface
    expect(screen.getByText('Bulk Upload Faces')).toBeInTheDocument();
    expect(screen.getByText('Select Multiple Images')).toBeInTheDocument();
  });

  test('displays statistics correctly', async () => {
    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Faces')).toBeInTheDocument();
    });

    // Check if statistics are displayed
    expect(screen.getByText('1')).toBeInTheDocument(); // total faces count
  });

  test('handles export functionality', async () => {
    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    });

    // Find and click export button
    const exportButton = screen.getByText('Export Database');
    fireEvent.click(exportButton);

    // Should open export modal
    expect(screen.getByText('Export Face Database')).toBeInTheDocument();
  });

  test('validates form input', async () => {
    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
    });

    // Try to submit form without required fields
    const uploadButton = screen.getByText('Upload');
    fireEvent.click(uploadButton);

    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText('Please select an image')).toBeInTheDocument();
    });
  });

  test('handles bulk upload with multiple files', async () => {
    render(<AdminPanel />);
    
    await waitFor(() => {
      expect(screen.getByText('Bulk Upload')).toBeInTheDocument();
    });

    // Switch to bulk upload
    const bulkUploadButton = screen.getByText('Bulk Upload');
    fireEvent.click(bulkUploadButton);

    // Mock multiple file selection
    const files = [
      new File(['test1'], 'person1.jpg', { type: 'image/jpeg' }),
      new File(['test2'], 'person2.jpg', { type: 'image/jpeg' })
    ];

    // Simulate file drop
    const dropzone = screen.getByTestId('dropzone');
    fireEvent.drop(dropzone, { dataTransfer: { files } });

    // Should display file list
    await waitFor(() => {
      expect(screen.getByText('Files to Upload (2)')).toBeInTheDocument();
    });
  });
});
