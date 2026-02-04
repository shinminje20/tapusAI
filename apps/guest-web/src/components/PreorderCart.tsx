/**
 * Pre-order cart showing items guest has added for soft pre-order.
 *
 * REQ-MENU-003: Soft pre-order for fast casual
 * AC-MENU-003: System stores selections
 */

import type { GuestInterest } from '../services/api';

interface PreorderCartProps {
  items: GuestInterest[];
  onRemove: (menuItemId: number) => void;
  onUpdateQuantity: (menuItemId: number, quantity: number) => void;
  isLoading?: boolean;
}

export function PreorderCart({
  items,
  onRemove,
  onUpdateQuantity,
  isLoading = false,
}: PreorderCartProps) {
  if (items.length === 0) {
    return null;
  }

  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = items.reduce((sum, item) => {
    const price = parseFloat(item.menu_item?.price || '0');
    return sum + price * item.quantity;
  }, 0);

  return (
    <div className="preorder-cart">
      <div className="cart-header">
        <h3>Your Pre-Order</h3>
        <span className="item-count">{totalItems} item{totalItems !== 1 ? 's' : ''}</span>
      </div>

      <div className="cart-items">
        {items.map((item) => (
          <div key={item.menu_item_id} className="cart-item">
            <div className="item-info">
              <span className="item-name">{item.menu_item?.name || 'Unknown Item'}</span>
              <span className="item-price">
                ${item.menu_item?.price} x {item.quantity}
              </span>
            </div>
            <div className="item-actions">
              <div className="qty-controls">
                <button
                  className="qty-btn"
                  onClick={() => {
                    if (item.quantity > 1) {
                      onUpdateQuantity(item.menu_item_id, item.quantity - 1);
                    }
                  }}
                  disabled={isLoading || item.quantity <= 1}
                  aria-label="Decrease quantity"
                >
                  -
                </button>
                <span className="qty-value">{item.quantity}</span>
                <button
                  className="qty-btn"
                  onClick={() => onUpdateQuantity(item.menu_item_id, item.quantity + 1)}
                  disabled={isLoading}
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
              <button
                className="remove-btn"
                onClick={() => onRemove(item.menu_item_id)}
                disabled={isLoading}
                aria-label="Remove item"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="cart-footer">
        <div className="total-line">
          <span>Estimated Total</span>
          <span className="total-price">${totalPrice.toFixed(2)}</span>
        </div>
        <p className="cart-note">
          This is a soft pre-order. Your order will be confirmed when you're seated.
        </p>
      </div>

      <style>{`
        .preorder-cart {
          background: var(--white);
          border-radius: 16px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          margin-bottom: 24px;
        }
        .cart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: var(--primary);
          color: var(--white);
        }
        .cart-header h3 {
          margin: 0;
          font-size: 1.125rem;
        }
        .item-count {
          font-size: 0.875rem;
          opacity: 0.9;
        }
        .cart-items {
          padding: 8px 16px;
        }
        .cart-item {
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding: 12px 0;
          border-bottom: 1px solid var(--gray-100);
        }
        .cart-item:last-child {
          border-bottom: none;
        }
        .item-info {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }
        .item-name {
          font-weight: 500;
          color: var(--gray-800);
        }
        .item-price {
          font-size: 0.875rem;
          color: var(--gray-600);
        }
        .item-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .qty-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .qty-btn {
          width: 28px;
          height: 28px;
          border: 1px solid var(--gray-300);
          background: var(--white);
          border-radius: 6px;
          font-size: 1rem;
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
          min-width: 20px;
          text-align: center;
          font-weight: 500;
        }
        .remove-btn {
          background: none;
          border: none;
          color: var(--danger);
          font-size: 0.875rem;
          cursor: pointer;
          padding: 4px 8px;
        }
        .remove-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .cart-footer {
          padding: 16px;
          background: var(--gray-50);
        }
        .total-line {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        .total-price {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--gray-800);
        }
        .cart-note {
          font-size: 0.75rem;
          color: var(--gray-500);
          margin: 0;
          text-align: center;
        }
      `}</style>
    </div>
  );
}
