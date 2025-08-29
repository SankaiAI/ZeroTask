# Changelog

All notable changes to ZeroTask will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Shared Service Account Architecture**: Updated PRD for company internal deployment
- IT setup documentation for one-time configuration of shared credentials
- Simplified end-user experience with pre-configured sources

### Changed
- **BREAKING**: Authentication model changed from individual BYOK tokens to shared service accounts
- UX flows updated to reflect IT-managed setup vs end-user token entry
- Sources configuration now assumes pre-configured credentials

### Deprecated

### Removed

### Fixed

### Security
- Enhanced security through centralized credential management by IT team
- Reduced attack surface by eliminating individual token proliferation

## [0.1.0] - 2025-08-29

### Added
- Project Requirements Document (PRD) for ZeroTask "Daily Brief (Local)"
- Comprehensive feature specification for privacy-first cross-app summary tool
- Architecture documentation for Next.js + FastAPI/Node + SQLite stack
- Data model design for Gmail, Slack, and GitHub integration
- Milestone-based release plan (3 phases)
- OAuth integration specifications for all three platforms
- Data Engineering Requirements covering:
  - Pipeline stability and error handling
  - Data consistency and integrity
  - Performance optimization and caching
  - Monitoring and observability
  - Data governance and privacy compliance

### Notes
- Initial documentation phase complete
- Ready for development phase (Milestone 1: Slack + GitHub + Ollama)