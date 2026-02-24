import React, { useState } from 'react';
import { Send, AlertCircle, CheckCircle2 } from 'lucide-react';
import api from '../api/axios';

export const TransferForm = ({ accountId, onTransferComplete }) => {
    const [destinationId, setDestinationId] = useState('');
    const [amount, setAmount] = useState('');
    
    // UI State
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        // Basic client-side validation
        if (!destinationId || destinationId.trim() === '') {
            setError('Destination Account ID is required');
            setLoading(false);
            return;
        }

        const parsedAmount = parseFloat(amount);
        if (isNaN(parsedAmount) || parsedAmount <= 0) {
            setError('Please enter a valid transfer amount');
            setLoading(false);
            return;
        }

        try {
            // Convert to cents before sending to the backend
            const amountInCents = Math.round(parsedAmount * 100);
            
            const payload = {
                from_account_id: accountId,
                to_identifier: destinationId.trim(),
                amount: amountInCents
            };

            await api.post('/transfers/', payload);
            
            // Clear form and display success
            setSuccess(`Successfully transferred $${parsedAmount.toFixed(2)}.`);
            setDestinationId('');
            setAmount('');
            
            // Trigger upstream data refresh
            if (onTransferComplete) {
                onTransferComplete();
            }

        } catch (err) {
            console.error('Transfer Error:', err);
            // Attempt to parse specific FastAPI validation errors or business logic errors
            const backendDetail = err.response?.data?.detail;
            if (Array.isArray(backendDetail)) {
                setError(backendDetail[0]?.msg || 'Validation error on payload');
            } else if (typeof backendDetail === 'string') {
                setError(backendDetail);
            } else {
                setError('Failed to initiate transfer. Please verify the destination ID.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <Send className="h-5 w-5 mr-2 text-blue-600" />
                Transfer Funds
            </h2>

            {error && (
                <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start">
                    <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            {success && (
                <div className="mb-4 bg-green-50 border-l-4 border-green-500 p-4 rounded-md flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-green-700">{success}</p>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="destinationId" className="block text-sm font-medium text-gray-700 mb-1">
                        Destination Identifier (Email or Account ID)
                    </label>
                    <input
                        type="text"
                        id="destinationId"
                        value={destinationId}
                        onChange={(e) => setDestinationId(e.target.value)}
                        placeholder="e.g. bob@example.com"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
                        required
                        disabled={loading || !accountId}
                    />
                </div>

                <div>
                    <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-1">
                        Amount (USD)
                    </label>
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <span className="text-gray-500 sm:text-sm">$</span>
                        </div>
                        <input
                            type="number"
                            id="amount"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            placeholder="0.00"
                            step="0.01"
                            min="0.01"
                            className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
                            required
                            disabled={loading || !accountId}
                        />
                    </div>
                </div>

                <div className="pt-2">
                    <button
                        type="submit"
                        disabled={loading || !accountId}
                        className={`w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white transition-colors
                            ${loading || !accountId 
                                ? 'bg-blue-400 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                            }`}
                    >
                        {loading ? 'Processing...' : 'Send Money'}
                    </button>
                </div>
            </form>
        </div>
    );
};
