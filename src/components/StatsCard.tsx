'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    color: string;
    delay?: number;
}

export default function StatsCard({ title, value, icon: Icon, color, delay = 0 }: StatsCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className="bg-gray-900/50 backdrop-blur-md p-6 rounded-xl border border-gray-800 shadow-lg flex items-center space-x-4"
        >
            <div className={`p-3 rounded-lg bg-opacity-20 ${color} bg-current`}>
                <Icon className={`w-8 h-8 ${color.replace('bg-', 'text-')}`} />
            </div>
            <div>
                <p className="text-gray-400 text-sm font-medium">{title}</p>
                <h3 className="text-2xl font-bold text-white">{value}</h3>
            </div>
        </motion.div>
    );
}
