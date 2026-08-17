import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import AppRoutes from "./Routes";
import ProfileMenu from "./components/ProfileMenu";

import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const [token, setToken] = useState(
    localStorage.getItem("token")
  );

  const [currentUser, setCurrentUser] = useState(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);

  useEffect(() => {
    const checkLogin = async () => {
      const savedToken =
        localStorage.getItem("token");

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

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email.trim() || !password.trim()) {
      alert(
        "Email and password are required"
      );
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
        alert(
          data.error || "Login failed"
        );

        setLoginLoading(false);
        return;
      }

      localStorage.setItem(
        "token",
        data.token
      );

      setToken(data.token);
      setCurrentUser(data.user);

      setEmail("");
      setPassword("");

      navigate("/dashboard", {
        replace: true,
      });
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
              Authorization:
                `Bearer ${savedToken}`,
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

    navigate("/", {
      replace: true,
    });
  };

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

  if (!token || !currentUser) {
    return (
      <div className="login-page">

        <div className="login-background">

          <div className="login-glow login-glow-one"></div>

          <div className="login-glow login-glow-two"></div>

          <div className="login-card">

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

            <div className="login-divider"></div>

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

            <form
              onSubmit={handleLogin}
              className="login-form"
            >

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

  const isProfilePage =
    location.pathname === "/profile";

  if (isProfilePage) {
    return (
      <div className="profile-route">
        <AppRoutes
          currentUser={currentUser}
        />
      </div>
    );
  }

  return (
    <div className="app-layout">

      <Sidebar
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      <main className="main-content">

        <div className="top-header">

          <ProfileMenu
            currentUser={currentUser}
            onLogout={handleLogout}
          />

        </div>

        <AppRoutes
          currentUser={currentUser}
        />

      </main>

    </div>
  );
}

export default App;