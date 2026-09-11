# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-11

### Added
- Full AI 3D product factory pipeline
- Description → parametric spec → 3D mesh generation
- Commercial listing generation (title, bullets, description, SEO tags)
- Real-time 3D viewer with Three.js
- Multi-provider AI copy enhancement (OpenAI, Anthropic, Gemini, Groq, etc.)
- STL and JSON export
- Sale page HTML generation
- Compatibility validation (printer + material, bed fit)
- Slicing cost estimation
- REST API with `/api/run`, `/api/printers`, `/api/materials`, `/api/copy-boost`
- Docker deployment support
- CI/CD pipeline (GitHub Actions)
- Comprehensive test suite
- Offline-first mode (no API key required)
- Support for 8 printers and 8 materials
- 4 quality levels (Draft, Standard, Fine, Ultra)
- Profit margin calculator with pricing ladder

### Changed
- Migrated from `start_local.py` to standard Flask app entry point
- Added `pyproject.toml` for modern Python packaging
- Improved Dockerfile with multi-stage build
- Added `docker-compose.yml` for local development

### Fixed
- Fixed `.gitignore` to exclude generated outputs
- Added proper `render.yaml`, `railway.toml`, `heroku.yml` deployment configs
- Added `runtime.txt` for Heroku Python runtime
- Fixed `requirements.txt` to include all dependencies

## [0.1.0] - Initial
- Initial release of Forge3D
