import React, { createContext, useContext, ReactNode } from 'react';
import { ApiClient } from './api-client';

// Create a singleton instance of the API client
const apiClient = new ApiClient('/api');

// Create the context
const ApiContext = createContext<ApiClient | undefined>(undefined);

// Provider component
interface ApiProviderProps {
  children: ReactNode;
}

export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  return (
    <ApiContext.Provider value={apiClient}>
      {children}
    </ApiContext.Provider>
  );
};

// Hook to use the API context
export const useApi = (): ApiClient => {
  const context = useContext(ApiContext);
  
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  
  return context;
}; 