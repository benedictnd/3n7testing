'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { cn } from '../../lib/utils';

type ToastType = 'success' | 'error' | 'info' | 'warning';
type ToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (message: string, type: ToastType, duration?: number) => void;
  removeToast: (id: string) => void;
  position: ToastPosition;
  setPosition: (position: ToastPosition) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export function ToastProvider({
  children,
  defaultPosition = 'top-right',
}: {
  children: React.ReactNode;
  defaultPosition?: ToastPosition;
}) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [position, setPosition] = useState<ToastPosition>(defaultPosition);

  const addToast = (message: string, type: ToastType = 'info', duration = 5000) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { id, message, type, duration };
    setToasts((prev) => [...prev, newToast]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, position, setPosition }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

function ToastContainer() {
  const { toasts, removeToast, position } = useToast();

  let positionClasses = '';
  switch (position) {
    case 'top-right':
      positionClasses = 'top-4 right-4';
      break;
    case 'top-left':
      positionClasses = 'top-4 left-4';
      break;
    case 'bottom-right':
      positionClasses = 'bottom-4 right-4';
      break;
    case 'bottom-left':
      positionClasses = 'bottom-4 left-4';
      break;
    case 'top-center':
      positionClasses = 'top-4 left-1/2 -translate-x-1/2';
      break;
    case 'bottom-center':
      positionClasses = 'bottom-4 left-1/2 -translate-x-1/2';
      break;
  }

  return (
    <div
      className={cn(
        'fixed flex flex-col gap-2 z-50 max-w-md',
        positionClasses
      )}
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  useEffect(() => {
    if (toast.duration) {
      const timer = setTimeout(() => {
        onClose();
      }, toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast, onClose]);

  let typeClasses = '';
  let icon = null;

  switch (toast.type) {
    case 'success':
      typeClasses = 'bg-green-500 text-white';
      icon = (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      );
      break;
    case 'error':
      typeClasses = 'bg-red-500 text-white';
      icon = (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
      break;
    case 'warning':
      typeClasses = 'bg-yellow-500 text-white';
      icon = (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
      break;
    case 'info':
    default:
      typeClasses = 'bg-blue-500 text-white';
      icon = (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
      break;
  }

  return (
    <div
      className={cn(
        'flex items-center rounded-lg shadow-lg overflow-hidden transition-all transform translate-y-0',
        'animate-in slide-in-from-top-5 fade-in duration-300',
        'animate-out slide-out-to-top-5 fade-out duration-200',
        typeClasses
      )}
      role="alert"
    >
      <div className="flex-shrink-0 py-4 pl-4">{icon}</div>
      <div className="p-4 mr-2 flex-1">{toast.message}</div>
      <button
        onClick={onClose}
        className="p-4 text-white hover:bg-white/10 self-start h-full focus:outline-none"
        aria-label="Close"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path
            fillRule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>
    </div>
  );
}

// Helper functions to make it easier to use toasts
export function useToasts() {
  const { addToast, removeToast } = useToast();
  
  return {
    showSuccess: (message: string, duration?: number) => 
      addToast(message, 'success', duration),
    showError: (message: string, duration?: number) => 
      addToast(message, 'error', duration),
    showWarning: (message: string, duration?: number) => 
      addToast(message, 'warning', duration),
    showInfo: (message: string, duration?: number) => 
      addToast(message, 'info', duration),
    removeToast,
  };
} 