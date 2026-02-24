import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';

export const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            // OAuth2PasswordRequestForm strictly requires form data, not JSON.
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await api.post('/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            // On success, hydrate the AuthContext and redirect to the dashboard
            login(response.data.access_token);
            navigate('/');
        } catch (err) {
            console.error("Login Error Details:", err);
            setError(err.response?.data?.detail || err.message || 'An error occurred during login');
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
                        Sign in to Banking
                    </h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 flex items-center">
                            <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0" />
                            <p className="text-sm text-red-700">{error}</p>
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
                                    autoComplete="current-password"
                                    required
                                    className="flex-grow px-3 py-2 outline-none border-none bg-transparent placeholder-gray-500 text-gray-900 sm:text-sm"
                                    placeholder="Password"
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
                            {isLoading ? 'Authenticating...' : 'Sign in'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
