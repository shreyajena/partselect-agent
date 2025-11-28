import './ChatWidget.css';
import ProductCard from './ProductCard';

const MessageBubble = ({ message, onPrompt }) => {
  const productMeta =
    message.metadata && message.metadata.type === 'product_info'
      ? message.metadata.product
      : null;

  return (
    <div className={`message-wrapper ${message.role}`}>
      <div className={`message-bubble ${message.role}`}>
        <p className="message-text">{message.content}</p>
        {productMeta && (
          <ProductCard product={productMeta} onPrompt={onPrompt} />
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
