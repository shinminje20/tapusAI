/**
 * Loading screen component.
 */

interface LoadingScreenProps {
  message?: string;
}

export function LoadingScreen({ message = 'Loading...' }: LoadingScreenProps) {
  return (
    <div className="loading-screen">
      <div className="spinner"></div>
      <p>{message}</p>
      <style>{`
        .loading-screen {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          gap: 16px;
        }
        .loading-screen p {
          color: var(--gray-500);
        }
      `}</style>
    </div>
  );
}
