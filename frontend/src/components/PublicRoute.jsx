import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Route guard component for public pages (e.g. Login, Register).
 * Redirects authenticated users to their Profile page.
 */
const PublicRoute = ({ children }) => {
  const isAuth = authService.isAuthenticated();
  
  return isAuth ? <Navigate to="/profile" replace /> : children;
};

export default PublicRoute;
