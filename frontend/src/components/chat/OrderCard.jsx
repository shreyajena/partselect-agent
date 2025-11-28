import './ChatWidget.css';

const formatPrice = (price) => {
  if (!price) return null;
  const num = Number(price);
  if (Number.isNaN(num)) return price;
  return `$${num.toFixed(2)}`;
};

const formatDate = (dateString) => {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return null;
  }
};

const getStatusColor = (status) => {
  const statusLower = status?.toLowerCase() || '';
  if (statusLower.includes('delivered') || statusLower.includes('completed')) {
    return 'order-status-delivered';
  }
  if (statusLower.includes('shipped') || statusLower.includes('processing')) {
    return 'order-status-shipped';
  }
  if (statusLower.includes('cancelled') || statusLower.includes('returned')) {
    return 'order-status-cancelled';
  }
  return 'order-status-pending';
};

const OrderCard = ({ order, onPrompt }) => {
  if (!order) return null;

  const {
    id,
    status,
    date,
    shippingType,
    partName,
    partId,
    partUrl,
    amount,
    transactionStatus,
    returnEligible,
  } = order;

  return (
    <div className="order-card">
      <div className="order-card-header">
        <div className="order-card-header-left">
          <div className="order-card-title">Order #{id}</div>
          <div className={`order-card-status ${getStatusColor(status)}`}>
            {status?.toUpperCase() || 'PENDING'}
          </div>
        </div>
        {amount && (
          <div className="order-card-amount-wrapper">
            <div className="order-card-amount">{formatPrice(amount)}</div>
          </div>
        )}
      </div>
      
      <div className="order-card-body">
        {date && (
          <div className="order-card-row">
            <span className="order-card-label">Order date:</span>
            <strong className="order-card-value">{formatDate(date)}</strong>
          </div>
        )}
        
        {shippingType && (
          <div className="order-card-row">
            <span className="order-card-label">Shipping:</span>
            <strong className="order-card-value">{shippingType}</strong>
          </div>
        )}

        {partName && (
          <div className="order-card-row">
            <span className="order-card-label">Part:</span>
            <strong className="order-card-value">{partName}</strong>
          </div>
        )}

        {transactionStatus && (
          <div className="order-card-row">
            <span className="order-card-label">Payment:</span>
            <strong className="order-card-value">{transactionStatus}</strong>
          </div>
        )}
      </div>
      
      <div className="order-card-actions">
        {partUrl && (
          <a
            href={partUrl}
            target="_blank"
            rel="noreferrer"
            className="order-card-btn order-card-btn-primary"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
            View part
          </a>
        )}
        {returnEligible && (
          <>
            <a
              href="https://www.partselect.com/user/self-service/"
              target="_blank"
              rel="noreferrer"
              className="order-card-btn order-card-btn-primary"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                <path d="M21 3v5h-5"></path>
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                <path d="M3 21v-5h5"></path>
              </svg>
              Return order
            </a>
            <button 
              type="button" 
              className="order-card-btn order-card-btn-secondary" 
              onClick={() => onPrompt && onPrompt(`I want to return order #${id}`, `Return order #${id}`)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              Chat about Return
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default OrderCard;

