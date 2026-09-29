import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { User } from "../types";
import { fetchMe, login as loginRequest, logout as logoutRequest, register as registerRequest } from "../api/auth";
import { getToken, clearToken } from "../api/client";

interface AuthContextValue {
  user: User | null;
  initializing: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      setInitializing(false);
      return;
    }

    fetchMe()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setInitializing(false));
  }, []);

  const value = useMemo<AuthContextValue>(() => {
    return {
      user,
      initializing,
      login: async (email: string, password: string) => {
        await loginRequest(email, password);
        const me = await fetchMe();
        setUser(me);
      },
      register: async (email: string, password: string) => {
        await registerRequest(email, password);
        await loginRequest(email, password);
        const me = await fetchMe();
        setUser(me);
      },
      logout: () => {
        logoutRequest();
        setUser(null);
      }
    };
  }, [user, initializing]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
