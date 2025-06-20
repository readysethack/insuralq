import React, { createContext, useContext, useEffect, useState } from "react";

type Role = "customer" | "investigator";
interface User {
  email: string;
  role: Role;
}

interface AuthContextType {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const session = localStorage.getItem("session");
    if (session) {
      setUser(JSON.parse(session));
    }
  }, []);

  const login = (user: User) => {
    setUser(user);
    localStorage.setItem("session", JSON.stringify(user));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("session");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
