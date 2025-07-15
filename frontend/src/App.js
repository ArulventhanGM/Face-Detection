import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import FaceRecognition from './pages/FaceRecognition';
import History from './pages/History';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/recognize" element={<FaceRecognition />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              theme: {
                primary: '#4aed88',
              },
            },
            error: {
              duration: 5000,
              theme: {
                primary: '#ff6b6b',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
