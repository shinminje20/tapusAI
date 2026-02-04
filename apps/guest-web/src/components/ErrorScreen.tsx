/**
 * Error screen component for displaying errors.
 */

interface ErrorScreenProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorScreen({
  title = 'Something went wrong',
  message,
  onRetry,
}: ErrorScreenProps) {
  return (
    <div className="error-screen">
      <div className="error-icon">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M15 9l-6 6M9 9l6 6" />
        </svg>
      </div>
      <h2>{title}</h2>
      <p>{message}</p>
      {onRetry && (
        <button className="btn btn-primary" onClick={onRetry}>
          Try Again
        </button>
      )}
      <style>{`
        .error-screen {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          padding: 24px;
          text-align: center;
          gap: 16px;
        }
        .error-icon {
          color: var(--danger);
        }
        .error-screen h2 {
          color: var(--gray-800);
          margin: 0;
        }
        .error-screen p {
          color: var(--gray-600);
          max-width: 300px;
        }
      `}</style>
    </div>
  );
}
