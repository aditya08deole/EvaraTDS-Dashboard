import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GlassLayout from './components/layout/GlassLayout';
import Dashboard from './components/Dashboard';
import History from './pages/History';
import Settings from './pages/Settings';
import { useRefresh } from './hooks/useRefresh';
import './index.css';

function App() {
  useRefresh(10000);

  return (
    <Router>
      <GlassLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </GlassLayout>
    </Router>
  );
}

export default App;