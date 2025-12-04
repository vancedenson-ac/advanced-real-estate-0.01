import React, { useState } from 'react';
import { Upload, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { uploadImage, uploadImageAsync } from '../api';

const UploadForm = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [asyncMode, setAsyncMode] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      if (asyncMode) {
        const response = await uploadImageAsync(file);
        setTaskId(response.task_id);
        setResult({ status: 'queued', task_id: response.task_id });
      } else {
        const response = await uploadImage(file);
        setResult(response);
        if (onUploadSuccess) {
          onUploadSuccess(response);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-6">
        <Upload className="w-5 h-5 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">Upload Image</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="async-mode"
            checked={asyncMode}
            onChange={(e) => setAsyncMode(e.target.checked)}
            className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            disabled={uploading}
          />
          <label htmlFor="async-mode" className="text-sm text-gray-600">
            Async Mode (Celery worker)
          </label>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Image
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={uploading}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer disabled:opacity-50"
          />
        </div>
        
        <button
          type="submit"
          disabled={uploading || !file}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4" />
              Upload
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start gap-3 mb-2">
            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-green-900 mb-1">Upload Successful</h3>
              {result.status === 'success' && (
                <div className="text-sm text-green-700 space-y-1">
                  <p>Image ID: {result.image_id}</p>
                  <p>Filename: {result.filename}</p>
                </div>
              )}
              {taskId && (
                <p className="text-sm text-green-700 mt-2">
                  Task ID: <code className="bg-green-100 px-2 py-1 rounded text-xs">{taskId}</code>
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadForm;
