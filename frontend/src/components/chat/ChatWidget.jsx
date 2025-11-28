import { useState } from 'react';
import ChatWindow from './ChatWindow';
import './ChatWidget.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setIsExpanded(false);
    }
  };

  return (
    <div className="chat-widget-container">
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          className="chat-float-button"
          onClick={handleToggle}
          aria-label="Open chat"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <ChatWindow
          isExpanded={isExpanded}
          setIsExpanded={setIsExpanded}
          onClose={handleToggle}
        />
      )}
    </div>
  );
};

export default ChatWidget;
