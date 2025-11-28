import './ChatWidget.css';

const LinkButtons = ({ links = [], onAction }) => {
  if (!links.length) return null;

  return (
    <div className="link-buttons">
      {links.map((link, index) => {
        const key = `${link.label}-${index}`;
        if (link.url) {
          return (
            <a
              key={key}
              className="link-button link-button-primary"
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
              {link.label}
            </a>
          );
        }
        if (link.prompt && onAction) {
          return (
            <button
              key={key}
              className="link-button link-button-secondary"
              onClick={() => onAction(link.prompt, link.label)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              {link.label}
            </button>
          );
        }
        return null;
      })}
    </div>
  );
};

export default LinkButtons;

