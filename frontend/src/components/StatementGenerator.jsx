import React, { useState } from 'react';
import { FileText, Download, AlertCircle } from 'lucide-react';
import api from '../api/axios';

export const StatementGenerator = ({ accountId }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [statement, setStatement] = useState(null);

    const formatCurrency = (amountInCents) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amountInCents / 100);
    };

    const handleDownload = async () => {
        if (!accountId) return;
        
        setLoading(true);
        setError('');
        
        try {
            const response = await api.get(`/accounts/${accountId}/statement/`);
            setStatement(response.data);
        } catch (err) {
            console.error('Statement Generation Error:', err);
            setError('Failed to generate statement. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Account Statement
            </h2>

            {error && (
                <div className="mb-4 bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start">
                    <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-700">{error}</p>
                </div>
            )}

            <button
                onClick={handleDownload}
                disabled={loading || !accountId}
                className={`w-full flex justify-center items-center py-2.5 px-4 border border-gray-300 rounded-lg shadow-sm text-sm font-medium transition-colors
                    ${loading || !accountId 
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                        : 'bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                    }`}
            >
                <Download className={`h-5 w-5 mr-2 ${loading ? 'animate-bounce' : ''}`} />
                {loading ? 'Generating...' : 'Download Monthly Statement'}
            </button>

            {statement && (
                <div className="mt-6 border-t border-gray-100 pt-6 animate-fade-in-down">
                    <h3 className="text-sm font-medium text-gray-900 mb-4">Statement Summary</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Starting Balance</span>
                            <span className="font-medium text-gray-900">{formatCurrency(statement.starting_balance)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Total Credits</span>
                            <span className="font-medium text-green-600">+{formatCurrency(statement.total_credits)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Total Debits</span>
                            <span className="font-medium text-red-600">-{formatCurrency(statement.total_debits)}</span>
                        </div>
                        <div className="flex justify-between text-sm pt-2 border-t border-gray-100">
                            <span className="font-medium text-gray-900">Ending Balance</span>
                            <span className="font-bold text-gray-900">{formatCurrency(statement.ending_balance)}</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-400 pt-2">
                            <span>Transactions Processed</span>
                            <span>{statement.transaction_count}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
