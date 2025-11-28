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
    { id: 1, role: 'assistant', content: "Hi, I'm Selecto — your buddy for all things PartSelect!" },
    { id: 2, role: 'assistant', content: 'Currently, I can help with dishwasher and refrigerator parts, repairs, and your order. You can start typing, or pick one of the quick options below.' },
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

  const addMessage = (role, content) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      role,
      content,
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
      const { reply } = await sendChatMessage(messageText);
      addMessage('assistant', reply);
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
          <img
            src={psLogo}
            alt="PartSelect logo"
            className="partselect-logo-img"
            draggable={false}
          />
          <div className="selecto-avatar">🤖</div>
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
          >
            {isExpanded ? '⤡' : '⤢'}
          </button>
          <button
            className="chat-header-button"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
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
        <input
          ref={inputRef}
          type="text"
          className="chat-input"
          placeholder="Type your question…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button
          className="chat-send-button"
          onClick={handleSend}
          aria-label="Send message"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
