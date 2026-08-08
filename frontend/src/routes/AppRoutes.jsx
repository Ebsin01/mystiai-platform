import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import PrivateRoute from '../components/PrivateRoute';
import PublicRoute from '../components/PublicRoute';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Profile from '../pages/Profile';
import UpdateProfile from '../pages/UpdateProfile';
import PalmAnalysisHistory from '../pages/PalmAnalysisHistory';
import PalmAnalysisDetail from '../pages/PalmAnalysisDetail';
import PalmAnalysisUpload from '../pages/PalmAnalysisUpload';
import TarotReading from '../pages/TarotReading';
import ThreeCardHistory from '../pages/ThreeCardHistory';
import AIDashboard from '../pages/AIDashboard';

// Simple mystic landing page content for home route `/`
const Home = () => {
  const isAuth = localStorage.getItem('token');

  return (
    <div className="landing-page-container">
      <header className="landing-hero">
        <div className="mystic-orb large-orb animate-pulse"></div>
        <h1>AI Palmistry &amp; Tarot</h1>
        <p className="subtitle">Demystify your destiny with artificial intelligence</p>
      </header>

      <main className="landing-features">
        <div className="mystic-card feature-card">
          <span className="card-icon">🔮</span>
          <h3>Tarot Readings</h3>
          <p>Harness neural intelligence to interpret ancient esoteric arcana and uncover hidden pathways.</p>
        </div>

        <div className="mystic-card feature-card">
          <span className="card-icon">✋</span>
          <h3>Palmistry Analysis</h3>
          <p>Analyze your hand lines, mounts, and shape using state of the art computer vision algorithms.</p>
        </div>
      </main>

      <section className="landing-cta">
        {isAuth ? (
          <Navigate to="/profile" replace />
        ) : (
          <div className="cta-buttons">
            <Navigate to="/login" replace />
          </div>
        )}
      </section>
    </div>
  );
};

/**
 * Main application routes orchestrator.
 * Combines pages with PublicRoute and PrivateRoute guards.
 */
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Home />} />

      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Private/Protected Routes */}
      <Route
        path="/profile"
        element={
          <PrivateRoute>
            <Profile />
          </PrivateRoute>
        }
      />

      <Route
        path="/update-profile"
        element={
          <PrivateRoute>
            <UpdateProfile />
          </PrivateRoute>
        }
      />

      {/* Palm Analysis History list */}
      <Route
        path="/palm-history"
        element={
          <PrivateRoute>
            <PalmAnalysisHistory />
          </PrivateRoute>
        }
      />

      {/* Palm Analysis Upload page */}
      <Route
        path="/palm-analysis/upload"
        element={
          <PrivateRoute>
            <PalmAnalysisUpload />
          </PrivateRoute>
        }
      />

      {/* Palm Analysis Detail page */}
      <Route
        path="/palm-analysis/:analysis_id"
        element={
          <PrivateRoute>
            <PalmAnalysisDetail />
          </PrivateRoute>
        }
      />

      {/* Tarot Reading page */}
      <Route
        path="/tarot-reading"
        element={
          <PrivateRoute>
            <TarotReading />
          </PrivateRoute>
        }
      />

      {/* Three-card history page */}
      <Route
        path="/three-card-history"
        element={
          <PrivateRoute>
            <ThreeCardHistory />
          </PrivateRoute>
        }
      />

      {/* AI dashboard page */}
      <Route
        path="/ai-dashboard"
        element={
          <PrivateRoute>
            <AIDashboard />
          </PrivateRoute>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
