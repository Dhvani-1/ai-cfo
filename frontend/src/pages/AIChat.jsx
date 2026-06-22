import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import SectionHeader from '../components/SectionHeader';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';

const AIChat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hello! I am your AI CFO. Ask me questions about your uploaded financial statements and invoices, such as:\n\n• \"Why were my expenses high?\"\n• \"What was my salary income?\"\n• \"How much did I spend on food?\"\n• \"Which category is my largest expense?\""
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chat', { question: userMessage.content });
      setMessages((prev) => [...prev, { role: 'assistant', content: res.data.answer }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Sorry, I encountered an error answering your query. Please check your network connection and try again.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-10rem)]">
      <SectionHeader
        title="AI CFO Assistant"
        subtitle="Chat with your financial database, analyze category spending, or explore salary inflows."
      />

      <div className="flex-1 flex flex-col rounded-xl border border-slate-200 bg-white shadow-xs overflow-hidden">
        {/* Messages Viewport */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {messages.map((m, idx) => (
            <ChatMessage key={idx} role={m.role} content={m.content} />
          ))}
          {loading && (
            <div className="flex justify-start items-center gap-3 w-full">
              <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-indigo-105 text-xs font-bold text-indigo-600 border border-indigo-200">
                CFO
              </div>
              <div className="flex items-center space-x-1.5 rounded-2xl bg-slate-100 px-4 py-3 border border-slate-200 rounded-bl-none">
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '0ms' }}></span>
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '150ms' }}></span>
                <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <ChatInput value={input} onChange={setInput} onSend={handleSend} isLoading={loading} />
      </div>
    </div>
  );
};

export default AIChat;
