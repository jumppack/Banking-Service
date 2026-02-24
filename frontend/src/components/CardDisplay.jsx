import React from 'react';
import { CreditCard, Wifi } from 'lucide-react';

export const CardDisplay = ({ card, cardholderName }) => {
    if (!card) {
        return (
            <div className="h-48 w-full max-w-sm rounded-2xl bg-gray-100 border-2 border-dashed border-gray-300 flex items-center justify-center">
                <p className="text-gray-500 font-medium">No active card found.</p>
            </div>
        );
    }

    // Mask card number: "9555581897110855" -> "•••• •••• •••• 0855"
    const maskedNumber = `•••• •••• •••• ${card.card_number.slice(-4)}`;

    return (
        <div className="relative h-56 w-full max-w-sm rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-900 p-6 text-white shadow-xl overflow-hidden">
            {/* Background Pattern overlays */}
            <div className="absolute top-0 right-0 -mr-8 -mt-8 h-32 w-32 rounded-full bg-white opacity-10"></div>
            <div className="absolute bottom-0 right-0 -mb-8 -mr-8 h-24 w-24 rounded-full bg-white opacity-10"></div>
            
            <div className="flex justify-between items-start h-full flex-col relative z-10">
                <div className="w-full flex justify-between items-center">
                    <CreditCard className="h-8 w-8 text-white opacity-80" />
                    <Wifi className="h-6 w-6 text-white opacity-80 transform rotate-90" />
                </div>
                
                <div className="w-full mt-4">
                    <p className="font-mono text-2xl tracking-widest">{maskedNumber}</p>
                </div>
                
                <div className="w-full flex justify-between items-end mt-4">
                    <div>
                        <p className="text-xs uppercase tracking-wider opacity-70 mb-1">Card Holder</p>
                        <p className="font-medium tracking-wide">{cardholderName}</p>
                    </div>
                    <div>
                        <p className="text-xs uppercase tracking-wider opacity-70 mb-1">Expires</p>
                        <p className="font-medium font-mono">{card.expiry}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
