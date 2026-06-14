import { createContext, useContext, useState, useEffect } from 'react';
import { signUpUser, loginUser, logoutUser, resetPassword, getStoredUser } from '../firebase/auth';

const AuthContext = createContext(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) {
      setUser(stored);
    }
    setLoading(false);
  }, []);

  const signup = async (email, password, profileData) => {
    const userData = await signUpUser(email, password, profileData);
    setUser(userData);
    return userData;
  };

  const login = async (email, password) => {
    const userData = await loginUser(email, password);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    await logoutUser();
    setUser(null);
  };

  const forgotPassword = async (email) => {
    await resetPassword(email);
  };

  const value = {
    user,
    loading,
    signup,
    login,
    logout,
    forgotPassword,
    isTeacher: user?.role === 'teacher',
    isStudent: user?.role === 'student',
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
