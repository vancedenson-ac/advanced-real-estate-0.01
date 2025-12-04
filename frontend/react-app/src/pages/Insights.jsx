import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Home, Filter } from 'lucide-react';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import PropertyCard from '../components/PropertyCard';
import { queryImages } from '../api';

const Insights = () => {
  const [analyticsData, setAnalyticsData] = useState({
    totalImages: 0,
    totalListings: 0,
    avgConditionScore: 0,
    totalConversations: 0,
  });
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch actual analytics from API
    // For now, use mock data
    setAnalyticsData({
      totalImages: 15,
      totalListings: 5,
      avgConditionScore: 0.78,
      totalConversations: 10,
    });
    
    // TODO: Fetch listings from API
    setListings([]);
    setLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Insights & Analytics</h1>
          <p className="text-gray-600">
            View property analytics, condition scores, and improvement recommendations
          </p>
        </div>

        {/* Analytics Dashboard */}
        <div className="mb-8">
          <AnalyticsDashboard data={analyticsData} />
        </div>

        {/* Listings Grid */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Home className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">Properties</h2>
            </div>
            <button className="btn-secondary flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filter
            </button>
          </div>

          {loading ? (
            <div className="card text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="text-gray-500 mt-4">Loading properties...</p>
            </div>
          ) : listings.length === 0 ? (
            <div className="card text-center py-12">
              <Home className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No properties found</p>
              <p className="text-gray-400 text-sm mt-1">Upload images to see property insights</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {listings.map((listing) => (
                <PropertyCard key={listing.id} listing={listing} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Insights;
