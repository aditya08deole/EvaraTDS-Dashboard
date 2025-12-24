import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { Lock, User, Eye, EyeOff, Mail, Phone, KeyRound } from 'lucide-react';

const Login: React.FC = () => {
  const [loginMethod, setLoginMethod] = useState<'admin' | 'viewer'>('admin');
  const [adminUsername, setAdminUsername] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [viewerUsername, setViewerUsername] = useState('');
  const [viewerPassword, setViewerPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showViewerPassword, setShowViewerPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleAdminSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const success = await login(adminUsername, adminPassword);
    
    if (success) {
      navigate('/dashboard');
    } else {
      setError('Invalid admin credentials. Please check your username and password.');
    }
    
    setLoading(false);
  };

  const handleViewerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Check credentials: username="user", password="pass@123"
    if (viewerUsername === 'user' && viewerPassword === 'pass@123') {
      const success = await login('viewer', 'viewer123');
      if (success) {
        navigate('/dashboard');
      }
    } else {
      setError('Invalid viewer credentials. Use username: user, password: pass@123');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0F1A] via-[#0E1627] to-[#111827] p-4 relative overflow-hidden">
      {/* Ambient Background Effects */}
      <div className="fixed top-0 left-0 w-[800px] h-[800px] bg-gradient-radial from-[#38BDF8]/10 to-transparent rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[800px] h-[800px] bg-gradient-radial from-[#0EA5E9]/8 to-transparent rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />
      
      <div className="w-full max-w-3xl relative z-10">
        {/* Logo & Title */}
        <div className="text-center mb-10">
          <div className="flex justify-center gap-8 mb-10">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-32 w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-32 w-auto object-contain" />
          </div>
          <h1 className="text-7xl md:text-8xl font-black bg-gradient-to-r from-[#38BDF8] via-[#0EA5E9] to-[#38BDF8] bg-clip-text text-transparent mb-4 leading-tight">
            EvaraTDS
          </h1>
          <p className="text-[#9CA3AF] text-xl font-semibold tracking-wide">IoT Water Quality Monitoring System</p>
        </div>

        {/* Login Card with Glass Morphism - 50% bigger */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-[#38BDF8]/20 via-[#0EA5E9]/10 to-transparent rounded-2xl blur-xl"></div>
          <div className="relative backdrop-blur-md bg-[#0F172A]/60 border border-[#1F2937]/60 rounded-2xl p-12 shadow-2xl">
            
            {/* Tab Selection */}
            <div className="flex gap-3 mb-10 bg-[#161E2E]/60 p-2 rounded-xl border border-[#1F2937]/50">
              <button
                onClick={() => { setLoginMethod('admin'); setError(''); }}
                className={`flex-1 py-4 px-6 rounded-lg font-bold text-base transition-all ${
                  loginMethod === 'admin'
                    ? 'bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] text-white shadow-lg'
                    : 'text-[#9CA3AF] hover:text-[#E5E7EB]'
                }`}
              >
                🔐 Admin Login
              </button>
              <button
                onClick={() => { setLoginMethod('viewer'); setError(''); }}
                className={`flex-1 py-4 px-6 rounded-lg font-bold text-base transition-all ${
                  loginMethod === 'viewer'
                    ? 'bg-gradient-to-r from-[#22C55E] to-[#10B981] text-white shadow-lg'
                    : 'text-[#9CA3AF] hover:text-[#E5E7EB]'
                }`}
              >
                👁️ Viewer Access
              </button>
            </div>

            {/* Admin Login Form */}
            {loginMethod === 'admin' && (
              <form onSubmit={handleAdminSubmit} className="space-y-6">
                <div>
                  <label className="block text-[#E5E7EB] text-base font-semibold mb-3">Admin Username</label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#38BDF8]" />
                    <input
                      type="text"
                      value={adminUsername}
                      onChange={(e) => setAdminUsername(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none transition placeholder:text-[#6B7280] text-base"
                      placeholder="Enter admin username"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[#E5E7EB] text-base font-semibold mb-3">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#38BDF8]" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={adminPassword}
                      onChange={(e) => setAdminPassword(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-12 py-4 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none transition placeholder:text-[#6B7280] text-base"
                      placeholder="Enter password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-[#6B7280] hover:text-[#38BDF8] transition"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-5 py-4 rounded-xl text-base font-medium backdrop-blur-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-bold py-5 text-lg rounded-xl transition-all shadow-lg shadow-[#38BDF8]/30 hover:shadow-xl hover:shadow-[#38BDF8]/40 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Signing in...' : 'Sign In as Admin'}
                </button>
              </form>
            )}

            {/* Viewer Simple Login Form */}
            {loginMethod === 'viewer' && (
              <form onSubmit={handleViewerSubmit} className="space-y-6">
                <div>
                  <label className="block text-[#E5E7EB] text-base font-semibold mb-3">Username</label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#22C55E]" />
                    <input
                      type="text"
                      value={viewerUsername}
                      onChange={(e) => setViewerUsername(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-4 py-4 focus:ring-2 focus:ring-[#22C55E] focus:border-transparent outline-none transition placeholder:text-[#6B7280] text-base"
                      placeholder="Enter username (user)"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[#E5E7EB] text-base font-semibold mb-3">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#22C55E]" />
                    <input
                      type={showViewerPassword ? 'text' : 'password'}
                      value={viewerPassword}
                      onChange={(e) => setViewerPassword(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-12 py-4 focus:ring-2 focus:ring-[#22C55E] focus:border-transparent outline-none transition placeholder:text-[#6B7280] text-base"
                      placeholder="Enter password (pass@123)"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowViewerPassword(!showViewerPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-[#6B7280] hover:text-[#22C55E] transition"
                    >
                      {showViewerPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-5 py-4 rounded-xl text-base font-medium backdrop-blur-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-[#22C55E] to-[#10B981] hover:from-[#10B981] hover:to-[#22C55E] text-white font-bold py-5 text-lg rounded-xl transition-all shadow-lg shadow-[#22C55E]/30 hover:shadow-xl hover:shadow-[#22C55E]/40 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Signing in...' : 'Sign In as Viewer'}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-[#6B7280] text-base mt-8 font-medium">
          © 2025 EvaraTech Pvt Ltd
        </p>
      </div>
    </div>
  );
};

export default Login;
