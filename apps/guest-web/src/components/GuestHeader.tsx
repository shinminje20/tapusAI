/**
 * Guest header component showing waitlist status.
 *
 * AC-MENU-001: Guest sees their waitlist position and ETA
 */

import type { GuestContext } from '../services/api';

interface GuestHeaderProps {
  guest: GuestContext;
}

export function GuestHeader({ guest }: GuestHeaderProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'waiting':
        return 'var(--warning)';
      case 'notified':
        return 'var(--success)';
      case 'seated':
        return 'var(--primary)';
      default:
        return 'var(--gray-500)';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'waiting':
        return 'In Queue';
      case 'notified':
        return 'Your Table is Ready!';
      case 'seated':
        return 'Seated';
      case 'cancelled':
        return 'Cancelled';
      case 'no_show':
        return 'No Show';
      default:
        return status;
    }
  };

  return (
    <header className="guest-header">
      <div className="guest-welcome">
        <h1>Welcome, {guest.guest_name}!</h1>
        <p className="party-info">Party of {guest.party_size}</p>
      </div>

      <div className="status-card" style={{ borderColor: getStatusColor(guest.status) }}>
        <div className="status-badge" style={{ backgroundColor: getStatusColor(guest.status) }}>
          {getStatusText(guest.status)}
        </div>

        {guest.status === 'waiting' && (
          <div className="wait-info">
            <div className="wait-stat">
              <span className="stat-value">{guest.position}</span>
              <span className="stat-label">Position</span>
            </div>
            {guest.eta_minutes !== null && (
              <div className="wait-stat">
                <span className="stat-value">~{guest.eta_minutes}</span>
                <span className="stat-label">Min Wait</span>
              </div>
            )}
          </div>
        )}

        {guest.status === 'notified' && (
          <p className="ready-message">Please proceed to the host stand</p>
        )}
      </div>

      <style>{`
        .guest-header {
          background: linear-gradient(135deg, var(--primary), var(--primary-dark));
          color: var(--white);
          padding: 24px 16px;
          border-radius: 0 0 24px 24px;
        }
        .guest-welcome h1 {
          font-size: 1.5rem;
          margin-bottom: 4px;
        }
        .party-info {
          opacity: 0.9;
          font-size: 0.875rem;
        }
        .status-card {
          background: var(--white);
          border-radius: 12px;
          padding: 16px;
          margin-top: 16px;
          border-left: 4px solid;
        }
        .status-badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 16px;
          color: var(--white);
          font-weight: 600;
          font-size: 0.875rem;
          margin-bottom: 12px;
        }
        .wait-info {
          display: flex;
          gap: 32px;
        }
        .wait-stat {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          color: var(--gray-800);
          line-height: 1;
        }
        .stat-label {
          font-size: 0.75rem;
          color: var(--gray-500);
          text-transform: uppercase;
          margin-top: 4px;
        }
        .ready-message {
          color: var(--gray-700);
          font-weight: 500;
        }
      `}</style>
    </header>
  );
}
