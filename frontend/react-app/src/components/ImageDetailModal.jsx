import React from 'react';
import { X, Home, TrendingUp, Lightbulb, MapPin, Palette, Wrench, DollarSign, Tag } from 'lucide-react';

const ImageDetailModal = ({ image, onClose }) => {
  if (!image) return null;

  const predictions = image.predictions || image;

  const getConditionColor = (score) => {
    if (score >= 0.8) return 'text-green-700 bg-green-50 border-green-200';
    if (score >= 0.6) return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    return 'text-red-700 bg-red-50 border-red-200';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Image Details</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Image Preview */}
          <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
            {image.s3_path ? (
              <img 
                src={image.s3_path} 
                alt={image.filename || 'Property image'} 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                <Home className="w-16 h-16" />
              </div>
            )}
          </div>

          {/* Predictions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Room Type */}
            {predictions.room_type && (
              <DetailCard
                icon={Home}
                label="Room Type"
                value={predictions.room_type.label || predictions.room_type}
                confidence={predictions.room_type.confidence}
              />
            )}

            {/* Condition Score */}
            {predictions.condition_score !== undefined && (
              <DetailCard
                icon={TrendingUp}
                label="Condition"
                value={`${(predictions.condition_score * 100).toFixed(0)}%`}
                className={getConditionColor(predictions.condition_score)}
              />
            )}

            {/* Natural Light */}
            {predictions.natural_light_score !== undefined && (
              <DetailCard
                icon={Lightbulb}
                label="Natural Light"
                value={`${(predictions.natural_light_score * 100).toFixed(0)}%`}
              >
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-400 h-2 rounded-full" 
                    style={{ width: `${predictions.natural_light_score * 100}%` }}
                  />
                </div>
              </DetailCard>
            )}

            {/* Localization */}
            {predictions.localization && (
              <DetailCard
                icon={MapPin}
                label="Location"
                value={predictions.localization.label || predictions.localization}
                confidence={predictions.localization.confidence}
              />
            )}

            {/* Style */}
            {predictions.style && (
              <DetailCard
                icon={Palette}
                label="Style"
                value={predictions.style.label || predictions.style}
                confidence={predictions.style.confidence}
              />
            )}
          </div>

          {/* Features */}
          {predictions.feature_tags && predictions.feature_tags.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Tag className="w-5 h-5 text-gray-400" />
                <h3 className="text-lg font-semibold text-gray-900">Features</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {predictions.feature_tags.map((feature, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium"
                  >
                    {feature.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Work Recommendations */}
          {predictions.work_recommendations && predictions.work_recommendations.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Wrench className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-gray-900">Work Recommendations</h3>
              </div>
              <div className="space-y-3">
                {predictions.work_recommendations.map((rec, idx) => (
                  <div key={idx} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-medium text-gray-900">{rec.description || rec.type}</p>
                        <p className="text-sm text-gray-500 capitalize mt-1">{rec.type}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                        rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                    {rec.estimated_roi && (
                      <p className="text-sm text-gray-600">
                        Estimated ROI: {rec.estimated_roi.toFixed(1)}x
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cost Estimates */}
          {predictions.cost_estimates && predictions.cost_estimates.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <DollarSign className="w-5 h-5 text-green-600" />
                <h3 className="text-lg font-semibold text-gray-900">Cost Estimates</h3>
              </div>
              <div className="space-y-2">
                {predictions.cost_estimates.map((estimate, idx) => {
                  const rec = predictions.work_recommendations?.[idx];
                  return (
                    <div key={idx} className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <p className="font-medium text-gray-900 mb-1">
                        {rec?.description || `Recommendation ${idx + 1}`}
                      </p>
                      <p className="text-lg font-semibold text-green-700">
                        ${estimate.low_estimate?.toLocaleString()} - ${estimate.high_estimate?.toLocaleString()}
                        <span className="text-sm text-gray-600 ml-2">{estimate.currency || 'USD'}</span>
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Metadata */}
          {image.meta && (
            <div className="pt-4 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Metadata</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {image.filename && (
                  <div>
                    <span className="text-gray-500">Filename:</span>
                    <span className="ml-2 text-gray-900">{image.filename}</span>
                  </div>
                )}
                {predictions.model_version && (
                  <div>
                    <span className="text-gray-500">Model:</span>
                    <span className="ml-2 text-gray-900">{predictions.model_version}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const DetailCard = ({ icon: Icon, label, value, confidence, className = '', children }) => {
  return (
    <div className={`p-4 rounded-lg border ${className || 'bg-gray-50 border-gray-200'}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4 text-gray-400" />
        <p className="text-sm text-gray-500">{label}</p>
      </div>
      <p className="text-lg font-semibold text-gray-900 capitalize">{value}</p>
      {confidence && (
        <p className="text-xs text-gray-500 mt-1">Confidence: {(confidence * 100).toFixed(0)}%</p>
      )}
      {children}
    </div>
  );
};

export default ImageDetailModal;

