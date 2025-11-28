import { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import QuickActions from './QuickActions';
import './ChatWidget.css';
import { sendChatMessage } from '../../api/chat';
import psLogo from '../../assets/ps-logo.svg';

const QUICK_ACTIONS = [
  {
    id: 'repair',
    label: 'Need repair help',
    prompt: 'My dishwasher is leaking. What should I check first?',
  },
  {
    id: 'order',
    label: 'Help me with my order',
    prompt: 'Track my order #1',
  },
  {
    id: 'compatible',
    label: 'Find compatible parts',
    prompt: 'Is part PS11752778 compatible with WDT780SAEM1?',
  },
  {
    id: 'place',
    label: 'Help me place an order',
    prompt: 'I want to order a replacement ice maker for my Whirlpool fridge.',
  },
  {
    id: 'track',
    label: 'Track my order',
    prompt: 'Where is my order #2?',
  },
];

const ChatWindow = ({ isExpanded, setIsExpanded, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Hi, I'm Selecto — your buddy for all things PartSelect!",
    },
    {
      id: 2,
      role: 'assistant',
      content:
        'Currently, I can help with dishwasher and refrigerator parts, repairs, and your order. You can start typing, or pick one of the quick options below.',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const addMessage = (role, content, metadata = null) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      role,
      content,
      metadata,
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleQuickAction = (action) => {
    sendMessage(action.prompt || action.label, action.label);
  };

  const sendMessage = async (text, displayText) => {
    const messageText = text?.trim();
    if (!messageText || isTyping) return;

    addMessage('user', displayText || text);
    setShowQuickActions(false);
    setIsTyping(true);

    try {
      const { reply, metadata } = await sendChatMessage(messageText);
      addMessage('assistant', reply, metadata || null);
    } catch (error) {
      addMessage(
        'assistant',
        "I'm having trouble reaching the PartSelect service right now. Please try again in a moment."
      );
      // eslint-disable-next-line no-console
      console.error('Chat API error:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = () => {
    if (!inputValue.trim() || isTyping) return;
    const currentInput = inputValue;
    setInputValue('');
    sendMessage(currentInput);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`chat-window ${isExpanded ? 'expanded' : 'floating'}`}>
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="chat-header-logo-wrapper">
            <img
              src={psLogo}
              alt="PartSelect logo"
              className="partselect-logo-img"
              draggable={false}
            />
          </div>
          <div className="selecto-avatar-wrapper">
            <div className="selecto-avatar">🤖</div>
            <div className="selecto-status-indicator"></div>
          </div>
          <div className="chat-header-text">
            <div className="chat-title">Selecto — Your Parts Buddy</div>
            <div className="chat-subtitle">Ask me anything about dishwasher/refrigerator parts, repairs, or your order.</div>
          </div>
        </div>
        <div className="chat-header-right">
          <button
            className="chat-header-button"
            onClick={() => setIsExpanded(!isExpanded)}
            aria-label={isExpanded ? 'Minimize' : 'Expand'}
            title={isExpanded ? 'Minimize' : 'Expand'}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {isExpanded ? (
                <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
              ) : (
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
              )}
            </svg>
          </button>
          <button
            className="chat-header-button"
            onClick={onClose}
            aria-label="Close"
            title="Close chat"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} onPrompt={sendMessage} />
        ))}

        {showQuickActions && messages.length <= 2 && (
          <QuickActions actions={QUICK_ACTIONS} onActionClick={handleQuickAction} />
        )}

        {isTyping && (
          <div className="typing-indicator">
            <div className="typing-bubble">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder="Type your question…"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isTyping}
          />
          {inputValue.trim() && (
            <button
              className="chat-clear-button"
              onClick={() => setInputValue('')}
              aria-label="Clear input"
              title="Clear"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          )}
        </div>
        <button
          className={`chat-send-button ${isTyping ? 'disabled' : ''}`}
          onClick={handleSend}
          aria-label="Send message"
          disabled={isTyping || !inputValue.trim()}
          title="Send message"
        >
          {isTyping ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="spinning">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 6v6l4 2"></path>
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
