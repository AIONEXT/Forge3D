# Contributing to Forge3D

Thank you for your interest in contributing to Forge3D! 🎉

## Getting Started

1. **Fork the repository** and clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/forge3d.git
   cd forge3d
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov coverage ruff
   ```

4. **Run the tests**:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** and ensure all tests pass:
   ```bash
   pytest tests/ -v
   ruff check .
   ruff format . --check
   ```

3. **Commit your changes** with a descriptive message:
   ```bash
   git commit -m "Add amazing feature"
   ```

4. **Push to your branch** and open a Pull Request:
   ```bash
   git push origin feature/amazing-feature
   ```

## Code Style

- Use Python 3.10+ syntax
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Use `ruff` for linting and formatting
- Run `pytest` before submitting

## Adding New Categories

To add a new product category:

1. Add the category to `CATEGORIES` in `ai_engine.py`
2. Add dimensions and properties to `printers_materials.py` if needed
3. Add builder logic to `mesh_engine.py` `build()` function
4. Add default dimensions to `generators/parametric.py` if applicable

## Reporting Issues

- Use the GitHub issue tracker
- Include reproduction steps and environment details
- Attach logs if applicable

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
