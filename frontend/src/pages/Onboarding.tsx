import React, { useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

const Onboarding: React.FC = () => {
  const { user, isSignedIn } = useUser();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState<string>('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isSignedIn) return;

    const created = user?.createdAt ? new Date(user.createdAt).getTime() : 0;
    const last = user?.lastSignInAt ? new Date(user.lastSignInAt).getTime() : 0;
    const isFirstTime = last === 0 || Math.abs((last || 0) - (created || 0)) < 1000;

    if (!isFirstTime) {
      navigate('/dashboard', { replace: true });
    }
  }, [isSignedIn, user, navigate]);

  const handleContinue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setSaving(true);
    try {
      if (fullName.trim()) {
        await user.update({ firstName: fullName.split(' ')[0], lastName: fullName.split(' ').slice(1).join(' ') });
      }
      await user.update({ publicMetadata: { onboarded: true } });
      navigate('/dashboard', { replace: true });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="w-full max-w-xl relative">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-black bg-gradient-to-r from-[#38BDF8] via-[#0EA5E9] to-[#38BDF8] bg-clip-text text-transparent">Welcome to EvaraTDS</h2>
          <p className="text-[#9CA3AF] mt-2">Let’s personalize your dashboard.</p>
        </div>
        <form onSubmit={handleContinue} className="space-y-5 backdrop-blur-xl bg-[#0F172A]/40 border border-[#1F2937]/50 rounded-2xl p-6">
          <div>
            <label className="block text-[#E5E7EB] text-sm font-semibold mb-2">Your Name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder={user?.fullName || 'Enter your full name'}
              className="w-full bg-[#161E2E]/60 border border-[#1F2937] text-[#E5E7EB] rounded-xl px-4 py-3.5 focus:ring-2 focus:ring-[#38BDF8] focus:border-transparent outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-bold py-3.5 rounded-xl disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Continue to Dashboard'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Onboarding;
