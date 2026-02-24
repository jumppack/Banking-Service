import React from 'react';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

export const TransactionHistory = ({ transactions }) => {
    if (!transactions || transactions.length === 0) {
        return (
            <div className="bg-white shadow rounded-lg p-6 text-center">
                <p className="text-gray-500">No recent transactions to display.</p>
            </div>
        );
    }

    // Cent formatting helper ($10.45 from 1045)
    const formatCurrency = (amountInCents) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amountInCents / 100);
    };

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-5 border-b border-gray-200">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Transactions</h3>
            </div>
            <ul className="divide-y divide-gray-200">
                {transactions.map((tx) => {
                    // Legacy DB safeguard: old outgoing transactions might hold positive values but type 'debit' or 'transfer_out'
                    const isOutgoing = tx.amount < 0 || tx.type === 'debit' || tx.type === 'transfer_out';
                    const isIncoming = !isOutgoing;
                    
                    const Icon = isIncoming ? ArrowDownLeft : ArrowUpRight;
                    const iconColor = isIncoming ? 'text-green-500' : 'text-red-500';
                    const iconBg = isIncoming ? 'bg-green-100' : 'bg-red-100';
                    const amountColor = isIncoming ? 'text-green-600' : 'text-gray-900';
                    const sign = isIncoming ? '+' : '-';
                    
                    // Always process absolute cent amount: handles both old positives and new strict negatives safely.
                    const absoluteCentAmount = Math.abs(tx.amount);

                    // Resolve exact 'Sent To' and 'Received From' phrasing, pushing Email to fully lowercase
                    let displayLabel = tx.type.replace('_', ' ');
                    if (tx.counterparty_name) {
                        displayLabel = isIncoming 
                            ? `Received from: ${tx.counterparty_name.toLowerCase()}` 
                            : `Sent to: ${tx.counterparty_name.toLowerCase()}`;
                    } else if (['transfer_in', 'transfer_out', 'debit', 'credit'].includes(tx.type)) {
                        // Retain capitalization for internal standard labels if DB lacks a counterparty
                        displayLabel = tx.type.charAt(0).toUpperCase() + tx.type.slice(1).replace('_', ' ');
                    }

                    return (
                        <li key={tx.id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                            <div className="flex items-center">
                                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${iconBg}`}>
                                    <Icon className={`h-5 w-5 ${iconColor}`} />
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-900">
                                        {displayLabel}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        {new Date(tx.timestamp).toLocaleDateString(undefined, {
                                            month: 'short',
                                            day: 'numeric',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </p>
                                </div>
                            </div>
                            <div className={`text-sm font-semibold ${amountColor}`}>
                                {sign}{formatCurrency(absoluteCentAmount)}
                            </div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};
