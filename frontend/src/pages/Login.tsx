import React from 'react';
import { SignIn } from '@clerk/clerk-react';

const Login: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B0F1A] via-[#0E1627] to-[#111827] p-4 relative overflow-hidden">
      <div className="fixed top-0 left-0 w-[800px] h-[800px] bg-gradient-radial from-[#38BDF8]/10 to-transparent rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[800px] h-[800px] bg-gradient-radial from-[#0EA5E9]/8 to-transparent rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />

      <div className="w-full max-w-xl relative z-10">
        <div className="text-center mb-8">
          <div className="flex justify-center gap-6 mb-8">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-20 w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-20 w-auto object-contain" />
          </div>
          <h1 className="text-5xl md:text-6xl font-black bg-gradient-to-r from-[#38BDF8] via-[#0EA5E9] to-[#38BDF8] bg-clip-text text-transparent mb-3 leading-tight">EvaraTDS</h1>
          <p className="text-[#9CA3AF] text-base font-semibold tracking-wide">IoT Water Quality Monitoring System</p>
        </div>

        <div className="relative flex justify-center">
          <div className="absolute inset-0 bg-gradient-to-br from-[#38BDF8]/20 via-[#0EA5E9]/10 to-transparent rounded-2xl blur-xl" />
          <div className="relative backdrop-blur-xl bg-[#0F172A]/40 border border-[#1F2937]/50 rounded-2xl p-6 shadow-2xl w-full flex justify-center">
            <SignIn
              appearance={{
                elements: {
                  formButtonPrimary: 'bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-bold',
                  headerTitle: 'text-[#E5E7EB] font-black',
                  headerSubtitle: 'text-[#9CA3AF]',
                  socialButtonsBlockButton: 'border-[#1F2937] bg-[#161E2E] text-[#E5E7EB]',
                  card: 'bg-transparent shadow-none',
                  footer: 'text-[#9CA3AF]',
                  formFieldInput: 'bg-[#161E2E] border-[#1F2937] text-[#E5E7EB]'
                }
              }}
              routing="path"
              path="/login"
              signUpUrl="/login"
              afterSignInUrl="/onboarding"
              afterSignUpUrl="/onboarding"
              forceRedirectUrl="/onboarding"
              fallbackRedirectUrl="/dashboard"
            />
          </div>
        </div>

        <p className="text-center text-[#6B7280] text-xs mt-6 font-medium">© 2025 EvaraTech Pvt Ltd</p>
      </div>
    </div>
  );
};

export default Login;
