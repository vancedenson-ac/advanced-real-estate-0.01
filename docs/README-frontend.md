# Frontend Documentation

Frontend components for the Real Estate AI Platform, providing user interfaces for property management, image upload, and AI-powered chat assistance.

## Overview

The frontend consists of two main applications:

1. **React Application** - Production-ready UI for property management and analysis
2. **Gradio Interface** - Quick testing and experimentation interface for API endpoints

## Architecture

```
frontend/
├── react-app/              # React production UI
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── api.js          # API client
│   │   └── App.js          # Main app component
│   ├── public/             # Static assets
│   └── package.json        # Dependencies
└── gradio-interface/        # Gradio testing UI
    ├── app.py              # Gradio application
    └── requirements.txt    # Python dependencies
```

## React Application

### Features

- **Image Upload**: Drag-and-drop or file picker for property images
  - Synchronous upload with immediate results
  - Asynchronous upload with task status polling
- **Image Grid**: Display uploaded images with predictions and metadata
- **Chat Panel**: RAG-powered AI assistant for property improvement advice
- **Analytics Dashboard**: Overview of property statistics and insights
- **Responsive Design**: Mobile-friendly interface

### Components

#### UploadForm
- Handles image upload (sync/async modes)
- Displays upload progress and results
- Shows prediction results after upload

#### ImageGrid
- Displays uploaded images in a grid layout
- Shows room type, condition scores, features
- Image previews with metadata

#### ChatPanel
- Interactive chat interface
- RAG-powered responses with property context
- Conversation history
- Message threading

#### AnalyticsDashboard
- Property statistics overview
- Condition score averages
- Total images and listings count
- Conversation metrics

### Pages

#### Home
- Main landing page
- Upload form and image grid
- Chat panel side-by-side

#### Insights
- Analytics dashboard
- Property statistics
- Performance metrics

## Gradio Interface

### Purpose

Quick testing and experimentation interface for API endpoints without building a full UI.

### Features

- **Upload Tab**: Test image upload endpoints
- **Query Tab**: Test image similarity search
- **Chat Tab**: Test RAG chat functionality
- **Get Image Tab**: Retrieve image metadata

### Usage

Access at http://localhost:7860 when running via Docker Compose.

## Development

### Prerequisites

- Node.js 18+ (for React app)
- Python 3.11+ (for Gradio interface)
- npm or yarn

### React App Setup

1. **Install dependencies:**
```bash
cd frontend/react-app
npm install
```

2. **Start development server:**
```bash
npm start
```

The app will be available at http://localhost:3000

3. **Build for production:**
```bash
npm run build
```

### Gradio Interface Setup

1. **Install dependencies:**
```bash
cd frontend/gradio-interface
pip install -r requirements.txt
```

2. **Run locally:**
```bash
python app.py
```

Access at http://localhost:7860

### API Client

The React app uses an Axios-based API client (`src/api.js`) with the following methods:

- `uploadImage(file, listingId)` - Synchronous image upload
- `uploadImageAsync(file, listingId)` - Asynchronous image upload
- `getTaskStatus(taskId)` - Get async task status
- `queryImages(query, k, listingId)` - Search similar images
- `getImage(imageId)` - Get image metadata
- `chat(message, conversationId, listingId, userId)` - RAG chat
- `getConversationMessages(conversationId)` - Get conversation history

### Environment Variables

Create `.env` in `react-app/`:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

For Docker, the API URL is automatically configured via nginx proxy.

## Docker Deployment

### React App

The React app is containerized with a multi-stage build:

1. Build stage: Compiles React app
2. Production stage: Serves via nginx

```bash
docker build -t realestate-frontend ./frontend/react-app
```

### Gradio Interface

Simple Python container:

```bash
docker build -t realestate-gradio ./frontend/gradio-interface
```

## API Integration

### Endpoints Used

- `POST /api/upload/` - Synchronous image upload
- `POST /api/upload/async` - Asynchronous image upload
- `GET /api/tasks/{task_id}` - Task status
- `POST /api/query/` - Image similarity search
- `GET /api/images/{image_id}` - Image metadata
- `POST /api/chat/` - RAG chat
- `GET /api/conversations/{conversation_id}/messages` - Conversation history

See [README-backend.md](README-backend.md#api-endpoints) for detailed API documentation.

## Styling

- CSS Modules for component-specific styles
- Global styles in `index.css` and `App.css`
- Responsive design with CSS Grid and Flexbox
- Mobile-first approach

## State Management

Currently uses React hooks for local state management. For complex state, consider:

- Redux or Zustand for global state
- React Query for server state caching
- Context API for theme/user preferences

## Testing

### Quick Test Commands

**Using Make:**
```bash
make test        # Run all backend tests
make test-cov    # Run backend tests with coverage
```

**Frontend Testing:**
Frontend testing is not yet implemented. Recommended tools:

- **Jest** - Unit testing
- **React Testing Library** - Component testing
- **Cypress** - End-to-end testing

## Performance Considerations

- Image lazy loading for ImageGrid
- Pagination for large image lists
- Debounced search queries
- Optimistic UI updates
- Service worker for offline support (future)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

- [ ] Image preview with zoom
- [ ] Drag-and-drop image reordering
- [ ] Batch image upload
- [ ] Image filtering and search
- [ ] Property comparison view
- [ ] Export reports (PDF/CSV)
- [ ] Dark mode theme
- [ ] Internationalization (i18n)
- [ ] Progressive Web App (PWA) support

## Troubleshooting

### CORS Issues

If accessing API from different origin, ensure backend CORS is configured:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)
```

### API Connection Issues

- Verify backend is running on port 8000
- Check nginx configuration for API proxy
- Ensure environment variables are set correctly

### Build Issues

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version compatibility
- Verify all dependencies are installed

## Quick Commands

### Development

```bash
make dev-frontend  # Start frontend with hot reload
make start         # Start all services
make stop          # Stop all services
make logs          # View logs
```

### Testing

```bash
make test          # Run backend tests
make test-cov      # Run tests with coverage
```

## Related Documentation

- [Backend API Documentation](README-backend.md)
- [Middleware Setup](README-middleware.md)
- [Testing Documentation](README-tests.md)
- [Main README](README.md)

