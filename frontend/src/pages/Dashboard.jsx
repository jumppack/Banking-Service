import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';
import { Navigation } from '../components/Navigation';
import { CardDisplay } from '../components/CardDisplay';
import { TransactionHistory } from '../components/TransactionHistory';

export const Dashboard = () => {
    const { user } = useContext(AuthContext);
    
    // UI State
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    
    // Data State
    const [accounts, setAccounts] = useState([]);
    const [cards, setCards] = useState([]);
    const [transactions, setTransactions] = useState([]);

    // We isolate the primary checking account to drive the UI safely
    const primaryAccount = accounts.find(acc => acc.account_number?.startsWith("100")) || accounts[0];

    useEffect(() => {
        const fetchDashboardData = async () => {
            setLoading(true);
            setError('');
            try {
                // 1. Fetch Accounts
                const accResponse = await api.get('/accounts/me');
                const userAccounts = accResponse.data;
                setAccounts(userAccounts);

                if (userAccounts.length > 0) {
                    const mainAccId = userAccounts[0].id;
                    
                    // 2. Fire parallel requests for Cards and Transactions tied to the main account
                    const [cardsRes, txRes] = await Promise.all([
                        api.get('/cards/'),
                        api.get(`/accounts/${mainAccId}/transactions/`)
                    ]);
                    
                    setCards(cardsRes.data);
                    setTransactions(txRes.data);
                }
            } catch (err) {
                console.error("Dashboard Fetch Error:", err.response?.status, err);
                setError('Failed to securely fetch dashboard data.');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    // Helper to format the big Hero balance
    const formatBalance = (balanceInCents) => {
        if (balanceInCents === undefined) return "$0.00";
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(balanceInCents / 100);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                <Navigation />
                <div className="flex items-center justify-center p-12">
                    <p className="text-gray-500 animate-pulse">Synchronizing secure data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation />
            
            <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {error && (
                    <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                )}

                {/* Top Section: Balance & Cards */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    
                    {/* Primary Balance Widget */}
                    <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-8 flex flex-col justify-center">
                        <h2 className="text-lg font-medium text-gray-500 mb-2 whitespace-nowrap">
                            Total Available Balance
                        </h2>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-5xl font-extrabold text-gray-900 tracking-tight">
                                {formatBalance(primaryAccount?.balance)}
                            </span>
                            <span className="text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                                Active • {primaryAccount?.currency}
                            </span>
                        </div>
                        <p className="mt-4 text-sm text-gray-500">
                            Available in {primaryAccount?.account_number ? `checking account ending in ${primaryAccount.account_number.slice(-4)}` : 'your primary account'}.
                        </p>
                    </div>

                    {/* Debit Card Display Widget */}
                    <div className="lg:col-span-1 flex items-center justify-center lg:justify-end">
                        <CardDisplay 
                            card={cards.length > 0 ? cards[0] : null} 
                            cardholderName={user?.identifier ? user.identifier.split('@')[0] : 'Card Holder'} 
                        />
                    </div>
                </div>

                {/* Bottom Section: Transaction History */}
                <div className="grid grid-cols-1 gap-8">
                    <div className="mt-4">
                        <TransactionHistory transactions={transactions} />
                    </div>
                </div>

            </main>
        </div>
    );
};
