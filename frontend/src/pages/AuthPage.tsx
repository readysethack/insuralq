import React, { useState } from "react";
import AuthForm from "../components/Auth/AuthForm";

const AuthPage: React.FC = () => {
  const [mode, setMode] = useState<"login" | "signup">("login");

  const handleAuth = (
    role: "customer" | "investigator",
    email: string,
    password: string
  ) => {
    // Simulate authentication and store session
    localStorage.setItem("session", JSON.stringify({ role, email }));
    window.location.href = role === "customer" ? "/customer" : "/investigator";
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md">
        <AuthForm mode={mode} onAuth={handleAuth} />
        <div className="text-center mt-4">
          {mode === "login" ? (
            <span>
              Don&apos;t have an account?{" "}
              <button
                className="text-blue-600 font-semibold hover:underline"
                onClick={() => setMode("signup")}
              >
                Sign Up
              </button>
            </span>
          ) : (
            <span>
              Already have an account?{" "}
              <button
                className="text-blue-600 font-semibold hover:underline"
                onClick={() => setMode("login")}
              >
                Login
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
