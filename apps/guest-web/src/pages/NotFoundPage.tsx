/**
 * Not Found page for invalid or missing tokens.
 *
 * REQ-MENU-005: Handle invalid SMS links gracefully
 */

interface NotFoundPageProps {
  message?: string;
}

export function NotFoundPage({ message }: NotFoundPageProps) {
  return (
    <div className="not-found-page">
      <div className="not-found-content">
        <div className="not-found-icon">
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M12 8v4M12 16h.01" />
          </svg>
        </div>
        <h1>Page Not Found</h1>
        <p>{message || "The page you're looking for doesn't exist or has expired."}</p>
        <p className="help-text">
          If you received an SMS link, please make sure you're using the complete URL.
        </p>
      </div>
      <style>{`
        .not-found-page {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          padding: 24px;
          text-align: center;
        }
        .not-found-content {
          max-width: 400px;
        }
        .not-found-icon {
          color: var(--gray-400);
          margin-bottom: 24px;
        }
        .not-found-page h1 {
          margin-bottom: 12px;
          color: var(--gray-800);
        }
        .not-found-page p {
          color: var(--gray-600);
          margin-bottom: 16px;
        }
        .help-text {
          font-size: 0.875rem;
          color: var(--gray-500);
        }
      `}</style>
    </div>
  );
}
