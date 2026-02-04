/**
 * Quantity selector for pre-order items.
 *
 * REQ-MENU-003: Soft pre-order for fast casual
 * AC-MENU-003: Guest selects items to soft pre-order
 */

interface QuantitySelectorProps {
  quantity: number;
  onChange: (quantity: number) => void;
  min?: number;
  max?: number;
  disabled?: boolean;
}

export function QuantitySelector({
  quantity,
  onChange,
  min = 1,
  max = 10,
  disabled = false,
}: QuantitySelectorProps) {
  const handleDecrement = () => {
    if (quantity > min) {
      onChange(quantity - 1);
    }
  };

  const handleIncrement = () => {
    if (quantity < max) {
      onChange(quantity + 1);
    }
  };

  return (
    <div className="quantity-selector">
      <button
        type="button"
        className="qty-btn"
        onClick={handleDecrement}
        disabled={disabled || quantity <= min}
        aria-label="Decrease quantity"
      >
        -
      </button>
      <span className="qty-value">{quantity}</span>
      <button
        type="button"
        className="qty-btn"
        onClick={handleIncrement}
        disabled={disabled || quantity >= max}
        aria-label="Increase quantity"
      >
        +
      </button>

      <style>{`
        .quantity-selector {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: var(--gray-100);
          border-radius: 8px;
          padding: 4px;
        }
        .qty-btn {
          width: 32px;
          height: 32px;
          border: none;
          background: var(--white);
          border-radius: 6px;
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--gray-700);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background-color 0.15s;
        }
        .qty-btn:hover:not(:disabled) {
          background: var(--gray-200);
        }
        .qty-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }
        .qty-value {
          min-width: 24px;
          text-align: center;
          font-weight: 600;
          color: var(--gray-800);
        }
      `}</style>
    </div>
  );
}
