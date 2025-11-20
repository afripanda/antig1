'use client';

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { motion } from 'framer-motion';

const COLORS = ['#8b5cf6', '#ec4899', '#06b6d4', '#10b981'];

export default function PlatformChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('/api/stats/platform')
            .then(res => res.json())
            .then(setData);
    }, []);

    if (!data.length) return <div className="h-64 flex items-center justify-center text-gray-500">Loading...</div>;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="w-full h-[350px] bg-gray-900/50 backdrop-blur-md rounded-xl p-6 border border-gray-800 shadow-xl"
        >
            <h2 className="text-xl font-bold mb-4 text-white">Platform Distribution</h2>
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="total_views"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                    />
                    <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
