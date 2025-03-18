'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useAuth } from '@/contexts/AuthContext';

export function MfaSetup() {
  const { mfa, enrollMFA, verifyMFA } = useAuth();
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Start MFA enrollment
  const handleStartEnrollment = async () => {
    setIsEnrolling(true);
    setError(null);
    
    try {
      const response = await enrollMFA();
      if (response.error) {
        setError(response.error.message);
        setIsEnrolling(false);
      }
    } catch (err) {
      setError('Failed to start MFA enrollment. Please try again.');
      setIsEnrolling(false);
    }
  };

  // Verify the TOTP code
  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsVerifying(true);
    setError(null);
    
    try {
      const { error } = await verifyMFA(verificationCode);
      
      if (error) {
        setError(error.message);
      } else {
        setSuccess(true);
        // Clear sensitive data
        setVerificationCode('');
      }
    } catch (err) {
      setError('Failed to verify the code. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  if (success) {
    return (
      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <div className="flex flex-col items-center space-y-4 text-center">
          <div className="rounded-full bg-green-100 p-3">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              className="h-6 w-6 text-green-600"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <h2 className="text-xl font-semibold">MFA Setup Complete</h2>
          <p className="text-muted-foreground">
            Your account is now protected with multi-factor authentication.
          </p>
        </div>
      </div>
    );
  }

  if (mfa.isEnrolled) {
    return (
      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <div className="flex flex-col space-y-4">
          <h2 className="text-xl font-semibold">MFA Already Enabled</h2>
          <p className="text-muted-foreground">
            Your account is already protected with multi-factor authentication.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <div className="flex flex-col space-y-4">
        <h2 className="text-xl font-semibold">Enable Two-Factor Authentication</h2>
        <p className="text-muted-foreground">
          Protect your account with Time-based One-Time Password (TOTP) authentication.
        </p>

        {error && (
          <div className="rounded-md bg-destructive/15 p-3 text-destructive">
            {error}
          </div>
        )}

        {!isEnrolling && (
          <button
            onClick={handleStartEnrollment}
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            Enable MFA
          </button>
        )}

        {isEnrolling && mfa.qrCode && (
          <div className="space-y-6">
            <div className="flex flex-col items-center space-y-4">
              <div className="rounded-lg border bg-muted p-2">
                {/* Using an img tag directly for the QR code since it's a data URL */}
                <img 
                  src={mfa.qrCode} 
                  alt="QR Code for TOTP" 
                  width={200} 
                  height={200} 
                />
              </div>
              
              {mfa.secret && (
                <div className="w-full max-w-xs overflow-x-auto rounded-md bg-muted p-2 text-center font-mono text-sm">
                  {mfa.secret}
                </div>
              )}
              
              <p className="text-sm text-muted-foreground">
                Scan this QR code or enter the secret key manually in your authenticator app.
              </p>
            </div>

            <div className="space-y-2">
              <label htmlFor="verificationCode" className="block text-sm font-medium">
                Verification Code
              </label>
              <input
                id="verificationCode"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                pattern="[0-9]*"
                maxLength={6}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Enter 6-digit code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/[^0-9]/g, ''))}
              />
              <p className="text-xs text-muted-foreground">
                Enter the 6-digit code from your authenticator app to verify setup.
              </p>
            </div>

            <button
              onClick={handleVerify}
              disabled={isVerifying || verificationCode.length !== 6}
              className="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isVerifying ? 'Verifying...' : 'Verify & Enable'}
            </button>
          </div>
        )}

        <div className="space-y-2 rounded-md bg-muted p-4">
          <h3 className="font-medium">Recommended Authenticator Apps</h3>
          <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
            <li>Google Authenticator</li>
            <li>Microsoft Authenticator</li>
            <li>Authy</li>
            <li>1Password</li>
            <li>Any app supporting TOTP (RFC 6238)</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 