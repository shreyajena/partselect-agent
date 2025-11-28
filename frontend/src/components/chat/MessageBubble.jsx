import './ChatWidget.css';
import ProductCard from './ProductCard';
import OrderCard from './OrderCard';
import LinkButtons from './LinkButtons';

const MessageBubble = ({ message, onPrompt }) => {
  const metadata = message.metadata || {};
  const productMeta =
    metadata.type === 'product_info' ? metadata.product : null;
  const orderMeta =
    metadata.type === 'order_info' ? metadata.order : null;
  const linksMeta = metadata.type === 'links' ? metadata.links : null;

  // Split content by newlines for better formatting
  const contentLines = message.content.split('\n').filter(line => line.trim());

  return (
    <div className={`message-wrapper ${message.role}`}>
      <div className={`message-bubble ${message.role}`}>
        {message.role === 'assistant' && (
          <div className="message-avatar">🤖</div>
        )}
        <div className="message-content-wrapper">
          <div className="message-text">
            {contentLines.map((line, idx) => (
              <p key={idx} className="message-text-line">
                {line}
              </p>
            ))}
          </div>
          {productMeta && (
            <div className="message-metadata">
              <ProductCard product={productMeta} onPrompt={onPrompt} />
            </div>
          )}
          {orderMeta && (
            <div className="message-metadata">
              <OrderCard order={orderMeta} onPrompt={onPrompt} />
            </div>
          )}
          {linksMeta && (
            <div className="message-metadata">
              <LinkButtons links={linksMeta} onAction={onPrompt} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
