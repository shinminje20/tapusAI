/**
 * Guest Web App main component with routing.
 *
 * REQ-MENU-005: Guest receives SMS with a link
 * Routes:
 * - /guest/:token - Main guest page with menu
 */

import { Routes, Route } from 'react-router-dom';
import { GuestPage } from './pages/GuestPage';
import { NotFoundPage } from './pages/NotFoundPage';

export default function App() {
  return (
    <Routes>
      {/* Main guest route with token */}
      <Route path="/guest/:token" element={<GuestPage />} />

      {/* Redirect root to a friendly message */}
      <Route path="/" element={<NotFoundPage message="Please use the link from your SMS" />} />

      {/* 404 for all other routes */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
