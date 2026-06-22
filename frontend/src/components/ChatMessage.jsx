import React from 'react';

const ChatMessage = ({ role, content }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex items-start gap-3 w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Bot Avatar Icon */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-600 border border-indigo-200">
          CFO
        </div>
      )}

      {/* Bubble text */}
      <div
        className={`max-w-xl sm:max-w-2xl rounded-2xl px-4 py-3 text-xs leading-relaxed ${
          isUser
            ? 'bg-indigo-600 text-white rounded-tr-none text-right font-medium'
            : 'bg-slate-100 text-slate-805 rounded-tl-none text-left whitespace-pre-line border border-slate-200'
        }`}
      >
        {content}
      </div>

      {/* User Avatar Icon */}
      {isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-700 border border-slate-300">
          ME
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
