import React from "react";
import { useAuth } from "../context/AuthContext";

interface ProtectedRouteProps {
  requiredRole?: "customer" | "investigator";
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  requiredRole,
  children,
}) => {
  const { user } = useAuth();

  if (!user) {
    window.location.href = "/auth";
    return null;
  }
  if (requiredRole && user.role !== requiredRole) {
    window.location.href = "/auth";
    return null;
  }
  return <>{children}</>;
};

export default ProtectedRoute;
