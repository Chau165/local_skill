# Accessibility Checklist

Use this checklist before closing UI work.

## Structure

- Use semantic HTML where possible before reaching for ARIA.
- Keep heading order logical and avoid skipping levels.
- Ensure landmarks and labels make the page navigable.

## Keyboard

- Every interactive control must be reachable by keyboard.
- Focus order should follow the visual and logical flow.
- Custom widgets must support keyboard interaction equivalent to native controls.

## Forms

- Inputs need visible labels or accurate accessible names.
- Validation errors should be announced clearly and linked to the field.
- Required state, helper text, and constraints should be discoverable.

## Feedback

- Important state changes should be perceivable without relying on color alone.
- Dialogs, menus, and popovers should manage focus correctly.
- Loading, success, and error states should be announced when appropriate.

## Visual

- Text and controls should meet contrast expectations.
- Touch targets should be large enough to operate comfortably.
- Layout should remain usable at zoom and on narrow screens.

## Verification

- Test with keyboard only.
- Check at least one screen reader path for important flows.
- Verify responsive layouts do not hide or break core actions.
