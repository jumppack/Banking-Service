import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, AlertCircle, CheckCircle2, Eye, EyeOff } from 'lucide-react';
import api from '../api/axios';

export const Signup = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setIsLoading(true);

        try {
            const payload = {
                email: email,
                password: password
            };

            await api.post('/auth/signup', payload);

            // On success, display message and redirect
            setSuccess('Registration successful! Redirecting to login...');
            
            setTimeout(() => {
                navigate('/login');
            }, 2000);
            
        } catch (err) {
            console.error("Signup Error Details:", err);
            // Attempt to parse validation array or direct detail string
            const backendDetail = err.response?.data?.detail;
            if (Array.isArray(backendDetail)) {
                setError(backendDetail[0]?.msg || 'Validation error on payload');
            } else if (typeof backendDetail === 'string') {
                setError(backendDetail);
            } else {
                setError('Registration failed. Please try a different email.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <div>
                    <div className="mx-auto h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <Lock className="h-6 w-6 text-blue-600" />
                    </div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 tracking-tight">
                        Create an Account
                    </h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 flex items-center">
                            <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0" />
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    )}
                    {success && (
                        <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4 flex items-center">
                            <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
                            <p className="text-sm text-green-700">{success}</p>
                        </div>
                    )}
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div className="relative mb-4">
                            <label htmlFor="email-address" className="sr-only">Email address</label>
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Mail className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                id="email-address"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="appearance-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                                placeholder="Email address"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">Password</label>
                            <div className="flex items-center border border-gray-300 rounded-md bg-white focus-within:ring-2 focus-within:ring-blue-500 overflow-hidden">
                                <div className="pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    id="password"
                                    name="password"
                                    type={showPassword ? "text" : "password"}
                                    autoComplete="new-password"
                                    required
                                    className="flex-grow px-3 py-2 outline-none border-none bg-transparent placeholder-gray-500 text-gray-900 sm:text-sm"
                                    placeholder="Create a Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <button
                                    type="button"
                                    className="px-3 text-gray-500 hover:text-gray-700 flex items-center focus:outline-none bg-transparent"
                                    onClick={() => setShowPassword(!showPassword)}
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-5 w-5" />
                                    ) : (
                                        <Eye className="h-5 w-5" />
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-50"
                        >
                            {isLoading ? 'Creating Account...' : 'Sign Up'}
                        </button>
                    </div>
                    
                    <div className="text-center mt-4">
                        <Link to="/login" className="font-medium text-sm text-blue-600 hover:text-blue-500 transition-colors">
                            Already have an account? Log in
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
};
