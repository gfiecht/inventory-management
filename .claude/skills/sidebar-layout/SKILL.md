---
name: sidebar-layout
description: Refactor the app layout from a top navigation bar to a modern left-aligned vertical sidebar navigation with polished SaaS UX/UI. Use this skill when migrating to sidebar nav, extracting TheSidebar.vue, or improving overall layout aesthetics.
---

# Sidebar Layout Refactor

You are an expert Frontend Engineer specializing in Vue 3, Tailwind CSS, and modern SaaS UX/UI design. Your task is to refactor the application's layout from a top-navigation bar to a modern, left-aligned vertical sidebar navigation, while polishing the overall interface.

## 1. Architectural Changes

**Layout Migration:** Locate the main layout component (e.g., `App.vue`, `DefaultLayout.vue`, or core navigation components). Replace the existing top navigation bar with a responsive, sticky left vertical sidebar.

**Component Extraction:** If the navigation logic is inline, extract the new sidebar into a reusable `TheSidebar.vue` component inside the components directory.

**Responsiveness:** The sidebar must be collapsible or turn into a bottom/overlay nav on mobile viewports.

## 2. Design & UI Specifications

**Navigation Layout:** The sidebar should include:
- Top: App logo and workspace/organization switcher (if applicable).
- Middle: Vertical list of navigation links with clear active/inactive states (using `router-link-active` or equivalent Vue Router states) and subtle SVG icons.
- Bottom: User profile snippet, settings, or a collapse toggle button.

**Spacing & Grid:** Enforce a strict spacing hierarchy using a consistent layout grid (e.g., Tailwind's `space-y-*`, `gap-*`, and standard `p-6` or `p-8` for main content containers). Ensure the main content area correctly scrolls independently of the fixed sidebar.

**Visual Polish:** Apply a clean, modern SaaS aesthetic: low-contrast borders, subtle hover transitions (`transition-all duration-200`), cohesive typography sizing, and an elegant, professional color palette (e.g., slate/zinc neutrals with a single clear accent color).

## 3. Technical Constraints

**Vue 3 Compliance:** Use Vue 3 `<script setup>` syntax and Composition API for any new or modified components.

**State & Routing:** Ensure all existing `vue-router` links are preserved and correctly mapped to the new vertical layout. Do not break existing router views.

**Framework Idioms:** Use standard utility classes (like Tailwind) if already present in the project. Do not introduce new CSS frameworks unless explicitly authorized.

## 4. Execution Plan

1. Scan the codebase to identify the current layout and navigation implementation.
2. Propose the structural changes and component breakdown before modifying files.
3. Implement the sidebar layout and update the main content wrapper.
4. Review the responsive behavior and fix any layout shifting or broken routing links.

## Key Reminders

- **Delegate to vue-expert**: Per project rules, any creation or significant modification of `.vue` files MUST be delegated to the `vue-expert` subagent.
- **Preserve routing**: All existing `vue-router` routes must remain intact — do not rename or remove route paths.
- **No new CSS frameworks**: Only use what is already in the project (check `package.json` first).
- **Test in browser**: Use Playwright MCP tools (`mcp__playwright__*`) to verify the layout at `http://localhost:3000` after implementation.
- **Mobile first**: Confirm the sidebar collapses or hides gracefully at small viewports before marking the task complete.
