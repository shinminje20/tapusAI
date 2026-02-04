/**
 * Messaging feature exports
 *
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * REQ-STAFF-002: Templates must support fast insertion and consistent tone
 * AC-STAFF-001: Canned templates available in admin UI
 * AC-STAFF-002: Templates are fast to send and consistent
 */

// Screen exports
export { MessagingScreen } from './screens';
export type { MessagingScreenParams } from './screens';

// Component exports
export { TemplateSelector, MessagePreview } from './components';

// Template exports
export { DEFAULT_TEMPLATES, getTemplateById } from './templates';
export type { MessageTemplate } from './templates';
