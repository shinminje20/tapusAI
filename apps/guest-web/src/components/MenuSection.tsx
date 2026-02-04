/**
 * Menu section component for displaying a category.
 *
 * REQ-MENU-001: Browse interactive menu organized by category
 * REQ-MENU-003: Soft pre-order for fast casual
 */

import type { MenuCategory } from '../services/api';
import { MenuItemCard } from './MenuItemCard';

interface MenuSectionProps {
  category: MenuCategory;
  starredItemIds: Set<number>;
  onToggleStar: (itemId: number, starred: boolean) => void;
  starringItemId?: number | null;
  preorderQuantities?: Map<number, number>;
  onAddToPreorder?: (itemId: number, quantity: number) => void;
  addingPreorderId?: number | null;
  enablePreorder?: boolean;
}

export function MenuSection({
  category,
  starredItemIds,
  onToggleStar,
  starringItemId,
  preorderQuantities,
  onAddToPreorder,
  addingPreorderId,
  enablePreorder = true,
}: MenuSectionProps) {
  // Filter out inactive items
  const activeItems = category.items.filter((item) => item.is_active);

  if (activeItems.length === 0) {
    return null;
  }

  return (
    <section className="menu-section">
      <h2 className="section-title">{category.name}</h2>
      {category.description && <p className="section-description">{category.description}</p>}

      <div className="section-items">
        {activeItems.map((item) => (
          <MenuItemCard
            key={item.id}
            item={item}
            isStarred={starredItemIds.has(item.id)}
            onToggleStar={onToggleStar}
            isStarring={starringItemId === item.id}
            preorderQuantity={preorderQuantities?.get(item.id) || 0}
            onAddToPreorder={onAddToPreorder}
            isAddingPreorder={addingPreorderId === item.id}
            enablePreorder={enablePreorder}
          />
        ))}
      </div>

      <style>{`
        .menu-section {
          margin-bottom: 32px;
        }
        .section-title {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--gray-800);
          margin-bottom: 4px;
          padding-left: 4px;
        }
        .section-description {
          font-size: 0.875rem;
          color: var(--gray-500);
          margin-bottom: 16px;
          padding-left: 4px;
        }
        .section-items {
          display: flex;
          flex-direction: column;
        }
      `}</style>
    </section>
  );
}
