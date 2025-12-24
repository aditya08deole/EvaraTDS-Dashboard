import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { Lock, User, Eye, EyeOff, Mail, Phone, KeyRound } from 'lucide-react';

const Login: React.FC = () => {
  const [loginMethod, setLoginMethod] = useState<'admin' | 'viewer'>('admin');
  const [adminUsername, setAdminUsername] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [viewerContact, setViewerContact] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [contactMethod, setContactMethod] = useState<'email' | 'phone'>('email');
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

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simulate OTP sending
    setTimeout(() => {
      setOtpSent(true);
      setLoading(false);
      setError('');
      // In production, this would call your backend API to send OTP
      console.log(`OTP sent to ${viewerContact} via ${contactMethod}`);
    }, 1500);
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Demo: Accept "123456" as valid OTP, or login as viewer
    setTimeout(async () => {
      if (otp === '123456') {
        const success = await login('viewer', 'viewer123');
        if (success) {
          navigate('/dashboard');
        }
      } else {
        setError('Invalid OTP. Try 123456 for demo.');
        setLoading(false);
      }
    }, 1000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0F1A] via-[#0E1627] to-[#111827] p-4 relative overflow-hidden">
      {/* Ambient Background Effects */}
      <div className="fixed top-0 left-0 w-[800px] h-[800px] bg-gradient-radial from-[#38BDF8]/10 to-transparent rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[800px] h-[800px] bg-gradient-radial from-[#0EA5E9]/8 to-transparent rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />
      
      <div className="w-full max-w-xl relative z-10">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center gap-6 mb-8">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-20 w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-20 w-auto object-contain" />
          </div>
          <h1 className="text-5xl md:text-6xl font-black bg-gradient-to-r from-[#38BDF8] via-[#0EA5E9] to-[#38BDF8] bg-clip-text text-transparent mb-3 leading-tight">
            EvaraTDS
          </h1>
          <p className="text-[#9CA3AF] text-base font-semibold tracking-wide">IoT Water Quality Monitoring System</p>
        </div>

        {/* Login Card with Glass Morphism */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-[#38BDF8]/20 via-[#0EA5E9]/10 to-transparent rounded-2xl blur-xl"></div>
          <div className="relative backdrop-blur-xl bg-[#0F172A]/40 border border-[#1F2937]/50 rounded-2xl p-8 shadow-2xl">
            
            {/* Tab Selection */}
            <div className="flex gap-2 mb-8 bg-[#161E2E]/60 p-1.5 rounded-xl border border-[#1F2937]/50">
              <button
                onClick={() => { setLoginMethod('admin'); setError(''); setOtpSent(false); }}
                className={`flex-1 py-3 px-4 rounded-lg font-bold text-sm transition-all ${
                  loginMethod === 'admin'
                    ? 'bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] text-white shadow-lg'
                    : 'text-[#9CA3AF] hover:text-[#E5E7EB]'
                }`}
              >
                🔐 Admin Login
              </button>
              <button
                onClick={() => { setLoginMethod('viewer'); setError(''); setOtpSent(false); }}
                className={`flex-1 py-3 px-4 rounded-lg font-bold text-sm transition-all ${
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
              <form onSubmit={handleAdminSubmit} className="space-y-5">
                <div>
                  <label className="block text-[#E5E7EB] text-sm font-semibold mb-2">Admin Username</label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#38BDF8]" />
                    <input
                      type="text"
                      value={adminUsername}
                      onChange={(e) => setAdminUsername(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-4 py-3.5 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none transition placeholder:text-[#6B7280]"
                      placeholder="Enter admin username"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[#E5E7EB] text-sm font-semibold mb-2">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#38BDF8]" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={adminPassword}
                      onChange={(e) => setAdminPassword(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-12 py-3.5 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none transition placeholder:text-[#6B7280]"
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
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-4 py-3 rounded-xl text-sm font-medium backdrop-blur-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-[#38BDF8]/30 hover:shadow-xl hover:shadow-[#38BDF8]/40 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Signing in...' : 'Sign In as Admin'}
                </button>
              </form>
            )}

            {/* Viewer OTP Login Form */}
            {loginMethod === 'viewer' && !otpSent && (
              <form onSubmit={handleSendOTP} className="space-y-5">
                <div>
                  <label className="block text-[#E5E7EB] text-sm font-semibold mb-3">Choose Login Method</label>
                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => { setContactMethod('email'); setViewerContact(''); }}
                      className={`flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition-all border ${
                        contactMethod === 'email'
                          ? 'bg-[#22C55E]/10 border-[#22C55E]/40 text-[#22C55E]'
                          : 'bg-[#161E2E]/60 border-[#1F2937] text-[#9CA3AF] hover:border-[#22C55E]/30'
                      }`}
                    >
                      <Mail className="w-4 h-4 inline mr-2" />
                      Email
                    </button>
                    <button
                      type="button"
                      onClick={() => { setContactMethod('phone'); setViewerContact(''); }}
                      className={`flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition-all border ${
                        contactMethod === 'phone'
                          ? 'bg-[#22C55E]/10 border-[#22C55E]/40 text-[#22C55E]'
                          : 'bg-[#161E2E]/60 border-[#1F2937] text-[#9CA3AF] hover:border-[#22C55E]/30'
                      }`}
                    >
                      <Phone className="w-4 h-4 inline mr-2" />
                      Phone
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-[#E5E7EB] text-sm font-semibold mb-2">
                    {contactMethod === 'email' ? 'Email Address' : 'Phone Number'}
                  </label>
                  <div className="relative">
                    {contactMethod === 'email' ? (
                      <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#22C55E]" />
                    ) : (
                      <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#22C55E]" />
                    )}
                    <input
                      type={contactMethod === 'email' ? 'email' : 'tel'}
                      value={viewerContact}
                      onChange={(e) => setViewerContact(e.target.value)}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-4 py-3.5 focus:ring-2 focus:ring-[#22C55E] focus:border-transparent outline-none transition placeholder:text-[#6B7280]"
                      placeholder={contactMethod === 'email' ? 'Enter your email' : 'Enter your phone number'}
                      required
                    />
                  </div>
                </div>

                {error && (
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-4 py-3 rounded-xl text-sm font-medium backdrop-blur-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-[#22C55E] to-[#10B981] hover:from-[#10B981] hover:to-[#22C55E] text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-[#22C55E]/30 hover:shadow-xl hover:shadow-[#22C55E]/40 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Sending OTP...' : 'Send OTP'}
                </button>
              </form>
            )}

            {/* OTP Verification Form */}
            {loginMethod === 'viewer' && otpSent && (
              <form onSubmit={handleVerifyOTP} className="space-y-5">
                <div className="bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] px-4 py-3 rounded-xl text-sm font-medium backdrop-blur-sm mb-4">
                  ✓ OTP sent to {viewerContact}
                </div>

                <div>
                  <label className="block text-[#E5E7EB] text-sm font-semibold mb-2">Enter OTP</label>
                  <div className="relative">
                    <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#22C55E]" />
                    <input
                      type="text"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      className="w-full bg-[#161E2E]/60 backdrop-blur-sm border border-[#1F2937] text-[#E5E7EB] rounded-xl pl-12 pr-4 py-3.5 focus:ring-2 focus:ring-[#22C55E] focus:border-transparent outline-none transition placeholder:text-[#6B7280] text-center text-2xl tracking-widest font-bold"
                      placeholder="000000"
                      maxLength={6}
                      required
                    />
                  </div>
                  <p className="text-[#6B7280] text-xs mt-2 text-center">Demo OTP: <span className="text-[#22C55E] font-mono">123456</span></p>
                </div>

                {error && (
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-4 py-3 rounded-xl text-sm font-medium backdrop-blur-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-[#22C55E] to-[#10B981] hover:from-[#10B981] hover:to-[#22C55E] text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-[#22C55E]/30 hover:shadow-xl hover:shadow-[#22C55E]/40 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Verifying...' : 'Verify & Login'}
                </button>

                <button
                  type="button"
                  onClick={() => { setOtpSent(false); setOtp(''); setError(''); }}
                  className="w-full text-[#9CA3AF] hover:text-[#E5E7EB] text-sm font-medium transition"
                >
                  ← Back to {contactMethod} entry
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-[#6B7280] text-xs mt-6 font-medium">
          © 2025 EvaraTech Pvt Ltd
        </p>
      </div>
    </div>
  );
};

export default Login;
