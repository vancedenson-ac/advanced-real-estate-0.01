import React from 'react';
import { MapPin, DollarSign, Home, TrendingUp, Image as ImageIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

const PropertyCard = ({ listing, onViewDetails }) => {
  const aggregation = listing.aggregation || {};
  
  return (
    <Link
      to={`/listings/${listing.id}`}
      className="card hover:shadow-md transition-shadow duration-200 block"
    >
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{listing.address}</h3>
        <div className="flex items-center gap-1 text-sm text-gray-500">
          <MapPin className="w-4 h-4" />
          <span>{listing.city}, {listing.state} {listing.zip_code}</span>
        </div>
      </div>

      {/* Price */}
      <div className="flex items-baseline gap-2 mb-4">
        <DollarSign className="w-5 h-5 text-primary-600" />
        <span className="text-2xl font-bold text-gray-900">
          ${listing.price?.toLocaleString() || 'N/A'}
        </span>
        {listing.estimated_price && (
          <span className="text-sm text-gray-500">
            (Est: ${listing.estimated_price.toLocaleString()})
          </span>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <ImageIcon className="w-4 h-4 text-gray-400" />
          <div>
            <p className="text-xs text-gray-500">Images</p>
            <p className="text-sm font-medium text-gray-900">
              {listing.total_images || aggregation.total_images || 0}
            </p>
          </div>
        </div>
        
        {aggregation.overall_condition_score !== undefined && (
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Condition</p>
              <p className="text-sm font-medium text-gray-900">
                {(aggregation.overall_condition_score * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        )}

        {aggregation.dominant_room_type && (
          <div className="flex items-center gap-2">
            <Home className="w-4 h-4 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Dominant Room</p>
              <p className="text-sm font-medium text-gray-900 capitalize">
                {aggregation.dominant_room_type}
              </p>
            </div>
          </div>
        )}

        {aggregation.dominant_style && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Style</span>
            <p className="text-sm font-medium text-gray-900 capitalize">
              {aggregation.dominant_style}
            </p>
          </div>
        )}
      </div>
    </Link>
  );
};

export default PropertyCard;

