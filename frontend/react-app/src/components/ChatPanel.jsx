import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Loader2 } from 'lucide-react';
import { chat, getConversationMessages } from '../api';

const ChatPanel = ({ listingId = null, userId = null }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to UI
    const newUserMessage = { role: 'user', text: userMessage };
    setMessages((prev) => [...prev, newUserMessage]);
    setLoading(true);

    try {
      const response = await chat(userMessage, conversationId, listingId, userId);
      
      // Update conversation ID if it's a new conversation
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant reply
      const assistantMessage = { role: 'assistant', text: response.reply };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        text: `Error: ${error.response?.data?.detail || error.message || 'Unknown error'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card flex flex-col h-[600px]">
      <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-200">
        <MessageCircle className="w-5 h-5 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">Chat Assistant</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <MessageCircle className="w-12 h-12 text-gray-300 mb-4" />
            <p className="text-gray-500 text-sm">
              Start a conversation by asking about home improvements, room features, or property value.
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSend} className="border-t border-gray-200 pt-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about home improvements..."
            disabled={loading}
            className="input flex-1"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="btn-primary flex items-center gap-2 px-4"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
