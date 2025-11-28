import './ChatWidget.css';

const QuickActions = ({ actions, onActionClick }) => {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="quick-actions">
      <div className="quick-actions-label">Quick actions:</div>
      <div className="quick-actions-chips">
        {actions.map(action => (
          <button
            key={action.id}
            className="quick-action-chip"
            onClick={() => onActionClick(action)}
            aria-label={action.label}
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;
