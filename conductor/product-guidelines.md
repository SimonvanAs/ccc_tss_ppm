# Product Guidelines: TSS PPM v3.0

## Tone & Voice

### Friendly and Approachable
TSS PPM uses a warm, conversational tone that makes performance reviews feel less intimidating. The language should be:

- **Encouraging** - Support users through the review process without being condescending
- **Clear** - Use plain language, avoid HR jargon where possible
- **Human** - Write as a helpful colleague, not a system
- **Respectful** - Acknowledge that performance reviews can be stressful

### Examples

| Instead of... | Use... |
|---------------|--------|
| "Submit form for processing" | "Send for review" |
| "Invalid input detected" | "Let's fix this together" |
| "Action required" | "You have a task waiting" |
| "Review cycle terminated" | "Review complete" |

## Error Messages & System Feedback

### Helpful and Solution-Oriented
All error messages and system feedback should explain what went wrong and guide users on how to fix it.

### Guidelines
1. **Lead with the problem** - State what happened clearly
2. **Explain why** - Help users understand the cause
3. **Provide the solution** - Give actionable next steps
4. **Use friendly language** - Maintain the approachable tone

### Examples

| Scenario | Message |
|----------|---------|
| Weight validation | "The goal weights must total 100%. Currently at 85% — add 15% more to continue." |
| Missing required field | "Please add a description for this goal so your manager understands what you're working toward." |
| Session timeout | "You've been away for a while. Your work is saved — just sign in again to continue." |
| Save confirmation | "Changes saved! Your manager will be notified once you submit." |

## Accessibility Standards

### WCAG 2.1 AA Compliance
TSS PPM adheres to Web Content Accessibility Guidelines (WCAG) 2.1 Level AA, ensuring the application is usable by people with diverse abilities.

### Requirements
- **Color Contrast**: Minimum 4.5:1 ratio for normal text, 3:1 for large text
- **Keyboard Navigation**: All functionality accessible via keyboard alone
- **Screen Reader Support**: Proper ARIA labels, semantic HTML, logical reading order
- **Focus Indicators**: Visible focus states on all interactive elements
- **Text Resizing**: Content remains functional at 200% zoom
- **Motion**: Respect `prefers-reduced-motion` user preference
- **Form Labels**: All inputs have associated labels and clear error identification

### Voice Input Accessibility
- Visual recording indicator with color AND icon state change
- Text alternative feedback for audio recording status
- Keyboard-accessible start/stop controls

## Responsive Design

### Desktop-First with Mobile Support
The primary workflow is optimized for desktop and laptop use, with functional mobile views for review and approval tasks.

### Breakpoints
| Breakpoint | Target | Use Case |
|------------|--------|----------|
| ≥1200px | Desktop | Full workflow: goal setting, scoring, calibration, analytics |
| 768-1199px | Tablet | Review viewing, approvals, basic editing |
| <768px | Mobile | Task notifications, quick approvals, review reading |

### Desktop Priority Features
- Full 9-grid visualization with hover interactions
- Side-by-side goal and competency panels
- Drag-and-drop goal reordering
- Complete analytics dashboards
- Calibration session management

### Mobile-Optimized Features
- Task list and notifications
- Review reading and approval
- Digital signature capture
- Basic goal viewing
- Voice input for feedback

## Visual Design Principles

### Clean and Minimal
The interface uses generous whitespace, focused content areas, and reduced visual clutter to keep attention on review content and scoring decisions.

### Principles
1. **Whitespace is content** - Give elements room to breathe
2. **One primary action** - Each screen has one clear next step
3. **Progressive disclosure** - Show details on demand, not all at once
4. **Consistent patterns** - Same actions look the same everywhere
5. **Purposeful color** - Use brand colors for meaning, not decoration

### Brand Colors Usage

| Color | Hex | Usage |
|-------|-----|-------|
| **Magenta** | #CC0E70 | Primary actions, focus states, active elements, recording indicator |
| **Navy Blue** | #004A91 | Headings, secondary actions, informational elements |
| **Success Green** | (define) | Positive scores, completion states, signed status |
| **Warning Orange** | (define) | Pending actions, attention needed |
| **Error Red** | (define) | Validation errors, VETO indicators |
| **Neutral Grays** | (define) | Backgrounds, borders, disabled states |

### Typography
- **Font Family**: Tahoma
- **Hierarchy**: Clear distinction between headings, body, and labels
- **Line Height**: Generous (1.5+) for readability
- **Maximum Line Width**: ~75 characters for comfortable reading

### Component Guidelines
- **Buttons**: Clear primary/secondary distinction, adequate touch targets (44x44px minimum)
- **Forms**: Single-column layout, inline validation, clear labels
- **Cards**: Subtle shadows, rounded corners, consistent padding
- **Tables**: Alternating row colors, sortable headers, responsive scroll on mobile
- **9-Grid**: High contrast cell backgrounds, clear score indicators, accessible color coding

## Internationalization

### Multi-Language Support
- All UI text must be externalized for translation
- Support right-to-left (RTL) layouts for future languages
- Date, number, and currency formatting based on locale
- Language selector accessible from all screens

### Translation Guidelines
- Keep strings context-aware for accurate translation
- Avoid concatenating translated strings
- Allow for text expansion (German/Dutch can be 30% longer than English)
- Use Unicode throughout
