/**
 * API service for guest web app.
 *
 * REQ-MENU-005: Guest receives SMS with a link
 * AC-MENU-001: Guest accesses menu from SMS link
 * AC-MENU-002: Star items for interest capture
 */

const API_BASE = '/api/v1';

// ==================== Types ====================

export interface GuestContext {
  entry_id: number;
  guest_name: string;
  party_size: number;
  status: string;
  position: number;
  eta_minutes: number | null;
  created_at: string;
}

export interface MenuItem {
  id: number;
  category_id: number;
  name: string;
  description: string | null;
  price: string;
  image_url: string | null;
  display_order: number;
  is_available: boolean;
  is_active: boolean;
  calories: number | null;
  allergens: string | null;
  tags: string | null;
  tags_list: string[];
}

export interface MenuCategory {
  id: number;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  items: MenuItem[];
}

export interface MenuResponse {
  categories: MenuCategory[];
  total_items: number;
}

export interface GuestInterest {
  id: number;
  menu_item_id: number;
  is_starred: boolean;
  is_preorder: boolean;
  quantity: number;
  menu_item: MenuItem | null;
}

export interface GuestInterestsResponse {
  starred_items: GuestInterest[];
  preorder_items: GuestInterest[];
  total_starred: number;
  total_preorder: number;
}

// ==================== API Functions ====================

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get guest context by token.
 * AC-MENU-001: Guest accesses their waitlist status
 */
export async function getGuestContext(token: string): Promise<GuestContext> {
  return fetchJson<GuestContext>(`${API_BASE}/guest/${token}`);
}

/**
 * Get menu for guest.
 * REQ-MENU-001: Browse interactive menu
 */
export async function getGuestMenu(token: string): Promise<MenuResponse> {
  return fetchJson<MenuResponse>(`${API_BASE}/guest/${token}/menu`);
}

/**
 * Get guest's starred and preorder items.
 * AC-MENU-002: Get starred items
 */
export async function getGuestInterests(token: string): Promise<GuestInterestsResponse> {
  return fetchJson<GuestInterestsResponse>(`${API_BASE}/guest/${token}/interests`);
}

/**
 * Star or unstar a menu item.
 * AC-MENU-002: Star items for interest capture
 */
export async function starItem(
  token: string,
  menuItemId: number,
  starred: boolean
): Promise<GuestInterest> {
  return fetchJson<GuestInterest>(`${API_BASE}/guest/${token}/interests/star`, {
    method: 'POST',
    body: JSON.stringify({ menu_item_id: menuItemId, starred }),
  });
}

/**
 * Add item to preorder.
 * AC-MENU-003: Soft pre-order capture
 */
export async function addPreorder(
  token: string,
  menuItemId: number,
  quantity: number = 1
): Promise<GuestInterest> {
  return fetchJson<GuestInterest>(`${API_BASE}/guest/${token}/preorder`, {
    method: 'POST',
    body: JSON.stringify({ menu_item_id: menuItemId, quantity }),
  });
}

/**
 * Remove item from preorder.
 */
export async function removePreorder(
  token: string,
  menuItemId: number
): Promise<GuestInterest> {
  return fetchJson<GuestInterest>(`${API_BASE}/guest/${token}/preorder/${menuItemId}`, {
    method: 'DELETE',
  });
}
