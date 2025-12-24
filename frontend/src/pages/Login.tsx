import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { Lock, User, Eye, EyeOff } from 'lucide-react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const success = await login(username, password);
    
    if (success) {
      navigate('/dashboard');
    } else {
      setError('Invalid credentials. Try admin/admin123 or viewer/viewer123');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0F1A] via-[#111827] to-[#161E2E] p-4">
      <div className="w-full max-w-md">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center gap-4 mb-6">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-16 w-auto" />
            <img src="/IIITH.png" alt="IIITH" className="h-16 w-auto" />
          </div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] bg-clip-text text-transparent mb-2">
            EvaraTDS
          </h1>
          <p className="text-[#9CA3AF] text-sm font-medium">IoT Water Quality Monitoring System</p>
        </div>

        {/* Login Form */}
        <div className="glass-card p-8 rounded-xl border border-[#1F2937]">
          <h2 className="text-2xl font-bold text-[#E5E7EB] mb-6 text-center">Sign In</h2>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label className="block text-[#9CA3AF] text-sm font-medium mb-2">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#6B7280]" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#161E2E] border border-[#1F2937] text-[#E5E7EB] rounded-lg pl-11 pr-4 py-3 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none transition"
                  placeholder="Enter username"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-[#9CA3AF] text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#6B7280]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#161E2E] border border-[#1F2937] text-[#E5E7EB] rounded-lg pl-11 pr-11 py-3 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none transition"
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B7280] hover:text-[#38BDF8] transition"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-bold py-3 rounded-lg transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-[#1F2937]">
            <p className="text-[#6B7280] text-xs text-center mb-3">Demo Credentials:</p>
            <div className="space-y-2 text-xs">
              <div className="bg-[#161E2E] p-3 rounded border border-[#1F2937]">
                <p className="text-[#38BDF8] font-bold mb-1">Admin Access</p>
                <p className="text-[#9CA3AF]">Username: <span className="text-[#E5E7EB] font-mono">admin</span></p>
                <p className="text-[#9CA3AF]">Password: <span className="text-[#E5E7EB] font-mono">admin123</span></p>
              </div>
              <div className="bg-[#161E2E] p-3 rounded border border-[#1F2937]">
                <p className="text-[#22C55E] font-bold mb-1">Viewer Access</p>
                <p className="text-[#9CA3AF]">Username: <span className="text-[#E5E7EB] font-mono">viewer</span></p>
                <p className="text-[#9CA3AF]">Password: <span className="text-[#E5E7EB] font-mono">viewer123</span></p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-[#6B7280] text-xs mt-6">
          © 2025 EvaraTech & IIITH. Enterprise IoT Solutions.
        </p>
      </div>
    </div>
  );
};

export default Login;
