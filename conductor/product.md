# Product Guide: TSS PPM v3.0

## Vision Statement

TSS PPM (Performance Portfolio Management) v3.0 is a web-based HR performance scoring application that replaces Excel-based annual employee reviews with a modern, streamlined digital platform. The system enables faster, more efficient performance evaluations through an intuitive 9-grid scoring interface, voice-powered input, and multi-language support.

## Target Users

| Role | Description |
|------|-------------|
| **Employee** | View and edit own goals, view reviews, sign off on completed reviews |
| **Manager** | Score team reviews, approve goal changes, access team dashboard and analytics |
| **HR** | View all reviews within OpCo, access organization statistics, manage calibration sessions |
| **Admin** | Manage OpCo settings, users, and system configuration (no access to review content for GDPR compliance) |

## Primary Business Outcome

**Streamlined Review Process** - Replace manual Excel-based workflows with a faster, more efficient digital process that reduces administrative burden and accelerates the annual performance review cycle.

## Core Capabilities

### 9-Grid Performance Scoring
- **WHAT-axis (Goals)**: Up to 9 weighted goals (must total 100%), scored 1-3
  - Goal types: Standard, KAR (Key Achievement Required), SCF (Success Critical Factor)
- **HOW-axis (Competencies)**: 6 competencies per TOV level (A/B/C/D), each scored 1-3
  - Based on the IDE Competency Framework
- **VETO Rules**: Automatic score adjustments for critical underperformance
- **Visual 9-Grid**: Real-time 3×3 matrix visualization as scores are entered

### Review Workflow
- Three-stage annual cycle: Goal Setting → Mid-Year Review → End-Year Review
- Digital signature workflow for employee and manager sign-off
- Goal change request and approval system
- Task lists for pending actions

### Voice Input
- Hold-to-dictate functionality for hands-free feedback entry
- Primary use case: Enable managers to quickly dictate feedback during review sessions
- Supports all three languages (EN/NL/ES)

### Multi-Language Support
- Full localization for English, Dutch, and Spanish
- UI translations and competency descriptions
- Language priority: User preference → OpCo default → Browser → English fallback

### Analytics & Reporting
- Team performance dashboards for managers
- Organization-wide statistics for HR
- Calibration sessions for fair and consistent ratings
- Automated PDF-A format reports with company branding
- Excel export options

## Target Markets

**Global with European Focus** - Primary deployment in European markets (Netherlands, Spain) with the architecture designed to scale internationally as needed.

## Deployment Model

**Decentralized OpCo Hosting** - Each Operating Company hosts their own TSS PPM instance to ensure:
- Data privacy and sovereignty
- Compliance with local regulations
- Prevention of centralized data access concerns
- OpCo-level customization and control

Initial rollout follows a single-OpCo pilot approach before expanding to additional OpCos.

## Brand Identity

- **Primary Magenta**: #CC0E70 (accents, buttons, focus states)
- **Primary Navy Blue**: #004A91 (headings, secondary elements)
- **Typography**: Tahoma font family
