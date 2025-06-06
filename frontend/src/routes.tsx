import { Routes, Route, Navigate } from 'react-router-dom';
import React from 'react';
import SignIn from './components/SignIn.tsx';
import SignUp from './components/SignUp';
import Todo from './components/Todo.tsx';

interface AppRoutesProps {
  isAuthenticated: boolean;
  onLogin: () => void;
}

// Componente para proteger rutas
const ProtectedRoute = ({
  isAuthenticated,
  children
}: {
  isAuthenticated: boolean;
  children: React.ReactElement;
}) => {
  if (!isAuthenticated) {
    // Si no está autenticado, redirige a la página de inicio de sesión
    return <Navigate to="/" replace />;
  }
  return children;
};

// Componente para redireccionar si ya está autenticado
const RedirectIfAuthenticated = ({
  isAuthenticated,
  children
}: {
  isAuthenticated: boolean;
  children: React.ReactElement;
}) => {
  if (isAuthenticated) {
    // Si ya está autenticado, redirige a la lista de tareas
    return <Navigate to="/todos" replace />;
  }
  return children;
};

export default function AppRoutes({ isAuthenticated, onLogin }: AppRoutesProps) {
  return (
    <Routes>
      {/* Rutas para usuarios no autenticados */}
      <Route
        path="/"
        element={
          <RedirectIfAuthenticated isAuthenticated={isAuthenticated}>
            <SignIn onLogin={onLogin} />
          </RedirectIfAuthenticated>
        }
      />
      <Route
        path="/signup"
        element={
          <RedirectIfAuthenticated isAuthenticated={isAuthenticated}>
            <SignUp />
          </RedirectIfAuthenticated>
        }
      />

      {/* Rutas protegidas para usuarios autenticados */}
      <Route
        path="/todos"
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Todo />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

