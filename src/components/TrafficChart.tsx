'use client';

import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

export default function TrafficChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('/api/stats/trend')
            .then(res => res.json())
            .then(data => {
                // Format date for display
                const formatted = data.map((item: any) => ({
                    ...item,
                    date: new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                }));
                setData(formatted);
            });
    }, []);

    if (!data.length) return <div className="h-64 flex items-center justify-center text-gray-500">Loading...</div>;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full h-[400px] bg-gray-900/50 backdrop-blur-md rounded-xl p-6 border border-gray-800 shadow-xl"
        >
            <h2 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                Traffic Pulse
            </h2>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                    <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} axisLine={false} />
                    <YAxis stroke="#9ca3af" tickLine={false} axisLine={false} tickFormatter={(value) => `${value / 1000}k`} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                        itemStyle={{ color: '#22d3ee' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="total_views"
                        stroke="#06b6d4"
                        fillOpacity={1}
                        fill="url(#colorViews)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
