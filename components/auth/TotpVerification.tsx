'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface TotpVerificationProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export function TotpVerification({ onSuccess, onCancel }: TotpVerificationProps) {
  const { mfa, verifyTOTP } = useAuth();
  const [verificationCode, setVerificationCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsVerifying(true);
    setError(null);
    
    try {
      if (!mfa.factorId) {
        setError('MFA session not initialized properly. Please try logging in again.');
        return;
      }
      
      const response = await verifyTOTP(verificationCode, mfa.factorId);
      
      if (response.error) {
        setError(response.error.message);
      } else {
        // MFA verification successful
        setVerificationCode(''); // Clear sensitive data
        onSuccess();
      }
    } catch (err) {
      setError('Failed to verify the code. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <div className="flex flex-col space-y-4">
        <h2 className="text-xl font-semibold">Two-Factor Authentication</h2>
        <p className="text-muted-foreground">
          Enter the 6-digit code from your authenticator app to verify your identity.
        </p>

        {error && (
          <div className="rounded-md bg-destructive/15 p-3 text-destructive">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <label htmlFor="totpCode" className="block text-sm font-medium">
            Authentication Code
          </label>
          <input
            id="totpCode"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            pattern="[0-9]*"
            maxLength={6}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            placeholder="Enter 6-digit code"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/[^0-9]/g, ''))}
            autoFocus
          />
        </div>

        <div className="flex justify-between gap-2">
          <button
            onClick={onCancel}
            className="inline-flex h-10 flex-1 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-muted-foreground ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            Cancel
          </button>
          <button
            onClick={handleVerify}
            disabled={isVerifying || verificationCode.length !== 6}
            className="inline-flex h-10 flex-1 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isVerifying ? 'Verifying...' : 'Verify'}
          </button>
        </div>

        <div className="text-center text-sm text-muted-foreground">
          <p>Don't have access to your authenticator app?</p>
          <button className="text-primary hover:underline" onClick={() => alert('Contact your administrator for recovery options')}>
            Use a recovery option
          </button>
        </div>
      </div>
    </div>
  );
} 