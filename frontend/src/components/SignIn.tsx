import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

interface SignInProps {
    onLogin: () => void;
}

export default function SignIn({ onLogin }: SignInProps) {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [emailTouched, setEmailTouched] = useState(false);
    const [passwordTouched, setPasswordTouched] = useState(false);

    const validateEmail = (email: string) => {
        // More comprehensive email validation
        const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return emailRegex.test(email.trim()) && email.length <= 254;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Form validation with specific messages
        if (!email && !password) {
            setError('Please enter your email and password.');
            return;
        }
        if (!email) {
            setError('Please enter your email address.');
            return;
        }
        if (!password) {
            setError('Please enter your password.');
            return;
        }
        if (!validateEmail(email)) {
            setError('Please enter a valid email address (e.g., user@example.com).');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters long.');
            return;
        }
        if (password.length > 128) {
            setError('Password is too long. Please use a shorter password.');
            return;
        }

        // Call the API for login
        setIsLoading(true);
        try {
            await authService.login(email, password);
            onLogin(); // Update app state to reflect authentication
        } catch (err: any) {
            console.error('Login error:', err);
            
            // Handle different types of errors with specific messages
            const errorMessage = err.response?.data?.error || err.response?.data?.detail || '';
            const statusCode = err.response?.status;
            
            if (statusCode === 400) {
                // Handle specific 400 errors based on message content
                if (errorMessage.toLowerCase().includes('invalid email or password')) {
                    setError('The email or password you entered is incorrect. Please check your credentials and try again.');
                } else if (errorMessage.toLowerCase().includes('account is temporarily locked')) {
                    setError('Your account has been temporarily locked due to multiple failed login attempts. Please try again in a few minutes.');
                } else if (errorMessage.toLowerCase().includes('account is not active')) {
                    setError('Your account is not active. Please contact support for assistance.');
                } else if (errorMessage.toLowerCase().includes('email is not verified')) {
                    setError('Please verify your email address before logging in. Check your inbox for a verification email.');
                } else if (errorMessage.toLowerCase().includes('validation failed')) {
                    setError('Please check that your email and password are entered correctly.');
                } else if (errorMessage) {
                    setError(errorMessage);
                } else {
                    setError('Invalid login credentials. Please check your email and password.');
                }
            } else if (statusCode === 401) {
                setError('The email or password you entered is incorrect. Please check your credentials and try again.');
            } else if (statusCode === 423 || statusCode === 429) {
                // Rate limiting or account locked
                if (errorMessage.toLowerCase().includes('too many login attempts from this ip')) {
                    setError('Too many login attempts from your location. Please wait a few minutes before trying again.');
                } else if (errorMessage.toLowerCase().includes('too many failed login attempts for this email')) {
                    setError('Too many failed attempts for this email address. Please wait before trying again or reset your password.');
                } else {
                    setError('Your account is temporarily locked due to too many failed attempts. Please try again later.');
                }
            } else if (statusCode === 422) {
                // Validation errors
                setError('Please check that your email and password are entered correctly.');
            } else if (statusCode >= 500) {
                setError('Our servers are experiencing issues. Please try again in a few moments.');
            } else if (err.code === 'NETWORK_ERROR' || !err.response) {
                setError('Unable to connect to our servers. Please check your internet connection and try again.');
            } else {
                // Fallback for any other errors
                setError(errorMessage || 'Login failed. Please try again or contact support if the problem persists.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={'flex flex-col justify-center items-center bg-white px-6 py-8 rounded-3xl border-2 border-gray-100 w-3/4 min-h-[460px]'}>
            <strong className={'text-3xl'}>Welcome Back!</strong>
            <form className={'mt-4 w-full'} onSubmit={handleSubmit}>
                <div>
                    <label className={'text-lg font-medium'}>Email</label>
                    <input 
                        className={`w-full border-2 rounded-xl p-2 bg-transparent transition-colors ${
                            emailTouched && email && !validateEmail(email) 
                                ? 'border-red-300 focus:border-red-500' 
                                : emailTouched && email && validateEmail(email)
                                ? 'border-green-300 focus:border-green-500'
                                : 'border-gray-100 focus:border-violet-400'
                        }`}
                        placeholder={'Enter your email'} 
                        type="email" 
                        value={email} 
                        onChange={e => {
                            setEmail(e.target.value);
                            setError(''); // Clear error when user starts typing
                        }}
                        onBlur={() => setEmailTouched(true)}
                        disabled={isLoading} 
                    />
                    {emailTouched && email && !validateEmail(email) && (
                        <div className="text-red-500 text-xs mt-1">Please enter a valid email address</div>
                    )}
                </div>
                <div className={'mt-4'}>
                    <label className={'text-lg font-medium'}>Password</label>
                    <input 
                        className={`w-full border-2 rounded-xl p-2 bg-transparent transition-colors ${
                            passwordTouched && password && password.length < 6
                                ? 'border-red-300 focus:border-red-500'
                                : passwordTouched && password && password.length >= 6
                                ? 'border-green-300 focus:border-green-500'
                                : 'border-gray-100 focus:border-violet-400'
                        }`}
                        placeholder={'Enter your password'} 
                        type="password" 
                        value={password} 
                        onChange={e => {
                            setPassword(e.target.value);
                            setError(''); // Clear error when user starts typing
                        }}
                        onBlur={() => setPasswordTouched(true)}
                        disabled={isLoading} 
                    />
                    {passwordTouched && password && password.length < 6 && (
                        <div className="text-red-500 text-xs mt-1">Password must be at least 6 characters</div>
                    )}
                </div>
                {error && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                        <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <div className="text-red-700 text-sm leading-relaxed">{error}</div>
                    </div>
                )}
                <div className={'flex flex-col mt-8 gap-y-2'}>
                    <button type="submit" className={'active:scale-[.98] active:duration-75 transition-all hover:scale-[1.02] ease-in-out bg-violet-500 text-white text-lg p-2 rounded-xl font-bold relative'}
                            disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <span className="opacity-0">Sign in</span>
                                <span className="absolute inset-0 flex items-center justify-center">
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                </span>
                            </>
                        ) : 'Sign in'}
                    </button>
                    <div className={'flex justify-center items-center mt-4 gap-3'}>
                        <p className={'font-medium'}>Don&apos;t have an account?</p>
                        <button
                            type="button"
                            className={'font-medium text-violet-500 hover:scale-110 hover:text-violet-600 transition-all duration-200'}
                            onClick={() => navigate('/signup')}
                            disabled={isLoading}
                        >
                            Sign up
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}

