/**
 * Staff convenience message templates
 *
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * REQ-STAFF-002: Templates must support fast insertion and consistent tone
 * AC-STAFF-001: Canned templates available in admin UI
 * AC-STAFF-002: Templates are fast to send and consistent
 */

/**
 * Message template structure
 * - id: Unique identifier for logging (AC-STAFF-002: log template used)
 * - label: Short label for button display
 * - message: Full message text to send
 */
export interface MessageTemplate {
  id: string;
  label: string;
  message: string;
}

/**
 * Default message templates
 * REQ-STAFF-001: Canned response templates on Admin tablet
 *
 * Templates are defined per requirements:
 * - Running behind notification
 * - Table hold warning
 * - Table ready notification (convenience shortcut)
 */
export const DEFAULT_TEMPLATES: readonly MessageTemplate[] = [
  {
    id: 'running_behind',
    label: 'Running Behind',
    message: "We're running a bit behind, new estimate is 15-20 mins.",
  },
  {
    id: 'table_hold',
    label: 'Table Hold Warning',
    message: "We can't hold your table longer than 10 minutes.",
  },
  {
    id: 'table_ready',
    label: 'Table Ready',
    message: 'Your table is ready! Please come to the host stand.',
  },
] as const;

/**
 * Get template by ID
 * @param id Template identifier
 * @returns Template or undefined if not found
 */
export function getTemplateById(id: string): MessageTemplate | undefined {
  return DEFAULT_TEMPLATES.find((t) => t.id === id);
}
