import React, { useContext } from 'react';
import { LogOut, User as UserIcon } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

export const Navigation = () => {
    const { user, logout } = useContext(AuthContext);

    return (
        <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <div className="flex-shrink-0 flex items-center">
                            <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <span className="text-white font-bold text-xl leading-none">B</span>
                            </div>
                            <span className="ml-3 text-xl font-bold text-gray-900 tracking-tight">Banking</span>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center text-sm font-medium text-gray-700 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200">
                            <UserIcon className="h-4 w-4 mr-2 text-gray-500" />
                            <span>{user?.identifier || 'User'}</span>
                        </div>
                        <button
                            onClick={logout}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors"
                            aria-label="Logout"
                        >
                            <LogOut className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};
