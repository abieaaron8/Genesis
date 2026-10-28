import { AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { Link, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { usePopper } from "react-popper";

import Home from "./pages/Home";
import History from "./pages/History";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Register from "./pages/Register";
import Stats from "./pages/Stats";
import { getMe, setAuthToken } from "./services/api";
import "./App.css";

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const isAuthRoute = location.pathname === "/login" || location.pathname === "/register";
  const theme = "light";
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [profileOpen, setProfileOpen] = useState(false);

  const [referenceElement, setReferenceElement] = useState(null);
  const [popperElement, setPopperElement] = useState(null);
  const { styles, attributes } = usePopper(referenceElement, popperElement, {
    placement: "bottom-end",
    modifiers: [
      {
        name: "offset",
        options: {
          offset: [0, 10],
        },
      },
    ],
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("veritas-theme", theme);
  }, [theme]);

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem("veritas-token");
      if (!token) {
        setCurrentUser(null);
        setAuthToken(null);
        setLoadingUser(false);
        return;
      }

      try {
        setAuthToken(token);
        const me = await getMe();
        setCurrentUser(me);
      } catch {
        localStorage.removeItem("veritas-token");
        setAuthToken(null);
        setCurrentUser(null);
      } finally {
        setLoadingUser(false);
      }
    };

    loadUser();
    setProfileOpen(false);
  }, [location.pathname]);

  const initials = useMemo(() => {
    if (!currentUser?.username) return "U";
    return currentUser.username.slice(0, 2).toUpperCase();
  }, [currentUser]);

  const logout = () => {
    localStorage.removeItem("veritas-token");
    setAuthToken(null);
    setCurrentUser(null);
    setProfileOpen(false);
    navigate("/login");
  };

  return (
    <div className={`app-shell ${isAuthRoute ? "auth-layout" : ""}`}>
      {!isAuthRoute && (
        <header className="top-nav">
          <h1>Genesis</h1>
          <nav>
            <Link to="/" className={`nav-link-btn nav-home ${location.pathname === "/" ? "active" : ""}`}>Verify</Link>
            <Link to="/history" className={`nav-link-btn nav-history ${location.pathname === "/history" ? "active" : ""}`}>History</Link>
            <Link to="/stats" className={`nav-link-btn nav-stats ${location.pathname === "/stats" ? "active" : ""}`}>Stats</Link>

            {!loadingUser && !currentUser && (
              <>
                <Link to="/login" className={`nav-link-btn ${location.pathname === "/login" ? "active" : ""}`}>Login</Link>
                <Link to="/register" className={`nav-link-btn ${location.pathname === "/register" ? "active" : ""}`}>Sign up</Link>
              </>
            )}

            {!loadingUser && currentUser && (
              <div className="profile-menu-wrap">
                <button
                  ref={setReferenceElement}
                  className="profile-chip" 
                  onClick={() => setProfileOpen((v) => !v)}
                >
                  <span className="profile-avatar">{initials}</span>
                  <span className="profile-name">{currentUser.username}</span>
                </button>
                
                <AnimatePresence>
                  {profileOpen && (
                    <div
                      ref={setPopperElement}
                      style={styles.popper}
                      {...attributes.popper}
                      className="profile-menu"
                    >
                      <p className="profile-email">{currentUser.email}</p>
                      <Link to="/profile" className="menu-link">
                        View Profile
                      </Link>
                      <button className="menu-link logout-btn" onClick={logout}>
                        Logout
                      </button>
                    </div>
                  )}
                </AnimatePresence>
              </div>
            )}

          </nav>
        </header>
      )}

      <div className="page-transition-wrapper">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
            <Route path="/stats" element={<Stats />} />
            <Route path="/login" element={currentUser ? <Navigate to="/" replace /> : <Login />} />
            <Route path="/register" element={currentUser ? <Navigate to="/" replace /> : <Register />} />
            <Route path="/profile" element={currentUser ? <Profile user={currentUser} onLogout={logout} /> : <Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
