import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Insights from './pages/Insights';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <nav className="bg-white border-b border-gray-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-xl font-bold text-gray-900">Real Estate AI</h1>
              <div className="flex gap-6">
                <a href="/" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                  Home
                </a>
                <a href="/insights" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                  Insights
                </a>
              </div>
            </div>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/insights" element={<Insights />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
