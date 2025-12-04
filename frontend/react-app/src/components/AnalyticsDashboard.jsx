import React from 'react';
import { BarChart3, Home, TrendingUp, MessageSquare } from 'lucide-react';

const StatCard = ({ icon: Icon, label, value, trend }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <div className="p-2 bg-primary-50 rounded-lg">
          <Icon className="w-5 h-5 text-primary-600" />
        </div>
        {trend && (
          <span className={`text-xs font-medium ${
            trend > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
};

const AnalyticsDashboard = ({ data = {} }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-6 h-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Home}
          label="Total Listings"
          value={data.totalListings || 0}
        />
        <StatCard
          icon={BarChart3}
          label="Total Images"
          value={data.totalImages || 0}
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Condition Score"
          value={data.avgConditionScore ? (data.avgConditionScore * 100).toFixed(0) + '%' : 'N/A'}
        />
        <StatCard
          icon={MessageSquare}
          label="Conversations"
          value={data.totalConversations || 0}
        />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
