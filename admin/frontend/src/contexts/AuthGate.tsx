import React from 'react';
import { useAuth } from './auth';

export const AuthGate: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { loading } = useAuth();

  if (loading) return <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="h-10 w-10 rounded-full border-4 border-gray-300 border-t-gray-600 always-spin" />
      </div>;    // пока токен получаем — просто крутим лоадер
  return <>{children}</>;
};
