/**
 * Menu item card with star and pre-order functionality.
 *
 * REQ-MENU-001: Browse interactive menu
 * AC-MENU-002: Star items for interest capture
 * REQ-MENU-003: Soft pre-order for fast casual
 * AC-MENU-003: Guest selects items to soft pre-order
 */

import { useState } from 'react';
import type { MenuItem } from '../services/api';

interface MenuItemCardProps {
  item: MenuItem;
  isStarred: boolean;
  onToggleStar: (itemId: number, starred: boolean) => void;
  isStarring?: boolean;
  preorderQuantity?: number;
  onAddToPreorder?: (itemId: number, quantity: number) => void;
  isAddingPreorder?: boolean;
  enablePreorder?: boolean;
}

export function MenuItemCard({
  item,
  isStarred,
  onToggleStar,
  isStarring,
  preorderQuantity = 0,
  onAddToPreorder,
  isAddingPreorder,
  enablePreorder = true,
}: MenuItemCardProps) {
  const [showQuantity, setShowQuantity] = useState(false);
  const [quantity, setQuantity] = useState(1);

  const handleStarClick = () => {
    if (!isStarring) {
      onToggleStar(item.id, !isStarred);
    }
  };

  const handleAddClick = () => {
    if (!item.is_available) return;
    setShowQuantity(true);
  };

  const handleConfirmAdd = () => {
    if (onAddToPreorder && !isAddingPreorder) {
      onAddToPreorder(item.id, quantity);
      setShowQuantity(false);
      setQuantity(1);
    }
  };

  const handleCancelAdd = () => {
    setShowQuantity(false);
    setQuantity(1);
  };

  return (
    <article className={`menu-item-card ${!item.is_available ? 'unavailable' : ''}`}>
      <div className="item-content">
        <div className="item-header">
          <h4 className="item-name">{item.name}</h4>
          <span className="item-price">${item.price}</span>
        </div>

        {item.description && <p className="item-description">{item.description}</p>}

        <div className="item-meta">
          {item.calories && <span className="meta-item">{item.calories} cal</span>}
          {item.tags_list.length > 0 && (
            <div className="tags">
              {item.tags_list.map((tag) => (
                <span key={tag} className="tag">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {item.allergens && (
          <p className="allergens">
            <strong>Allergens:</strong> {item.allergens}
          </p>
        )}

        {!item.is_available && <span className="unavailable-badge">Currently Unavailable</span>}

        {/* Pre-order section */}
        {enablePreorder && item.is_available && (
          <div className="preorder-section">
            {preorderQuantity > 0 && !showQuantity && (
              <span className="in-cart-badge">{preorderQuantity} in pre-order</span>
            )}

            {showQuantity ? (
              <div className="quantity-picker">
                <div className="qty-controls">
                  <button
                    type="button"
                    className="qty-btn"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <span className="qty-value">{quantity}</span>
                  <button
                    type="button"
                    className="qty-btn"
                    onClick={() => setQuantity(Math.min(10, quantity + 1))}
                    disabled={quantity >= 10}
                  >
                    +
                  </button>
                </div>
                <div className="qty-actions">
                  <button
                    type="button"
                    className="confirm-btn"
                    onClick={handleConfirmAdd}
                    disabled={isAddingPreorder}
                  >
                    {isAddingPreorder ? 'Adding...' : 'Add'}
                  </button>
                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={handleCancelAdd}
                    disabled={isAddingPreorder}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                className="add-preorder-btn"
                onClick={handleAddClick}
              >
                + Add to Pre-Order
              </button>
            )}
          </div>
        )}
      </div>

      <button
        className={`star-btn ${isStarred ? 'starred' : 'not-starred'}`}
        onClick={handleStarClick}
        disabled={isStarring || !item.is_available}
        aria-label={isStarred ? 'Remove from favorites' : 'Add to favorites'}
      >
        {isStarred ? '\u2605' : '\u2606'}
      </button>

      <style>{`
        .menu-item-card {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          background: var(--white);
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        .menu-item-card.unavailable {
          opacity: 0.6;
        }
        .item-content {
          flex: 1;
          min-width: 0;
        }
        .item-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 8px;
        }
        .item-name {
          font-size: 1rem;
          font-weight: 600;
          color: var(--gray-800);
          margin: 0;
        }
        .item-price {
          font-weight: 600;
          color: var(--gray-700);
          white-space: nowrap;
        }
        .item-description {
          font-size: 0.875rem;
          color: var(--gray-600);
          margin-bottom: 8px;
          line-height: 1.4;
        }
        .item-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          align-items: center;
          margin-bottom: 8px;
        }
        .meta-item {
          font-size: 0.75rem;
          color: var(--gray-500);
        }
        .tags {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        .tag {
          font-size: 0.625rem;
          padding: 2px 6px;
          background: var(--gray-100);
          color: var(--gray-600);
          border-radius: 4px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .allergens {
          font-size: 0.75rem;
          color: var(--warning);
          margin: 0;
        }
        .unavailable-badge {
          display: inline-block;
          font-size: 0.75rem;
          padding: 4px 8px;
          background: var(--gray-200);
          color: var(--gray-600);
          border-radius: 4px;
          margin-top: 8px;
        }
        .star-btn {
          flex-shrink: 0;
        }
        .star-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        /* Pre-order section styles */
        .preorder-section {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid var(--gray-100);
        }
        .in-cart-badge {
          display: inline-block;
          font-size: 0.75rem;
          padding: 4px 8px;
          background: var(--success);
          color: var(--white);
          border-radius: 4px;
          margin-bottom: 8px;
        }
        .add-preorder-btn {
          width: 100%;
          padding: 10px 16px;
          background: var(--primary);
          color: var(--white);
          border: none;
          border-radius: 8px;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: background-color 0.15s;
        }
        .add-preorder-btn:hover {
          background: var(--primary-dark);
        }
        .quantity-picker {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .qty-controls {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
        }
        .qty-btn {
          width: 36px;
          height: 36px;
          border: 1px solid var(--gray-300);
          background: var(--white);
          border-radius: 8px;
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--gray-700);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .qty-btn:hover:not(:disabled) {
          background: var(--gray-100);
        }
        .qty-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }
        .qty-value {
          min-width: 32px;
          text-align: center;
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--gray-800);
        }
        .qty-actions {
          display: flex;
          gap: 8px;
        }
        .confirm-btn {
          flex: 1;
          padding: 10px;
          background: var(--success);
          color: var(--white);
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }
        .confirm-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .cancel-btn {
          flex: 1;
          padding: 10px;
          background: var(--gray-200);
          color: var(--gray-700);
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }
        .cancel-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      `}</style>
    </article>
  );
}
