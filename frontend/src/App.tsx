import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GlassLayout from './components/layout/GlassLayout';
import Dashboard from './components/Dashboard';
import History from './pages/History';
import Settings from './pages/Settings';
import Login from './pages/Login';
import { useRefresh } from './hooks/useRefresh';
import { useAuthStore } from './store/useAuthStore';
import { useSettingsStore } from './store/useSettingsStore';
import './index.css';

// Protected Route Component
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  useRefresh(10000);
  const { initialize } = useAuthStore();
  const { loadSettings } = useSettingsStore();

  // Initialize auth and settings on app start
  useEffect(() => {
    initialize();
    loadSettings();
  }, [initialize, loadSettings]);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <GlassLayout><Dashboard /></GlassLayout>
          </ProtectedRoute>
        } />
        <Route path="/history" element={
          <ProtectedRoute>
            <GlassLayout><History /></GlassLayout>
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <GlassLayout><Settings /></GlassLayout>
          </ProtectedRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;