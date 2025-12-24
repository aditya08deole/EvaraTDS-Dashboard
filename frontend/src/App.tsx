import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GlassLayout from './components/layout/GlassLayout';
import Dashboard from './components/Dashboard';
import History from './pages/History';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Onboarding from './pages/Onboarding';
import { useRefresh } from './hooks/useRefresh';
import { useSettingsStore } from './store/useSettingsStore';
import { RedirectToSignIn, SignedIn, SignedOut, useAuth } from '@clerk/clerk-react';
import { AuthInterceptor } from './components/AuthInterceptor';
import './index.css';

// Protected Route using Clerk session
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isSignedIn } = useAuth();
  return isSignedIn ? children : <RedirectToSignIn />;
};

function App() {
  useRefresh(10000);
  const { loadSettings } = useSettingsStore();

  // Initialize auth and settings on app start
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  return (
    <Router>
      <AuthInterceptor />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/onboarding" element={
          <SignedIn>
            <GlassLayout><Onboarding /></GlassLayout>
          </SignedIn>
        } />
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