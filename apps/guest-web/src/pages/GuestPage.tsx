/**
 * Main guest page with waitlist status and menu browsing.
 *
 * REQ-MENU-005: Guest receives SMS with a link
 * REQ-MENU-001: Browse interactive menu
 * AC-MENU-001: Guest accesses menu from SMS link
 * AC-MENU-002: Star items for interest capture
 * REQ-MENU-003: Soft pre-order for fast casual
 * AC-MENU-003: Guest selects items to soft pre-order
 */

import { useState, useMemo, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  useGuestContext,
  useGuestMenu,
  useGuestInterests,
  useStarItem,
  useAddPreorder,
  useRemovePreorder,
} from '../hooks/useGuestData';
import { GuestHeader } from '../components/GuestHeader';
import { MenuSection } from '../components/MenuSection';
import { PreorderCart } from '../components/PreorderCart';
import { Toast } from '../components/Toast';
import { LoadingScreen } from '../components/LoadingScreen';
import { ErrorScreen } from '../components/ErrorScreen';

interface ToastState {
  message: string;
  type: 'success' | 'error' | 'info';
}

export function GuestPage() {
  const { token } = useParams<{ token: string }>();
  const [starringItemId, setStarringItemId] = useState<number | null>(null);
  const [addingPreorderId, setAddingPreorderId] = useState<number | null>(null);
  const [toast, setToast] = useState<ToastState | null>(null);

  // Fetch data using React Query hooks
  const {
    data: guestContext,
    isLoading: contextLoading,
    error: contextError,
    refetch: refetchContext,
  } = useGuestContext(token || '');

  const {
    data: menuData,
    isLoading: menuLoading,
    error: menuError,
  } = useGuestMenu(token || '');

  const {
    data: interests,
    isLoading: interestsLoading,
  } = useGuestInterests(token || '');

  const starMutation = useStarItem(token || '');
  const addPreorderMutation = useAddPreorder(token || '');
  const removePreorderMutation = useRemovePreorder(token || '');

  // Derive starred item IDs for quick lookup
  const starredItemIds = useMemo(() => {
    const ids = new Set<number>();
    interests?.starred_items.forEach((item) => ids.add(item.menu_item_id));
    return ids;
  }, [interests]);

  // Derive preorder quantities for quick lookup
  const preorderQuantities = useMemo(() => {
    const map = new Map<number, number>();
    interests?.preorder_items.forEach((item) => {
      map.set(item.menu_item_id, item.quantity);
    });
    return map;
  }, [interests]);

  // Handle star toggle
  const handleToggleStar = async (menuItemId: number, starred: boolean) => {
    setStarringItemId(menuItemId);
    try {
      await starMutation.mutateAsync({ menuItemId, starred });
    } finally {
      setStarringItemId(null);
    }
  };

  // Handle add to preorder
  const handleAddToPreorder = useCallback(async (menuItemId: number, quantity: number) => {
    setAddingPreorderId(menuItemId);
    try {
      await addPreorderMutation.mutateAsync({ menuItemId, quantity });
      setToast({ message: 'Added to your pre-order!', type: 'success' });
    } catch (error) {
      setToast({ message: 'Failed to add item. Please try again.', type: 'error' });
    } finally {
      setAddingPreorderId(null);
    }
  }, [addPreorderMutation]);

  // Handle remove from preorder
  const handleRemoveFromPreorder = useCallback(async (menuItemId: number) => {
    try {
      await removePreorderMutation.mutateAsync(menuItemId);
      setToast({ message: 'Removed from pre-order', type: 'info' });
    } catch (error) {
      setToast({ message: 'Failed to remove item. Please try again.', type: 'error' });
    }
  }, [removePreorderMutation]);

  // Handle update preorder quantity (re-add with new quantity)
  const handleUpdatePreorderQuantity = useCallback(async (menuItemId: number, quantity: number) => {
    try {
      await addPreorderMutation.mutateAsync({ menuItemId, quantity });
    } catch (error) {
      setToast({ message: 'Failed to update quantity. Please try again.', type: 'error' });
    }
  }, [addPreorderMutation]);

  // Close toast
  const handleCloseToast = useCallback(() => {
    setToast(null);
  }, []);

  // Loading state
  if (contextLoading) {
    return <LoadingScreen message="Loading your reservation..." />;
  }

  // Error state - likely invalid token
  if (contextError) {
    const errorMessage = contextError.message.includes('404')
      ? 'This link may have expired or is invalid. Please check your SMS for the correct link.'
      : contextError.message;

    return (
      <ErrorScreen
        title="Unable to Load"
        message={errorMessage}
        onRetry={() => refetchContext()}
      />
    );
  }

  // No guest data
  if (!guestContext) {
    return (
      <ErrorScreen
        title="Reservation Not Found"
        message="We couldn't find your reservation. Please check your SMS link."
      />
    );
  }

  // Filter active categories
  const activeCategories = menuData?.categories.filter((cat) => cat.is_active) || [];

  const preorderItems = interests?.preorder_items || [];
  const hasPreorderItems = preorderItems.length > 0;

  return (
    <div className="guest-page">
      <GuestHeader guest={guestContext} />

      <main className="guest-main">
        <div className="menu-intro">
          <h2>Browse Our Menu</h2>
          <p>Star items you're interested in, or add them to your pre-order!</p>
          {interests && interests.total_starred > 0 && (
            <p className="starred-count">
              You've starred {interests.total_starred} item{interests.total_starred !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        {/* Pre-order cart - AC-MENU-003: Pre-order summary */}
        {hasPreorderItems && (
          <PreorderCart
            items={preorderItems}
            onRemove={handleRemoveFromPreorder}
            onUpdateQuantity={handleUpdatePreorderQuantity}
            isLoading={addPreorderMutation.isPending || removePreorderMutation.isPending}
          />
        )}

        {menuLoading || interestsLoading ? (
          <div className="menu-loading">
            <div className="spinner"></div>
            <p>Loading menu...</p>
          </div>
        ) : menuError ? (
          <div className="menu-error">
            <p>Unable to load menu. Please try again.</p>
          </div>
        ) : activeCategories.length === 0 ? (
          <div className="menu-empty">
            <p>Menu is currently being updated. Please check back soon!</p>
          </div>
        ) : (
          <div className="menu-content">
            {activeCategories.map((category) => (
              <MenuSection
                key={category.id}
                category={category}
                starredItemIds={starredItemIds}
                onToggleStar={handleToggleStar}
                starringItemId={starringItemId}
                preorderQuantities={preorderQuantities}
                onAddToPreorder={handleAddToPreorder}
                addingPreorderId={addingPreorderId}
                enablePreorder={true}
              />
            ))}
          </div>
        )}
      </main>

      <footer className="guest-footer">
        <p>Powered by tapusAI</p>
      </footer>

      {/* Toast notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={handleCloseToast}
        />
      )}

      <style>{`
        .guest-page {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        .guest-main {
          flex: 1;
          padding: 24px 16px;
          max-width: 768px;
          margin: 0 auto;
          width: 100%;
        }
        .menu-intro {
          text-align: center;
          margin-bottom: 24px;
        }
        .menu-intro h2 {
          color: var(--gray-800);
          margin-bottom: 8px;
        }
        .menu-intro p {
          color: var(--gray-500);
          font-size: 0.875rem;
        }
        .starred-count {
          color: var(--star-gold);
          font-weight: 600;
          margin-top: 8px;
        }
        .menu-loading,
        .menu-error,
        .menu-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px 24px;
          text-align: center;
          gap: 16px;
        }
        .menu-error p,
        .menu-empty p {
          color: var(--gray-500);
        }
        .menu-content {
          padding-bottom: 24px;
        }
        .guest-footer {
          text-align: center;
          padding: 16px;
          background: var(--gray-100);
        }
        .guest-footer p {
          font-size: 0.75rem;
          color: var(--gray-400);
        }
      `}</style>
    </div>
  );
}
