import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import CustomerChatPage from "./pages/CustomerChatPage";
import InvestigatorDashboardPage from "./pages/InvestigatorDashboardPage";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./routes/ProtectedRoute";

const App: React.FC = () => (
  <AuthProvider>
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route
          path="/customer"
          element={
            <ProtectedRoute requiredRole="customer">
              <CustomerChatPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/investigator"
          element={
            <ProtectedRoute requiredRole="investigator">
              <InvestigatorDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  </AuthProvider>
);

export default App;
