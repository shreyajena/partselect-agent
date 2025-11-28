import ChatWidget from '../components/chat/ChatWidget';
import './PartSelectDemo.css';
import psLogo from '../assets/ps-logo.svg';
import heroImage from '../assets/ps-section.png';
const PartSelectDemo = () => {
  const brands = ['Whirlpool', 'Samsung', 'LG', 'GE', 'Frigidaire', 'Maytag', 'KitchenAid', 'Bosch'];
  return <div className="partselect-demo">
      {/* Header */}
      <header className="demo-header">
        <div className="demo-header-top">
          <div className="demo-container">
            <div className="demo-logo">
              <img
                src={psLogo}
                alt="PartSelect logo"
                className="partselect-logo-img"
                draggable={false}
              />
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
        {/* Hero Screenshot */}
      <section className="demo-hero">
        <img
          src={heroImage}
          alt="PartSelect search hero"
          className="demo-hero-image"
          draggable={false}
        />
      </section>
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