import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import api from "../utils/api";

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, refCode?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api.get("/profile/me")
        .then((res) => {
          // Derive user info from profile endpoint or store from login
          const stored = localStorage.getItem("user");
          if (stored) setUser(JSON.parse(stored));
        })
        .catch(() => {
          localStorage.clear();
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    // Decode user from token (basic info) — fetch profile separately
    const payload = JSON.parse(atob(data.access_token.split(".")[1]));
    const u = { id: payload.sub, email, role: "user" };
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);
  };

  const register = async (email: string, password: string, fullName: string, refCode?: string) => {
    const { data } = await api.post("/auth/register", {
      email,
      password,
      full_name: fullName,
      ref_code: refCode,
    });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    const payload = JSON.parse(atob(data.access_token.split(".")[1]));
    const u = { id: payload.sub, email, role: "user" };
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);
  };

  const logout = () => {
    api.post("/auth/logout").catch(() => {});
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
