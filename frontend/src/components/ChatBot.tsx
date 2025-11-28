import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Maximize2, Minimize2 } from "lucide-react";
import psLogo from "@/assets/ps-logo.svg";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
}

const quickActions = [
  {
    id: 'repair',
    label: 'Get repair help',
    starterText: "Tell me what's wrong with your refrigerator or dishwasher and I'll help you diagnose the issue or find the right repair steps.",
    examples: [
      'The ice maker on my Whirlpool fridge is not working. How can I fix it?',
      'My dishwasher is leaking from the bottom. What do I do?',
    ],
  },
  {
    id: 'compatible',
    label: 'Find compatible parts',
    starterText: 'Give me your model number (e.g., WDT780SAEM1) and I\'ll show you parts that are guaranteed to fit.',
    examples: [
      'Is PS11752778 compatible with Whirlpool WDT780SAEM1?',
      'Does WPW10321304 fit my fridge?',
    ],
  },
  {
    id: 'order',
    label: 'Help me with my order',
    starterText: 'Share your order number and I can help you check status, shipping details, or returns.',
    examples: [
      'What is the status of order #2?',
      'Help me track Order #1',
    ],
  },
  {
    id: 'usage',
    label: 'How do I use this?',
    starterText: 'Ask me about dishwasher or refrigerator cycles, settings, or usage tips, and I\'ll explain what they do based on PartSelect guides.',
    examples: [
      'What is eco mode on a dishwasher?',
      'How do I reset my refrigerator?',
    ],
  },
];

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [currentExamples, setCurrentExamples] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Initial greeting messages
      setTimeout(() => {
        setMessages([
          {
            id: "1",
            type: "assistant",
            content: "Hi, I'm Selecto — your buddy for all things PartSelect!",
          },
        ]);
      }, 300);
      
      setTimeout(() => {
        setMessages(prev => [
          ...prev,
          {
            id: "2",
            type: "assistant",
            content: "You can chat freely or choose from the quick options below.",
          },
        ]);
      }, 800);
    }
  }, [isOpen]);

  const handleQuickAction = (action: typeof quickActions[0]) => {
    if (action.starterText) {
      // Add assistant message with starter text
      const assistantMessage: Message = {
        id: Date.now().toString(),
        type: "assistant",
        content: action.starterText,
      };
      setMessages(prev => [...prev, assistantMessage]);
      setShowQuickActions(false);
      setCurrentExamples(action.examples || []);
      
      // Focus the input so user can type their response
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    } else {
      // Fallback to old behavior
      const userMessage: Message = {
        id: Date.now().toString(),
        type: "user",
        content: action.label,
      };
      setMessages(prev => [...prev, userMessage]);
      setShowQuickActions(false);
    }
  };

  const handleExampleClick = (exampleText: string) => {
    setInputValue(exampleText);
    handleSend(exampleText);
  };

  const handleSend = (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: messageText,
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setShowQuickActions(false);
    setCurrentExamples([]);

    // Add mock assistant response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "This is a prototype response from Selecto. In the full version, I'd provide helpful information about your question!",
      };
      setMessages(prev => [...prev, assistantMessage]);
    }, 600);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <Button
              onClick={() => setIsOpen(true)}
              className="h-16 w-16 rounded-full bg-primary shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 group"
              style={{ boxShadow: "0 8px 32px rgba(27, 56, 117, 0.3)" }}
            >
              <MessageCircle className="h-7 w-7 text-primary-foreground group-hover:scale-110 transition-transform" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: isExpanded ? 0 : 100, scale: isExpanded ? 1 : 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: isExpanded ? 0 : 100, scale: isExpanded ? 1 : 0.8 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className={`fixed z-50 bg-background shadow-2xl flex flex-col overflow-hidden ${
              isExpanded 
                ? "inset-4 rounded-3xl" 
                : "bottom-6 right-6 w-[380px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-3rem)] rounded-2xl"
            }`}
            style={{ boxShadow: "0 8px 32px rgba(27, 56, 117, 0.2)" }}
          >
            {/* Header */}
            <div className="bg-primary text-primary-foreground p-4 flex items-center gap-3">
              <div className="flex items-center gap-3 flex-1">
                <img
                  src={psLogo}
                  alt="PartSelect logo"
                  className="h-10 w-auto rounded-md bg-white/95 p-1 shadow-sm"
                />
                <div className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center">
                  <span className="text-lg">🤖</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">Selecto — Your Parts Buddy</h3>
                  <p className="text-xs text-primary-foreground/80">Ask me anything about repairs, parts, or your order.</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  onClick={() => setIsExpanded(!isExpanded)}
                  variant="ghost"
                  size="icon"
                  className="text-primary-foreground hover:bg-primary-foreground/20 rounded-full"
                  title={isExpanded ? "Minimize" : "Expand"}
                >
                  {isExpanded ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
                </Button>
                <Button
                  onClick={() => {
                    setIsOpen(false);
                    setIsExpanded(false);
                  }}
                  variant="ghost"
                  size="icon"
                  className="text-primary-foreground hover:bg-primary-foreground/20 rounded-full"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-secondary/30">
              <AnimatePresence initial={false}>
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.type === "user"
                          ? "bg-chat-user text-chat-user-foreground rounded-br-sm"
                          : "bg-chat-assistant text-chat-assistant-foreground rounded-bl-sm"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Quick Actions */}
              {showQuickActions && messages.length >= 2 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="flex flex-wrap gap-2 pt-2"
                >
                  {quickActions.map((action) => (
                    <motion.button
                      key={action.id}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleQuickAction(action)}
                      className="px-4 py-2 bg-background border border-border rounded-full text-sm font-medium text-foreground hover:bg-secondary transition-colors"
                    >
                      {action.label}
                    </motion.button>
                  ))}
                </motion.div>
              )}

              {/* Example Prompts */}
              {currentExamples.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="pt-2 px-4"
                >
                  <div className="text-xs text-muted-foreground mb-2">Try these examples:</div>
                  <div className="flex flex-wrap gap-2">
                    {currentExamples.map((example, idx) => (
                      <motion.button
                        key={idx}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleExampleClick(example)}
                        className="px-3 py-1.5 bg-secondary border border-border rounded-full text-xs font-medium text-foreground hover:bg-secondary/80 transition-colors"
                      >
                        {example}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-background border-t border-border">
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleSend();
                    }
                  }}
                  placeholder="Type your question…"
                  className="flex-1 rounded-full border-border focus-visible:ring-primary"
                />
                <Button
                  onClick={() => handleSend()}
                  size="icon"
                  className="rounded-full bg-primary hover:bg-primary/90 h-10 w-10"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatBot;
