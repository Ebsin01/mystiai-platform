import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import Navbar from './components/Navbar';
import AppRoutes from './routes/AppRoutes';
import './App.css';

/**
 * Root Application component initializing the Router and layouts.
 */
function App() {
  return (
    <Router>
      <div className="app-wrapper">
        <Navbar />
        <main className="app-main-content">
          <AppRoutes />
        </main>
        <footer className="app-footer">
          <p>© 2026 AI Palmistry & Tarot Intelligence Platform. All secrets reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
