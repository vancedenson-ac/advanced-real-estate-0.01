import React from 'react';
import { Home, Lightbulb, TrendingUp, MapPin, Palette, Wrench, DollarSign } from 'lucide-react';

const ImageCard = ({ image, onViewDetails }) => {
  const predictions = image.predictions || image;
  
  const getConditionColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      {/* Image Preview */}
      <div className="aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden">
        {image.s3_path ? (
          <img 
            src={image.s3_path} 
            alt={image.filename || 'Property image'} 
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <Home className="w-12 h-12" />
          </div>
        )}
      </div>

      {/* Predictions */}
      <div className="space-y-3">
        {/* Room Type */}
        {predictions.room_type && (
          <div className="flex items-center gap-2">
            <Home className="w-4 h-4 text-gray-400" />
            <div className="flex-1">
              <p className="text-xs text-gray-500">Room Type</p>
              <p className="text-sm font-medium text-gray-900 capitalize">
                {predictions.room_type.label || predictions.room_type}
              </p>
            </div>
            {predictions.room_type.confidence && (
              <span className="text-xs text-gray-500">
                {(predictions.room_type.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>
        )}

        {/* Condition Score */}
        {predictions.condition_score !== undefined && (
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-gray-400" />
            <div className="flex-1">
              <p className="text-xs text-gray-500">Condition</p>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${getConditionColor(predictions.condition_score)}`}>
                  {getScoreLabel(predictions.condition_score)}
                </span>
                <span className="text-xs text-gray-500">
                  {(predictions.condition_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Natural Light */}
        {predictions.natural_light_score !== undefined && (
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-gray-400" />
            <div className="flex-1">
              <p className="text-xs text-gray-500">Natural Light</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-400 h-2 rounded-full" 
                    style={{ width: `${predictions.natural_light_score * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-12 text-right">
                  {(predictions.natural_light_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Localization */}
        {predictions.localization && (
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-gray-400" />
            <div className="flex-1">
              <p className="text-xs text-gray-500">Location</p>
              <p className="text-sm font-medium text-gray-900 capitalize">
                {predictions.localization.label || predictions.localization}
              </p>
            </div>
          </div>
        )}

        {/* Style */}
        {predictions.style && (
          <div className="flex items-center gap-2">
            <Palette className="w-4 h-4 text-gray-400" />
            <div className="flex-1">
              <p className="text-xs text-gray-500">Style</p>
              <p className="text-sm font-medium text-gray-900 capitalize">
                {predictions.style.label || predictions.style}
              </p>
            </div>
          </div>
        )}

        {/* Features */}
        {predictions.feature_tags && predictions.feature_tags.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-1">Features</p>
            <div className="flex flex-wrap gap-1">
              {predictions.feature_tags.slice(0, 3).map((feature, idx) => (
                <span 
                  key={idx}
                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                >
                  {feature.replace(/_/g, ' ')}
                </span>
              ))}
              {predictions.feature_tags.length > 3 && (
                <span className="text-xs text-gray-500 px-2 py-1">
                  +{predictions.feature_tags.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Work Recommendations Summary */}
        {predictions.work_recommendations && predictions.work_recommendations.length > 0 && (
          <div className="pt-2 border-t border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Wrench className="w-4 h-4 text-primary-600" />
              <p className="text-xs font-medium text-gray-700">Recommendations</p>
            </div>
            <div className="space-y-1">
              {predictions.work_recommendations.slice(0, 2).map((rec, idx) => (
                <div key={idx} className="text-xs text-gray-600 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                  <span className="truncate">{rec.description || rec.type}</span>
                </div>
              ))}
              {predictions.work_recommendations.length > 2 && (
                <p className="text-xs text-gray-500 mt-1">
                  +{predictions.work_recommendations.length - 2} more
                </p>
              )}
            </div>
          </div>
        )}

        {/* Cost Estimates Summary */}
        {predictions.cost_estimates && predictions.cost_estimates.length > 0 && (
          <div className="pt-2 border-t border-gray-200">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-green-600" />
              <p className="text-xs font-medium text-gray-700">Est. Cost</p>
            </div>
            <div className="text-xs text-gray-600 mt-1">
              ${predictions.cost_estimates[0]?.low_estimate?.toLocaleString() || 0} - 
              ${predictions.cost_estimates[0]?.high_estimate?.toLocaleString() || 0}
            </div>
          </div>
        )}
      </div>

      {/* View Details Button */}
      {onViewDetails && (
        <button
          onClick={() => onViewDetails(image)}
          className="mt-4 w-full text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors"
        >
          View Details →
        </button>
      )}
    </div>
  );
};

export default ImageCard;

