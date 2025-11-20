'use client';

import { useEffect, useState } from 'react';
import TrafficChart from '@/components/TrafficChart';
import PlatformChart from '@/components/PlatformChart';
import TopDomainsChart from '@/components/TopDomainsChart';
import StatsCard from '@/components/StatsCard';
import { Users, Eye, Activity, Globe } from 'lucide-react';

export default function Home() {
  const [stats, setStats] = useState({
    totalViews: 0,
    totalUsers: 0, // This will be a sum of daily active users for now
  });

  useEffect(() => {
    // Fetch trend data to calculate totals
    fetch('/api/stats/trend')
      .then(res => res.json())
      .then(data => {
        const totalViews = data.reduce((acc: number, curr: any) => acc + (curr.total_views || 0), 0);
        // We don't have total users in trend, but we can sum it if we added it to the query. 
        // For now, let's just use a placeholder or fetch from another endpoint if needed.
        // Actually, let's just show Total Views and maybe "Data Points" for now.
        setStats({ totalViews, totalUsers: data.length });
      });
  }, []);

  return (
    <main className="min-h-screen p-8 md:p-12 max-w-7xl mx-auto space-y-12">
      {/* Header */}
      <header className="space-y-2">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600">
          Publisher Pulse
        </h1>
        <p className="text-gray-400 text-lg">Real-time insights into your digital ecosystem.</p>
      </header>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Pageviews"
          value={stats.totalViews.toLocaleString()}
          icon={Eye}
          color="bg-cyan-500"
          delay={0}
        />
        <StatsCard
          title="Data Points"
          value={stats.totalUsers.toLocaleString()}
          icon={Activity}
          color="bg-purple-500"
          delay={0.1}
        />
        <StatsCard
          title="Active Platforms"
          value="3"
          icon={Globe}
          color="bg-pink-500"
          delay={0.2}
        />
        <StatsCard
          title="Publishers"
          value="12"
          icon={Users}
          color="bg-blue-500"
          delay={0.3}
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Traffic Pulse - Spans 2 columns */}
        <div className="lg:col-span-2">
          <TrafficChart />
        </div>

        {/* Platform Split */}
        <div className="lg:col-span-1">
          <PlatformChart />
        </div>
      </div>

      {/* Secondary Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <TopDomainsChart />
        {/* Placeholder for another chart or list */}
        <div className="bg-gray-900/50 backdrop-blur-md rounded-xl p-6 border border-gray-800 shadow-xl flex items-center justify-center">
          <p className="text-gray-500">More insights coming soon...</p>
        </div>
      </div>
    </main>
  );
}
