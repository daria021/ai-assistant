// src/contexts/auth.tsx
import { createContext, useContext, useEffect, useState } from 'react';
import { apiClient } from '../services/apiClient';
import { getMe } from '../services/api';
import { initData } from '@telegram-apps/sdk';
import type { UserRole } from '../types/UserRole';

interface AuthContextType {
  userId: string | null;
  role: UserRole | null;
  isBanned: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userId, setUserId] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [isBanned, setIsBanned] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const authenticateUser = async () => {
      initData.restore();
      const data = initData.raw();
      if (!data) {
        setLoading(false);
        return;
      }
      try {
        const { data: auth } = await apiClient.post('/auth/telegram', { initData: data });
        localStorage.setItem('authToken', auth.access_token);
        localStorage.setItem('refreshToken', auth.refresh_token);
        apiClient.defaults.headers.common.Authorization = `Bearer ${auth.access_token}`;

        const me = await getMe();
        setUserId(me.id);
        setRole(me.role);
        // Обратите внимание: поле из API должно точно совпадать.
        // Часто оно называется is_banned, но в JS удобнее — isBanned.
        setIsBanned(!!me.is_banned);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    authenticateUser();
  }, []);
  console.log('AuthContext:', { userId, role, isBanned, loading });

  return (
    <AuthContext.Provider value={{ userId, role, isBanned, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
