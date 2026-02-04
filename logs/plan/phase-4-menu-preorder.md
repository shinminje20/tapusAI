# Phase 4: Menu Browsing & Soft Pre-Order

**Created:** 2026-02-04
**Status:** Planning

---

## Requirements Coverage

| REQ/AC | Description | Task |
|--------|-------------|------|
| REQ-MENU-001 | Guests can browse interactive menu | 4B.2 |
| REQ-MENU-002 | Guests can "star" items of interest | 4B.3 |
| REQ-MENU-003 | Fast casual soft pre-order | 4B.4 |
| REQ-MENU-004 | Full service "likely to order" view | 4C.2 |
| REQ-MENU-005 | SMS link → menu page flow | 4A.5, 4B.1 |
| AC-MENU-001 | Guest accesses menu from SMS link | 4A.5, 4B.1 |
| AC-MENU-002 | Star items stores to guest/entry | 4A.4, 4B.3 |
| AC-MENU-003 | Soft pre-order stored, hidden until seated | 4A.4 |
| AC-MENU-004 | Admin sees "Likely to order" summary | 4C.2 |
| AC-MENU-005 | Data model: menu_items, guest_interests, preorders | 4A.1, 4A.3 |

---

## Task Breakdown

### Phase 4A: Backend - Data Models & API

#### 4A.1 - Menu Data Model
- `MenuItem` entity: id, name, description, price, category, image_url, available, display_order
- `MenuCategory` entity: id, name, display_order, restaurant_id
- Database migrations
- Tests for entities

#### 4A.2 - Menu API Endpoints
- `GET /api/v1/menu` - List all menu items (public)
- `GET /api/v1/menu/categories` - List categories with items
- `GET /api/v1/menu/{item_id}` - Get single item
- Admin endpoints (protected):
  - `POST /api/v1/admin/menu` - Create item
  - `PUT /api/v1/admin/menu/{item_id}` - Update item
  - `DELETE /api/v1/admin/menu/{item_id}` - Delete item

#### 4A.3 - Guest Interests Data Model
- `GuestInterest` entity: id, waitlist_entry_id, menu_item_id, starred, quantity (for pre-order), created_at
- Links to waitlist_entry and menu_item
- Tests for entities

#### 4A.4 - Guest Interests API
- `POST /api/v1/guest/{token}/interests` - Star/unstar items
- `GET /api/v1/guest/{token}/interests` - Get guest's starred items
- `POST /api/v1/guest/{token}/preorder` - Submit soft pre-order
- `GET /api/v1/waitlist/{entry_id}/interests` - Admin view of guest interests

#### 4A.5 - Guest Token & Link Generation
- Generate secure token for each waitlist entry
- Token embedded in SMS link: `{BASE_URL}/guest/{token}`
- Token validates to specific waitlist entry
- Token expiry policy (e.g., 24 hours or until seated)
- Update SMS notification to include guest link

---

### Phase 4B: Guest Web App

#### 4B.1 - Guest Web App Setup
- New app: `apps/guest-web/` (React + Vite or Next.js)
- Mobile-first responsive design
- Route: `/guest/{token}` - Main guest page
- Validates token, loads waitlist entry context

#### 4B.2 - Menu Browsing UI
- Category tabs/sections
- Menu item cards with name, description, price, image
- Search/filter functionality (optional MVP)
- Responsive grid layout

#### 4B.3 - Star/Interest Functionality
- Star button on each menu item
- Visual feedback (filled/unfilled star)
- Persists to backend via API
- Shows "Your starred items" section

#### 4B.4 - Soft Pre-Order Flow (Fast Casual Mode)
- "Add to pre-order" button with quantity selector
- Pre-order cart/summary
- Submit pre-order button
- Confirmation message
- Note: Kitchen visibility controlled by seating status (AC-MENU-003)

---

### Phase 4C: Admin Integration

#### 4C.1 - Menu Management (Admin) - Optional for MVP
- Menu items list view
- Add/edit/delete menu items
- Category management
- Can defer to Phase 5 if needed

#### 4C.2 - "Likely to Order" Display
- On WaitlistItem, show interest summary
- Format: "Interested in: Burger, Salad (+2 more)"
- Expandable to see full list
- Visual indicator when guest has starred items

---

## Implementation Order

1. **4A.1** - Menu data model (backend foundation)
2. **4A.2** - Menu API (public endpoints first)
3. **4A.3** - Guest interests data model
4. **4A.5** - Guest token generation (needed for web app)
5. **4B.1** - Guest web app setup
6. **4B.2** - Menu browsing UI
7. **4A.4** - Guest interests API
8. **4B.3** - Star functionality
9. **4C.2** - Admin "Likely to Order" display
10. **4B.4** - Soft pre-order flow (if time permits)

---

## Technical Decisions Needed

1. **Guest Web App Framework**: React + Vite (simple, fast) vs Next.js (SSR, better SEO)
   - Recommendation: React + Vite (simpler, SSR not critical for authenticated guest pages)

2. **Token Format**: JWT vs opaque token
   - Recommendation: Opaque token (UUID) stored in DB, simpler security model

3. **Image Storage**: Local upload vs external URL
   - Recommendation: External URL for MVP (simpler), can add upload later

4. **Pre-order Visibility Trigger**: Manual "seat" action vs automatic
   - Per AC-MENU-003: Kitchen sees after seating/confirmation
   - Recommendation: Expose when status changes to `seated`

---

## Estimated Scope

- Backend: ~8-10 files (entities, repositories, endpoints, tests)
- Guest Web App: ~10-15 files (app setup, components, pages)
- Admin Updates: ~2-3 files

---

## Dependencies

- Phase 3 complete (SMS notifications - for guest link delivery)
- No external dependencies for MVP (images via URL)
