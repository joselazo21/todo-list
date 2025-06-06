import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

export default function SignUp() {
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const validateEmail = (email: string) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Form validation
        if (!name || !email || !password || !confirmPassword) {
            setError('All fields are required.');
            return;
        }
        if (name.length < 2) {
            setError('Name must be at least 2 characters long.');
            return;
        }
        if (!validateEmail(email)) {
            setError('Invalid email format.');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters.');
            return;
        }
        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }


        setIsLoading(true);
        try {
            await authService.register(name, email, password);
            setSuccess('Account created successfully! You can now sign in.');
            setTimeout(() => navigate('/'), 1500);
        } catch (err: any) {
            if (err.response?.data?.email) {
                setError(`Email error: ${err.response.data.email.join(' ')}`);
            } else if (err.response?.data?.password) {
                setError(`Password error: ${err.response.data.password.join(' ')}`);
            } else if (err.response?.data?.name) {
                setError(`Name error: ${err.response.data.name.join(' ')}`);
            } else if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Registration failed. Please try again later.');
            }
            console.error('Registration error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={'flex flex-col justify-center items-center bg-white px-6 py-8 rounded-3xl border-2 border-gray-100 w-3/4 min-h-[460px]'}>
            <strong className={'text-3xl'}>Create Account</strong>
            <form className={'mt-4 w-full'} onSubmit={handleSubmit}>
                <div>
                    <label className={'text-lg font-medium'}>Full Name</label>
                    <input className={'w-full border-2 border-gray-100 rounded-xl p-2 bg-transparent'}
                           placeholder={'Enter your full name'} type="text" value={name} onChange={e => setName(e.target.value)} disabled={isLoading} />
                </div>
                <div className={'mt-4'}>
                    <label className={'text-lg font-medium'}>Email</label>
                    <input className={'w-full border-2 border-gray-100 rounded-xl p-2 bg-transparent'}
                           placeholder={'Enter your email'} type="email" value={email} onChange={e => setEmail(e.target.value)} disabled={isLoading} />
                </div>
                <div className={'mt-4'}>
                    <label className={'text-lg font-medium'}>Password</label>
                    <input className={'w-full border-2 border-gray-100 rounded-xl p-2 bg-transparent'}
                           placeholder={'Create a password'} type="password" value={password} onChange={e => setPassword(e.target.value)} disabled={isLoading} />
                </div>
                <div className={'mt-4'}>
                    <label className={'text-lg font-medium'}>Confirm Password</label>
                    <input className={'w-full border-2 border-gray-100 rounded-xl p-2 bg-transparent'}
                           placeholder={'Repeat your password'} type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} disabled={isLoading} />
                </div>
                {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
                {success && <div className="text-green-600 text-sm mt-2">{success}</div>}
                <div className={'flex flex-col mt-4 gap-y-2'}>
                    <button type="submit" className={'active:scale-[.98] active:duration-75 transition-all hover:scale-[1.02] ease-in-out bg-violet-500 text-white text-lg p-2 rounded-xl font-bold relative'} disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <span className="opacity-0">Sign up</span>
                                <span className="absolute inset-0 flex items-center justify-center">
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                </span>
                            </>
                        ) : 'Sign up'}
                    </button>
                    <div className={'flex justify-center items-center mt-4 gap-3'}>
                        <p className={'font-medium'}>Already have an account?</p>
                        <button
                            type="button"
                            className={'font-medium text-violet-500 hover:scale-110 hover:text-violet-600 transition-all duration-200'}
                            onClick={() => navigate('/')}
                            disabled={isLoading}
                        >
                            Sign in
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}

