import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext.tsx';
import { TodoProvider } from './contexts/TodoContext.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <TodoProvider>
        <Router>
          <App />
        </Router>
      </TodoProvider>
    </AuthProvider>
  </StrictMode>
)
