'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { 
  Session, 
  User, 
  Provider,
  UserResponse,
  AuthError,
  AuthTokenResponse,
  MFAEnrollResponse
} from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';

type MFAState = {
  isEnrolled: boolean;
  needsTotp: boolean;
  factorId?: string;
  qrCode?: string;
  secret?: string;
};

type AuthContextType = {
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  isAdmin: boolean;
  signUp: (email: string, password: string) => Promise<UserResponse>;
  signIn: (email: string, password: string) => Promise<AuthTokenResponse>;
  signInWithProvider: (provider: Provider) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updatePassword: (password: string) => Promise<{ error: AuthError | null }>;
  
  // MFA related functions
  mfa: MFAState;
  enrollMFA: () => Promise<MFAEnrollResponse>;
  verifyMFA: (code: string) => Promise<{ error: AuthError | null }>;
  unenrollMFA: () => Promise<{ error: AuthError | null }>;
  verifyTOTP: (code: string, factorId: string) => Promise<AuthTokenResponse>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mfa, setMfa] = useState<MFAState>({
    isEnrolled: false,
    needsTotp: false,
  });

  // Check if user is admin
  const isAdmin = user?.app_metadata?.role === 'admin';

  useEffect(() => {
    // Get initial session and set up listener
    const getInitialSession = async () => {
      setIsLoading(true);
      
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setSession(session);
        setUser(session?.user ?? null);
        
        // Check if MFA is enrolled
        if (session?.user) {
          const { data, error } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
          
          if (data) {
            setMfa({
              ...mfa,
              isEnrolled: data.currentLevel === 'aal2'
            });
          }
        }
      } catch (error) {
        console.error('Error getting initial session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    getInitialSession();

    // Set up auth state change listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, newSession) => {
        setSession(newSession);
        setUser(newSession?.user ?? null);
        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Sign up a new user
  const signUp = async (email: string, password: string) => {
    return await supabase.auth.signUp({
      email,
      password,
    });
  };

  // Sign in an existing user
  const signIn = async (email: string, password: string) => {
    const response = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    
    // Check if MFA verification is required
    if (response.error?.message.includes('factors')) {
      const { data } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
      
      if (data) {
        setMfa({
          ...mfa,
          needsTotp: true,
          factorId: data.nextLevel?.factors?.[0].id
        });
      }
    }
    
    return response;
  };

  // Sign in with a third-party provider
  const signInWithProvider = async (provider: Provider) => {
    await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
  };

  // Sign out
  const signOut = async () => {
    await supabase.auth.signOut();
  };

  // Reset password
  const resetPassword = async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });
    return { error };
  };

  // Update password
  const updatePassword = async (password: string) => {
    const { error } = await supabase.auth.updateUser({
      password,
    });
    return { error };
  };

  // Enroll in MFA (TOTP)
  const enrollMFA = async () => {
    const response = await supabase.auth.mfa.enroll({
      factorType: 'totp',
    });
    
    if (response.data) {
      setMfa({
        ...mfa,
        qrCode: response.data.totp.qr_code,
        secret: response.data.totp.secret,
      });
    }
    
    return response;
  };

  // Verify MFA enrollment
  const verifyMFA = async (code: string) => {
    if (!mfa.secret) {
      return { error: new Error('MFA not initialized') as unknown as AuthError };
    }
    
    const { error } = await supabase.auth.mfa.challengeAndVerify({
      factorId: mfa.factorId || '',
      code,
    });
    
    if (!error) {
      setMfa({
        ...mfa,
        isEnrolled: true,
        needsTotp: false,
        qrCode: undefined,
        secret: undefined,
      });
    }
    
    return { error };
  };

  // Unenroll from MFA
  const unenrollMFA = async () => {
    if (!mfa.factorId) {
      return { error: new Error('No MFA factor to unenroll') as unknown as AuthError };
    }
    
    const { error } = await supabase.auth.mfa.unenroll({
      factorId: mfa.factorId,
    });
    
    if (!error) {
      setMfa({
        isEnrolled: false,
        needsTotp: false,
        factorId: undefined,
      });
    }
    
    return { error };
  };

  // Verify TOTP during login
  const verifyTOTP = async (code: string, factorId: string) => {
    const response = await supabase.auth.mfa.verifyTotp({
      factorId,
      code,
    });
    
    if (!response.error) {
      setMfa({
        ...mfa,
        needsTotp: false,
      });
    }
    
    return response;
  };

  const value = {
    session,
    user,
    isLoading,
    isAdmin,
    signUp,
    signIn,
    signInWithProvider,
    signOut,
    resetPassword,
    updatePassword,
    mfa,
    enrollMFA,
    verifyMFA,
    unenrollMFA,
    verifyTOTP,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 