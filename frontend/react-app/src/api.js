/** Axios API client for FastAPI backend */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload image (synchronous)
export const uploadImage = async (file, listingId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (listingId) {
    formData.append('listing_id', listingId);
  }

  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Upload image (asynchronous)
export const uploadImageAsync = async (file, listingId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (listingId) {
    formData.append('listing_id', listingId);
  }

  const response = await api.post('/upload/async', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Get task status
export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/tasks/${taskId}`);
  return response.data;
};

// Query similar images
export const queryImages = async (query, k = 6, listingId = null) => {
  const response = await api.post('/query/', {
    query,
    k,
    listing_id: listingId,
  });
  return response.data;
};

// Get image by ID
export const getImage = async (imageId) => {
  const response = await api.get(`/images/${imageId}`);
  return response.data;
};

// Get all listings
export const getListings = async () => {
  const response = await api.get('/listings');
  return response.data;
};

// Get listing by ID
export const getListing = async (listingId) => {
  const response = await api.get(`/listings/${listingId}`);
  return response.data;
};

// Get property aggregation
export const getPropertyAggregation = async (listingId) => {
  const response = await api.get(`/listings/${listingId}/aggregation`);
  return response.data;
};

// Chat with RAG
export const chat = async (message, conversationId = null, listingId = null, userId = null) => {
  const response = await api.post('/chat/', {
    message,
    conversation_id: conversationId,
    listing_id: listingId,
    user_id: userId,
  });
  return response.data;
};

// Get conversation messages
export const getConversationMessages = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}/messages`);
  return response.data;
};

export default api;

