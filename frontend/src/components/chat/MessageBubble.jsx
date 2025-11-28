import './ChatWidget.css';

const MessageBubble = ({ message }) => {
  return (
    <div className={`message-wrapper ${message.role}`}>
      <div className={`message-bubble ${message.role}`}>
        {message.content}
      </div>
    </div>
  );
};

export default MessageBubble;
