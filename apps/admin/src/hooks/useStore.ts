/**
 * Typed Redux hooks for Admin app.
 *
 * Provides type-safe useSelector and useDispatch hooks
 * with proper TypeScript inference from the store.
 */

import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from '../app/store';

/**
 * Typed useDispatch hook for Admin app
 * Use this instead of plain useDispatch for type safety
 */
export const useAppDispatch: () => AppDispatch = useDispatch;

/**
 * Typed useSelector hook for Admin app
 * Use this instead of plain useSelector for type safety
 */
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
