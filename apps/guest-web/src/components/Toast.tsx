/**
 * Toast notification for user feedback.
 *
 * REQ-MENU-003: Confirmation message after pre-order action
 */

import { useEffect } from 'react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  onClose: () => void;
  duration?: number;
}

export function Toast({ message, type = 'success', onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  const iconMap = {
    success: '\u2713',
    error: '\u2717',
    info: '\u2139',
  };

  return (
    <div className={`toast toast-${type}`} role="alert" aria-live="polite">
      <span className="toast-icon">{iconMap[type]}</span>
      <span className="toast-message">{message}</span>
      <button className="toast-close" onClick={onClose} aria-label="Close">
        \u2715
      </button>

      <style>{`
        .toast {
          position: fixed;
          bottom: 24px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          z-index: 1000;
          animation: slideUp 0.3s ease-out;
          max-width: calc(100% - 32px);
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateX(-50%) translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
          }
        }
        .toast-success {
          background: var(--success);
          color: var(--white);
        }
        .toast-error {
          background: var(--danger);
          color: var(--white);
        }
        .toast-info {
          background: var(--primary);
          color: var(--white);
        }
        .toast-icon {
          font-size: 1.125rem;
          font-weight: bold;
        }
        .toast-message {
          font-size: 0.875rem;
          font-weight: 500;
        }
        .toast-close {
          background: none;
          border: none;
          color: inherit;
          opacity: 0.7;
          cursor: pointer;
          padding: 4px;
          font-size: 1rem;
        }
        .toast-close:hover {
          opacity: 1;
        }
      `}</style>
    </div>
  );
}
