import React, { useState, useEffect } from 'react';
import { Upload, MessageCircle } from 'lucide-react';
import UploadForm from '../components/UploadForm';
import ImageGrid from '../components/ImageGrid';
import ChatPanel from '../components/ChatPanel';
import ImageDetailModal from '../components/ImageDetailModal';
import { getImage, queryImages } from '../api';

const Home = () => {
  const [uploadedImages, setUploadedImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleUploadSuccess = async (response) => {
    // Fetch full image details
    try {
      const imageDetails = await getImage(response.image_id);
      setUploadedImages((prev) => [imageDetails, ...prev]);
    } catch (error) {
      // If fetch fails, use response data
      setUploadedImages((prev) => [
        {
          id: response.image_id,
          filename: response.filename,
          predictions: response.predictions,
          s3_path: null,
        },
        ...prev,
      ]);
    }
  };

  const handleViewDetails = async (image) => {
    try {
      const imageDetails = await getImage(image.id);
      setSelectedImage(imageDetails);
      setShowModal(true);
    } catch (error) {
      setSelectedImage(image);
      setShowModal(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Real Estate AI Platform</h1>
          <p className="text-gray-600">
            Upload images, analyze properties, and get AI-powered home improvement advice
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload & Images */}
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Upload className="w-5 h-5 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">Image Upload</h2>
              </div>
              <UploadForm onUploadSuccess={handleUploadSuccess} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Uploaded Images</h2>
                {uploadedImages.length > 0 && (
                  <span className="text-sm text-gray-500">
                    {uploadedImages.length} {uploadedImages.length === 1 ? 'image' : 'images'}
                  </span>
                )}
              </div>
              <ImageGrid images={uploadedImages} onViewDetails={handleViewDetails} />
            </div>
          </div>

          {/* Right Column - Chat */}
          <div>
            <ChatPanel />
          </div>
        </div>
      </div>

      {/* Image Detail Modal */}
      {showModal && (
        <ImageDetailModal
          image={selectedImage}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default Home;
