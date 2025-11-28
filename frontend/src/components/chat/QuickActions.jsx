import './ChatWidget.css';

const QuickActions = ({ actions, onActionClick }) => {
  return (
    <div className="quick-actions">
      {actions.map(action => (
        <button
          key={action.id}
          className="quick-action-chip"
          onClick={() => onActionClick(action)}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
};

export default QuickActions;
