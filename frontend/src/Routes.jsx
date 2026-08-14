import { Navigate, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Deals from "./pages/Deals";
import Duplicates from "./pages/Duplicates";
import Scraping from "./pages/Scraping";
import Jobs from "./pages/Jobs";
import Statistics from "./pages/Statistics";
import Logs from "./pages/Logs";
import Users from "./pages/Users";

function ProtectedRoute({ currentUser, children, adminOnly = false }) {
  if (!currentUser) {
    return <Navigate to="/" replace />;
  }

  if (adminOnly && currentUser.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function AppRoutes({ currentUser }) {
  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to="/dashboard" replace />}
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute currentUser={currentUser}>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/deals"
        element={
          <ProtectedRoute currentUser={currentUser}>
            <Deals currentUser={currentUser} />
          </ProtectedRoute>
        }
      />

      <Route
        path="/duplicates"
        element={
          <ProtectedRoute currentUser={currentUser}>
            <Duplicates />
          </ProtectedRoute>
        }
      />

      {/* ADMIN ONLY */}

      <Route
        path="/scraping"
        element={
          <ProtectedRoute
            currentUser={currentUser}
            adminOnly
          >
            <Scraping />
          </ProtectedRoute>
        }
      />

      <Route
        path="/jobs"
        element={
          <ProtectedRoute
            currentUser={currentUser}
            adminOnly
          >
            <Jobs />
          </ProtectedRoute>
        }
      />

      <Route
        path="/statistics"
        element={
          <ProtectedRoute
            currentUser={currentUser}
            adminOnly
          >
            <Statistics />
          </ProtectedRoute>
        }
      />

      <Route
        path="/logs"
        element={
          <ProtectedRoute
            currentUser={currentUser}
            adminOnly
          >
            <Logs />
          </ProtectedRoute>
        }
      />

      <Route
        path="/users"
        element={
          <ProtectedRoute
            currentUser={currentUser}
            adminOnly
          >
            <Users />
          </ProtectedRoute>
        }
      />

      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}

export default AppRoutes;