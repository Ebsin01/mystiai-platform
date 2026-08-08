import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../services/authService';

/**
 * Route guard component for protecting private routes.
 * Redirects unauthenticated users to the Login page.
 */
const PrivateRoute = ({ children }) => {
  const isAuth = authService.isAuthenticated();
  
  return isAuth ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
