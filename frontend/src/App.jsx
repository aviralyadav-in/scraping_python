import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Deals from "./pages/Deals";
import Scraping from "./pages/Scraping";
import Jobs from "./pages/Jobs";
import Statistics from "./pages/Statistics";
import Duplicates from "./pages/Duplicates";
import Logs from "./pages/Logs";
import Users from "./pages/Users";

import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [token, setToken] = useState(
    localStorage.getItem("token")
  );

  const [currentUser, setCurrentUser] = useState(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);

  // ==========================================
  // CHECK EXISTING LOGIN
  // ==========================================

  useEffect(() => {
    const checkLogin = async () => {
      const savedToken = localStorage.getItem("token");

      if (!savedToken) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(
          `${API_URL}/api/auth/me/`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${savedToken}`,
            },
          }
        );

        if (!response.ok) {
          localStorage.removeItem("token");

          setToken(null);
          setCurrentUser(null);

          setLoading(false);

          return;
        }

        const user = await response.json();

        setToken(savedToken);
        setCurrentUser(user);

        // Always start from dashboard
        setActivePage("dashboard");
      } catch (error) {
        console.error(
          "Authentication check failed:",
          error
        );

        localStorage.removeItem("token");

        setToken(null);
        setCurrentUser(null);
      }

      setLoading(false);
    };

    checkLogin();
  }, []);

  // ==========================================
  // LOGIN
  // ==========================================

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email.trim() || !password.trim()) {
      alert("Email and password are required");
      return;
    }

    setLoginLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/auth/login/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || "Login failed");

        setLoginLoading(false);

        return;
      }

      // Save token
      localStorage.setItem(
        "token",
        data.token
      );

      setToken(data.token);

      setCurrentUser(data.user);

      // Always open dashboard after login
      setActivePage("dashboard");

      setEmail("");
      setPassword("");
    } catch (error) {
      console.error(
        "Login error:",
        error
      );

      alert(
        "Unable to connect to server"
      );
    }

    setLoginLoading(false);
  };

  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = async () => {
    const savedToken =
      localStorage.getItem("token");

    try {
      if (savedToken) {
        await fetch(
          `${API_URL}/api/auth/logout/`,
          {
            method: "POST",

            headers: {
              Authorization: `Bearer ${savedToken}`,
            },
          }
        );
      }
    } catch (error) {
      console.error(
        "Logout error:",
        error
      );
    }

    localStorage.removeItem("token");

    setToken(null);

    setCurrentUser(null);

    setActivePage("dashboard");
  };

  // ==========================================
  // PAGE ACCESS CONTROL
  // ==========================================

  const adminPages = [
    "scraping",
    "jobs",
    "statistics",
    "duplicates",
    "logs",
    "users",
  ];

  const userPages = [
    "dashboard",
    "deals",
    "duplicates",
  ];

  const handlePageChange = (page) => {
    // If normal user tries to open
    // an admin-only page
    if (
      currentUser?.role !== "admin" &&
      adminPages.includes(page)
    ) {
      setActivePage("dashboard");
      return;
    }

    setActivePage(page);
  };

  // ==========================================
  // RENDER PAGE
  // ==========================================

  const renderPage = () => {
    // Extra security:
    // Normal user can NEVER render admin pages

    if (
      currentUser?.role !== "admin" &&
      adminPages.includes(activePage)
    ) {
      return <Dashboard />;
    }

    switch (activePage) {
      case "dashboard":
        return <Dashboard />;

      case "deals":
        return (
          <Deals
            currentUser={currentUser}
          />
        );

      case "duplicates":
        return <Duplicates />;

      // ADMIN ONLY

      case "scraping":
        return <Scraping />;

      case "jobs":
        return <Jobs />;

      case "statistics":
        return <Statistics />;

      case "logs":
        return <Logs />;

      case "users":
        return <Users />;

      default:
        return <Dashboard />;
    }
  };

  // ==========================================
  // LOADING SCREEN
  // ==========================================

  if (loading) {
    return (
      <div className="app-layout">
        <main className="main-content">
          <div className="loading-screen">
            <div className="loading-spinner"></div>

            <h2>Loading...</h2>

            <p>
              Checking your account...
            </p>
          </div>
        </main>
      </div>
    );
  }

  // ==========================================
  // LOGIN SCREEN
  // ONLY LOGIN UI UPDATED
  // ==========================================

  if (!token || !currentUser) {
    return (
      <div className="login-page">

        <div className="login-background">

          {/* Decorative background elements */}

          <div className="login-glow login-glow-one"></div>

          <div className="login-glow login-glow-two"></div>

          <div className="login-card">

            {/* BRAND */}

            <div className="login-brand">

              <div className="login-logo">
                TD
              </div>

              <div className="login-brand-text">

                <h1>
                  Telegram Deals
                </h1>

                <p>
                  Scraper Dashboard
                </p>

              </div>

            </div>

            {/* DIVIDER */}

            <div className="login-divider"></div>

            {/* HEADING */}

            <div className="login-heading">

              <span className="login-welcome">
                Welcome back
              </span>

              <h2>
                Sign in to your account
              </h2>

              <p>
                Enter your credentials to
                continue to the dashboard.
              </p>

            </div>

            {/* FORM */}

            <form
              onSubmit={handleLogin}
              className="login-form"
            >

              {/* EMAIL */}

              <div className="login-field">

                <label>
                  Email Address
                </label>

                <div className="input-wrapper">

                  <span className="input-icon">
                    @
                  </span>

                  <input
                    type="email"
                    value={email}
                    onChange={(e) =>
                      setEmail(
                        e.target.value
                      )
                    }
                    placeholder="Enter your email"
                    autoComplete="email"
                  />

                </div>

              </div>

              {/* PASSWORD */}

              <div className="login-field">

                <label>
                  Password
                </label>

                <div className="input-wrapper">

                  <span className="input-icon">
                    •
                  </span>

                  <input
                    type="password"
                    value={password}
                    onChange={(e) =>
                      setPassword(
                        e.target.value
                      )
                    }
                    placeholder="Enter your password"
                    autoComplete="current-password"
                  />

                </div>

              </div>

              {/* LOGIN BUTTON */}

              <button
                type="submit"
                className="login-button"
                disabled={loginLoading}
              >
                {loginLoading ? (
                  <>
                    <span className="button-spinner"></span>

                    Signing in...
                  </>
                ) : (
                  <>
                    <span>
                      Sign In
                    </span>

                    <span className="login-arrow">
                      →
                    </span>
                  </>
                )}
              </button>

            </form>

            {/* SECURITY INFO */}

            <div className="login-security">

              <span className="security-icon">
                ✓
              </span>

              <div>
                <strong>
                  Secure Login
                </strong>

                <p>
                  Your account information
                  is protected.
                </p>
              </div>

            </div>

            {/* FOOTER */}

            <div className="login-footer">

              <span>
                © 2026 Telegram Deals
              </span>

              <span>
                •
              </span>

              <span>
                Secure Management System
              </span>

            </div>

          </div>

        </div>

      </div>
    );
  }

  // ==========================================
  // MAIN APPLICATION
  // ==========================================

  return (
    <div className="app-layout">

      <Sidebar
        activePage={activePage}
        setActivePage={handlePageChange}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      <main className="main-content">

        {renderPage()}

      </main>

    </div>
  );
}

export default App;