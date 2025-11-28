import ChatWidget from '../components/chat/ChatWidget';
import './PartSelectDemo.css';
const PartSelectDemo = () => {
  const brands = ['Whirlpool', 'Samsung', 'LG', 'GE', 'Frigidaire', 'Maytag', 'KitchenAid', 'Bosch'];
  return <div className="partselect-demo">
      {/* Header */}
      <header className="demo-header">
        <div className="demo-header-top">
          <div className="demo-container">
            <div className="demo-logo">
              <div className="demo-house-icon">🏠</div>
              <span className="demo-logo-text">PartSelect</span>
            </div>
            <nav className="demo-nav">
              <a href="#brand">Find by Brand</a>
              <a href="#product">Find by Product</a>
              <a href="#symptom">Find by Symptom</a>
              <a href="#contact">Contact</a>
              <a href="#blog">Blog</a>
              <a href="#repair">Repair Help</a>
              <a href="#filters">Water Filters</a>
            </nav>
          </div>
        </div>
        <div className="demo-support-ribbon">
          <div className="demo-container">
            <span>🎯 Free Expert Support • 7 Days a Week • 365 Days a Year</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="demo-main">
        <div className="demo-container">
          
        </div>
      </main>

      {/* Chat Widget */}
      <ChatWidget />
    </div>;
};
export default PartSelectDemo;