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
  } = product;

  const handleCompatibility = () => {
    if (!onPrompt) return;
    const prompt = `Is part ${id} compatible with my appliance model?`;
    onPrompt(prompt, `Check compatibility for ${id}`);
  };

  return (
    <div className="product-card">
      <div className="product-card-header">
        <div className="product-card-title">{name || 'Part details'}</div>
        {price && <div className="product-card-price">{formatPrice(price)}</div>}
      </div>
      <div className="product-card-body">
        {applianceType && (
          <div className="product-card-row">
            <span>Appliance:</span>
            <strong>{applianceType}</strong>
          </div>
        )}
        {installDifficulty && (
          <div className="product-card-row">
            <span>Install difficulty:</span>
            <strong>{installDifficulty}</strong>
          </div>
        )}
        {installTime && (
          <div className="product-card-row">
            <span>Install time:</span>
            <strong>{installTime}</strong>
          </div>
        )}
      </div>
      <div className="product-card-actions">
        {url && (
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="product-card-btn primary"
          >
            View product
          </a>
        )}
        <button type="button" className="product-card-btn" onClick={handleCompatibility}>
          Check compatibility
        </button>
      </div>
    </div>
  );
};

export default ProductCard;

