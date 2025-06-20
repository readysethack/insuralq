import React, { useState } from "react";

type AuthMode = "login" | "signup";
type Role = "customer" | "investigator";

interface AuthFormProps {
  mode: AuthMode;
  onAuth: (role: Role, email: string, password: string) => void;
}

const demo = { email: "demo@example.com", password: "demo123" };

const AuthForm: React.FC<AuthFormProps> = ({ mode, onAuth }) => {
  const [role, setRole] = useState<Role>("customer");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onAuth(role, email, password);
    }, 800);
  };

  const autofillDemo = () => {
    setEmail(demo.email);
    setPassword(demo.password);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white dark:bg-gray-900 rounded-xl shadow-lg p-8 w-full max-w-md mx-auto flex flex-col gap-6"
    >
      <h2 className="text-2xl font-bold text-center mb-2 text-blue-700 dark:text-blue-200">
        {mode === "login" ? "Login" : "Sign Up"}
      </h2>
      <div className="flex gap-4 justify-center mb-2">
        <button
          type="button"
          onClick={() => setRole("customer")}
          className={`px-4 py-2 rounded-lg font-semibold transition ${
            role === "customer"
              ? "bg-blue-600 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
          }`}
        >
          Customer
        </button>
        <button
          type="button"
          onClick={() => setRole("investigator")}
          className={`px-4 py-2 rounded-lg font-semibold transition ${
            role === "investigator"
              ? "bg-purple-600 text-white"
              : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
          }`}
        >
          Investigator
        </button>
      </div>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        autoComplete="email"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        autoComplete="current-password"
      />
      {error && <div className="text-red-500 text-center">{error}</div>}
      <button
        type="submit"
        className="w-full py-3 rounded-lg bg-blue-600 text-white font-bold hover:bg-blue-700 transition disabled:opacity-60"
        disabled={loading}
      >
        {loading ? "Please wait..." : mode === "login" ? "Login" : "Sign Up"}
      </button>
      <button
        type="button"
        onClick={autofillDemo}
        className="w-full py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-200 dark:hover:bg-gray-700 transition"
      >
        Use Demo Credentials
      </button>
    </form>
  );
};

export default AuthForm;
