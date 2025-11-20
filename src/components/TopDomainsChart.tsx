'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';

export default function TopDomainsChart() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('/api/stats/top-domains')
            .then(res => res.json())
            .then(setData);
    }, []);

    if (!data.length) return <div className="h-64 flex items-center justify-center text-gray-500">Loading...</div>;

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="w-full h-[350px] bg-gray-900/50 backdrop-blur-md rounded-xl p-6 border border-gray-800 shadow-xl"
        >
            <h2 className="text-xl font-bold mb-4 text-white">Top Domains</h2>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart layout="vertical" data={data} margin={{ left: 20 }}>
                    <XAxis type="number" hide />
                    <YAxis
                        dataKey="domain_name"
                        type="category"
                        stroke="#9ca3af"
                        tickLine={false}
                        axisLine={false}
                        width={100}
                    />
                    <Tooltip
                        cursor={{ fill: 'transparent' }}
                        contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                    />
                    <Bar dataKey="monthly_pageviews" radius={[0, 4, 4, 0]}>
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index === 0 ? '#ec4899' : '#8b5cf6'} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
