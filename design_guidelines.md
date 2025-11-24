# Design Guidelines: Sistema Integrado de Controle - Notas Fiscais e Containers

## Design Approach

**System Selected**: Material Design (enterprise variant) with Carbon Design influences for data-heavy sections
**Justification**: Information-dense logistics application requiring clear data hierarchy, efficient workflows, and robust table components. Material Design provides excellent visual feedback systems while maintaining professional utility.

## Typography

**Font Stack**: 
- Primary: Roboto (400, 500, 700) via Google Fonts CDN
- Monospace: Roboto Mono for container numbers, CNPJ, and IDs

**Hierarchy**:
- Page Titles: text-3xl font-bold (30px)
- Section Headers: text-xl font-medium (20px)
- Data Labels: text-sm font-medium (14px, uppercase with tracking-wide)
- Table Headers: text-sm font-semibold (14px)
- Body/Table Data: text-base (16px)
- Metadata/Timestamps: text-sm text-gray-600 (14px)

## Layout System

**Spacing Primitives**: Use Tailwind units of 2, 4, 6, 8, 12, 16, 20
- Component padding: p-6
- Section margins: mb-8
- Card spacing: space-y-6
- Grid gaps: gap-4 to gap-6
- Button padding: px-6 py-3

**Container Widths**:
- Main application container: max-w-7xl mx-auto
- Dashboard cards: Full width within grid
- Forms: max-w-2xl
- Modals: max-w-lg to max-w-3xl based on content

## Component Library

### Navigation
**Sidebar Navigation** (persistent for main modules):
- Fixed left sidebar (w-64)
- Collapsible on mobile
- Two main sections: "Notas Fiscais" and "Containers"
- Icon + label for each route
- Active state with accent border-left indicator
- Sub-navigation accordion for nested routes

### Data Tables
**Enhanced DataTables**:
- Bordered cells with subtle row hover states
- Fixed header on scroll
- Sticky first column for key identifiers (nota number/container number)
- Status badges in dedicated column
- Action buttons (icon-only) in last column
- Alternating row backgrounds for readability
- Responsive: Stack to cards on mobile

**Table Toolbar**:
- Search input (with icon prefix)
- Filter dropdowns (Status, Local, Armador for containers)
- Export button
- Add New button (primary, top-right)

### Status System
**Container Status Badges**:
- Portaria: Blue badge with dot indicator
- Pátio Cheio: Green badge
- Desova: Orange badge with pulse animation
- Pátio Vazio: Gray badge
- Liberado Saída: Purple badge

**NFe Status** (existing):
- Pendente: Yellow badge
- Processada: Green badge

Badge style: Rounded-full, px-3 py-1, font-medium text-xs, with leading dot indicator

### Cards
**Dashboard Stat Cards**:
- White background, rounded-lg, shadow-sm
- p-6 padding
- Icon in accent circle (top or left)
- Large number display (text-3xl font-bold)
- Label below (text-sm text-gray-600)
- Optional trend indicator (up/down arrow with percentage)

**Container Detail Cards**:
- Border-left accent based on status
- Grid layout for key-value pairs
- Monospace for identifiers

### Forms
**Input Fields**:
- Consistent height (h-12)
- Border with focus:ring transition
- Labels above inputs (text-sm font-medium mb-2)
- Helper text below (text-xs text-gray-500)
- Error states with red border and error message
- Required indicator (red asterisk)

**Form Layout**:
- Single column for simple forms
- Two-column grid (grid-cols-2 gap-6) for container registration
- Full-width submit buttons at bottom
- Secondary actions (Cancel) as text buttons

### Buttons
**Hierarchy**:
- Primary: Solid background, white text, shadow-sm
- Secondary: Outlined, transparent background
- Tertiary: Text only, no border
- Icon-only: Square (h-10 w-10), centered icon

**Sizes**: px-6 py-3 (default), px-4 py-2 (small), px-8 py-4 (large)

### Modal Dialogs
**Movement Registration Modals**:
- Overlay backdrop (bg-black/50)
- Centered modal (max-w-2xl)
- Header with title and close button
- Body with form (p-6)
- Footer with actions (border-top, p-4, flex justify-end)

### Timeline (Movement History)
**Container Movement Timeline**:
- Vertical line connecting events
- Circle markers at each event (filled for completed)
- Event card with timestamp, type, and observations
- Color-coded by movement type

## Dashboard Layout

**Grid Structure** (for both NFe and Container dashboards):
- 4-column grid on desktop (grid-cols-4)
- 2-column on tablet (md:grid-cols-2)
- Single column on mobile
- Stat cards in top row
- Charts/detailed tables below

**Unified Dashboard Option**:
- Tabbed interface switching between "Notas Fiscais" and "Containers"
- Combined overview showing both systems' key metrics
- Quick action buttons for common tasks

## Responsive Behavior

**Breakpoints**:
- Mobile: < 768px (stack all, hide sidebar, hamburger menu)
- Tablet: 768px - 1024px (2-column grids, condensed sidebar)
- Desktop: > 1024px (full layout with sidebar)

**Mobile Adaptations**:
- Tables become stacked cards
- Filter toolbar becomes dropdown sheet
- Sidebar becomes slide-out drawer
- Actions move to card footer

## Animations

**Minimal, purposeful animations only**:
- Status badge pulse for "Desova" status
- Smooth transitions for modal open/close (duration-200)
- Table row hover (subtle background change)
- Loading spinner for data fetch

**No decorative animations** - focus on functional feedback.

## Accessibility

- Semantic HTML throughout (nav, main, section, article)
- ARIA labels for icon-only buttons
- Keyboard navigation for all interactive elements
- Focus visible states (ring-2 ring-offset-2)
- Color contrast meeting WCAG AA standards
- Screen reader announcements for status changes

## Icons

**Library**: Material Icons (via CDN)
**Usage**:
- Navigation items (24px)
- Status indicators (16px, inline with text)
- Action buttons (20px)
- Dashboard stat cards (48px)

## Integration Considerations

Maintain visual consistency between existing NFe module and new Container module - same navigation pattern, card styles, table formatting. Users should perceive this as one cohesive system, not two separate applications bolted together.