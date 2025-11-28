import './ChatWidget.css';

const formatPrice = (price) => {
  if (!price) return null;
  const num = Number(price);
  if (Number.isNaN(num)) return price;
  return `$${num.toFixed(2)}`;
};

const ProductCard = ({ product, onPrompt }) => {
  if (!product) return null;

  const {
    id,
    name,
    price,
    url,
    symptoms,
    installDifficulty,
    installTime,
    applianceType,
    brand,
  } = product;

  const handleCompatibility = () => {
    if (!onPrompt) return;
    const prompt = `Is part ${id} compatible with my appliance model?`;
    onPrompt(prompt, `Check compatibility for ${id}`);
  };

  // Parse symptoms if it's a string
  const symptomList = symptoms 
    ? (typeof symptoms === 'string' 
        ? symptoms.split(',').map(s => s.trim()).filter(Boolean)
        : Array.isArray(symptoms) ? symptoms : [])
    : [];

  return (
    <div className="product-card">
      <div className="product-card-header">
        <div className="product-card-header-left">
          <div className="product-card-title">{name || 'Part details'}</div>
          {id && (
            <div className="product-card-id">Part ID: {id}</div>
          )}
        </div>
        {price && (
          <div className="product-card-price-wrapper">
            <div className="product-card-price">{formatPrice(price)}</div>
          </div>
        )}
      </div>
      
      <div className="product-card-body">
        {(brand || applianceType) && (
          <div className="product-card-row">
            <span className="product-card-label">Brand/Type:</span>
            <strong className="product-card-value">
              {brand && applianceType ? `${brand} ${applianceType}` : brand || applianceType}
            </strong>
          </div>
        )}
        
        {installDifficulty && (
          <div className="product-card-row">
            <span className="product-card-label">Install difficulty:</span>
            <strong className={`product-card-value product-card-difficulty product-card-difficulty-${installDifficulty.toLowerCase().replace(/\s+/g, '-')}`}>
              {installDifficulty}
            </strong>
          </div>
        )}
        
        {installTime && (
          <div className="product-card-row">
            <span className="product-card-label">Install time:</span>
            <strong className="product-card-value">{installTime}</strong>
          </div>
        )}
      </div>
      
      <div className="product-card-actions">
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="product-card-btn product-card-btn-primary"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
            View product
          </a>
        )}
        <button 
          type="button" 
          className="product-card-btn product-card-btn-secondary" 
          onClick={handleCompatibility}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 11l3 3L22 4"></path>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path>
          </svg>
          Check compatibility
        </button>
      </div>
    </div>
  );
};

export default ProductCard;

