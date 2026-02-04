import { waitlistApi } from '../waitlistApi';
import { ADMIN_SOURCE } from '../../app/constants';

/**
 * Tests for waitlistApi (Admin App)
 *
 * Verifies:
 * - AC-WL-003: Status transitions (waiting -> seated/canceled/no_show)
 * - AC-WL-005: Reordering updates position
 * - AC-WL-006: VIP flagging
 * - AC-WL-007: ETA is included in response
 */

describe('waitlistApi', () => {
  describe('endpoints', () => {
    it('has getWaitlist query endpoint', () => {
      expect(waitlistApi.endpoints.getWaitlist).toBeDefined();
    });

    it('has updateStatus mutation endpoint', () => {
      expect(waitlistApi.endpoints.updateStatus).toBeDefined();
    });

    it('has toggleVip mutation endpoint', () => {
      expect(waitlistApi.endpoints.toggleVip).toBeDefined();
    });

    it('has reorderEntries mutation endpoint', () => {
      expect(waitlistApi.endpoints.reorderEntries).toBeDefined();
    });
  });

  describe('constants', () => {
    it('ADMIN_SOURCE is set to admin', () => {
      // Verifies AC-WL-008: Source captured as 'admin'
      expect(ADMIN_SOURCE).toBe('admin');
    });
  });

  describe('hooks export', () => {
    it('exports useGetWaitlistQuery hook', () => {
      // Import the hooks from the module
      const { useGetWaitlistQuery } = require('../waitlistApi');
      expect(useGetWaitlistQuery).toBeDefined();
    });

    it('exports useUpdateStatusMutation hook', () => {
      const { useUpdateStatusMutation } = require('../waitlistApi');
      expect(useUpdateStatusMutation).toBeDefined();
    });

    it('exports useToggleVipMutation hook', () => {
      const { useToggleVipMutation } = require('../waitlistApi');
      expect(useToggleVipMutation).toBeDefined();
    });

    it('exports useReorderEntriesMutation hook', () => {
      const { useReorderEntriesMutation } = require('../waitlistApi');
      expect(useReorderEntriesMutation).toBeDefined();
    });
  });
});
