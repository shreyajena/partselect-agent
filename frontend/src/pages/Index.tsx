import ChatBot from "@/components/ChatBot";
import PartSelectDemo from "./PartSelectDemo";
const Index = () => {
  return <div className="min-h-screen bg-secondary">
      {/* New Production-Style Demo */}
      <div className="mb-8">
        <PartSelectDemo />
      </div>

      {/* Original Prototype Demo */}
      <div className="border-t-8 border-primary/20 bg-background">
      <header className="bg-background border-b border-border">
        
      </header>

      {/* Demo Page Content */}
      

      {/* Chatbot Widget */}
      <ChatBot />
      </div>
    </div>;
};
export default Index;