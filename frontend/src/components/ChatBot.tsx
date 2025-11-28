import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Maximize2, Minimize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
}

const quickActions = [
  { id: "repair", label: "Need repair help", response: "Sure — what appliance or part are you trying to repair?" },
  { id: "order", label: "Help me with my order", response: "I'd be happy to help with your order! Could you provide your order number?" },
  { id: "place", label: "Help me place an order", response: "Great! What part or appliance are you looking for?" },
  { id: "compatibility", label: "Part compatibility check", response: "I can help check part compatibility. What's the model number of your appliance?" },
  { id: "installation", label: "Installation instructions", response: "I can help with installation! What part do you need to install?" },
  { id: "track", label: "Track my order", response: "I'll help you track your order. What's your order number?" },
];

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [showQuickActions, setShowQuickActions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: action.label,
    };
    setMessages(prev => [...prev, userMessage]);
    setShowQuickActions(false);

    // Add assistant response after delay
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: action.response,
      };
      setMessages(prev => [...prev, assistantMessage]);
    }, 600);
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setShowQuickActions(false);

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
                <div className="h-10 w-10 rounded-full bg-primary-foreground/20 flex items-center justify-center font-bold text-lg">
                  PS
                </div>
                <div className="h-8 w-8 rounded-full bg-partselect-red flex items-center justify-center">
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

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-background border-t border-border">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your question…"
                  className="flex-1 rounded-full border-border focus-visible:ring-primary"
                />
                <Button
                  onClick={handleSend}
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
