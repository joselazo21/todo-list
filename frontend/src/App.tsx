import { useEffect } from 'react';
import './App.css';
import AppRoutes from './routes';
import { authService, setAuthContextRef } from './services/api';
import { useAuth } from './contexts/AuthContext';
import {LogoutIcon} from "./assets/icons";

function App() {
  const auth = useAuth();

  useEffect(() => {
    // Set the auth context reference for the API service
    setAuthContextRef(auth);
  }, [auth]);

  const handleLogin = () => {
    // The auth state is already updated by the authService.login call
    // No need to manually update state here
  };

  const handleLogout = () => {
    authService.logout();
  };

  // Show loading spinner while auth is initializing
  if (auth.isLoading) {
    return (
      <div className="flex items-center justify-center w-full h-svh bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-violet-500"></div>
          <p className="text-gray-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  return (
      <div className={"flex w-full h-svh"}>
        {auth.isAuthenticated && (
          <div className="fixed top-0 left-0 w-full flex justify-between items-center bg-gray-100 px-6 py-3 shadow z-50">
            <div className="text-gray-700 font-medium">
              Welcome, <span className="text-violet-600 font-bold">{auth.user?.name || 'User'}</span>
            </div>
            <button
                className="text-red-500 px-4 py-2 rounded-lg font-bold hover:underline active:scale-[.98] active:duration-75 transition-all hover:scale-[1.02] ease-in-out flex items-center gap-2"
                onClick={handleLogout}
            >
              <LogoutIcon />
              Logout
            </button>
          </div>
        )}
        <div
            className={`m-2 flex h-fit mt-25 items-center justify-center ${
                auth.isAuthenticated ?   'w-full':'lg:w-1/2 w-full'
            }`}
        >
          <AppRoutes isAuthenticated={auth.isAuthenticated} onLogin={handleLogin} />
        </div>
        {!auth.isAuthenticated && (<div className={'w-1/2 hidden relative lg:flex h-full bg-gray-200 items-center justify-center'}>
          <div className={'w-40 h-40 bg-gradient-to-tr from-purple-500 to-red-500 rounded-full animate-bounce'}></div>
          <div className={'w-full h-1/2 bottom-0 absolute bg-gray-200/40 backdrop-blur-lg'}></div>
        </div>)}
      </div>
  );
}

export default App;
