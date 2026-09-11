# Forge3D — AI 3D Product Factory

Fully automated: **product description + printer + material → commercial-ready product for sale.**

![Forge3D](https://img.shields.io/badge/Forge3D-AI%203D%20Product%20Factory-blue)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

![Forge3D Demo](https://img.shields.io/badge/Demo-Live%20Site-grey)

## ✨ Features

- **AI-Powered Design**: Type a description → get a parametric 3D model instantly
- **Commercial Package**: Auto-generated Etsy/Amazon listing with SEO title, bullets, description, and pricing
- **Real-Time 3D Viewer**: Interactive Three.js preview with auto-rotate, wireframe, and screenshot
- **Multi-Provider AI**: OpenAI, Anthropic, Gemini, Groq, Ollama, and more for copy enhancement
- **Offline-First**: No API key required — fully functional locally
- **8 Printers, 8 Materials**: Real-world specs with compatibility checking
- **4 Quality Levels**: Draft, Standard, Fine, Ultra
- **STL + JSON + HTML Export**: Download models, listings, and sale pages
- **Docker-Ready**: Containerized for any cloud deployment
- **CI/CD**: GitHub Actions pipeline included

## 🚀 Quick Start

### Soft run (default: offline safe)

```bash
pip install -r requirements.txt
python start_local.py
```

Open <http://127.0.0.1:5000>.

### Direct Flask app

```bash
pip install -r requirements.txt
python app.py
```

### Docker

```bash
docker build -t forge3d .
docker run -p 8000:8000 --env-file .env.example forge3d
```

Or with Docker Compose:

```bash
docker-compose up --build
```

### Gunicorn production

```bash
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 wsgi:app
```

## 📦 Deployment

### Render

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Set the build command and start command:

   ```text
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT wsgi:app
   ```

4. Set environment variables:

   ```text
   FORGE3D_PORT = 8000
   FORGE3D_DEBUG = false
   FORGE3D_SECRET_KEY = (auto-generated)
   ```

5. Deploy — `render.yaml` is pre-configured

### Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login and create an app:

   ```bash
   heroku login
   heroku create forge3d-app
   ```

3. Set environment variables:

   ```bash
   heroku config:set FORGE3D_DEBUG=false
   heroku config:set FORGE3D_SECRET_KEY=$(openssl rand -hex 32)
   ```

4. Deploy:

   ```bash
   git push heroku main
   ```

5. Or use `heroku.yml` with the Heroku CI pipeline

### Railway

1. Create a new project on [Railway](https://railway.app)
2. Deploy from GitHub repository
3. `railway.toml` is pre-configured
4. Set environment variables

### VPS / Self-Hosted

```bash
git clone https://github.com/YOUR_USERNAME/forge3d.git
cd forge3d
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
```

Use Nginx as reverse proxy with SSL.

## 🎮 Use the App

1. Type a product description (e.g., `ribbed twist vase, modern home decor, matte finish`)
2. Pick a printer profile
3. Pick a material
4. Adjust size slider and profit margin
5. Hit **Generate**
6. Preview in 3D, export STL/JSON/HTML, and download a sales page
7. Optionally use **AI Copy Boost** for enhanced listings

## 🔌 API Reference

### Get Printers

```bash
GET /api/printers
```

### Get Materials

```bash
GET /api/materials
```

### Generate Product

```bash
POST /api/run
Content-Type: application/json

{
  "description": "ribbed twist vase, modern home decor",
  "printer_id": "bambu_x1c",
  "material_id": "pla",
  "quality_id": "standard",
  "scale": 1.0,
  "margin": 0.55
}
```

### AI Copy Boost

```bash
POST /api/copy-boost
Content-Type: application/json

{
  "listing": { ... },
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

### Download Files

```bash
GET /download/<filename>
```

### Health Check

```bash
GET /health
GET /ready
```

## 🤖 AI Providers

Set one of these environment variables before starting:

| Provider | Variables |
| --- | --- |
| OpenAI | `AI_PROVIDER=openai`, `OPENAI_API_KEY=...`, `AI_MODEL=gpt-4o-mini` |
| Anthropic | `AI_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=...`, `AI_MODEL=claude-3-5-sonnet-latest` |
| Google Gemini | `AI_PROVIDER=gemini`, `GEMINI_API_KEY=...`, `AI_MODEL=gemini-2.0-flash` |
| Groq | `AI_PROVIDER=groq`, `GROQ_API_KEY=...`, `AI_MODEL=llama-3-1-8b-instant` |
| OpenRouter | `AI_PROVIDER=openrouter`, `OPENROUTER_API_KEY=...`, `AI_MODEL=meta-llama/llama-3.1-8b-instruct` |
| Together | `AI_PROVIDER=together`, `TOGETHER_API_KEY=...`, `AI_MODEL=meta-llama/Llama-3.1-8B-Instruct-Turbo` |
| Mistral | `AI_PROVIDER=mistral`, `MISTRAL_API_KEY=...`, `AI_MODEL=mistral-small-latest` |
| Ollama | `AI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434`, `OLLAMA_MODEL=llama3.1` |
| Local Server | `AI_PROVIDER=local`, `LOCAL_LLM_BASE_URL=http://localhost:8001`, `LOCAL_LLM_MODEL=my-model` |
| Offline | `AI_PROVIDER=offline` (default, no API key needed) |

## ⚙️ Configuration

Environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `FORGE3D_HOST` | `0.0.0.0` | Host address |
| `PORT` | `FORGE3D_PORT` or `5000` | Listening port; cloud platforms set `PORT` automatically |
| `FORGE3D_DEBUG` | `false` | Debug mode |
| `FORGE3D_SECRET_KEY` | generated at startup | Stable Flask secret key for deployments; set this explicitly when needed |
| `AI_PROVIDER` | `offline` | AI provider |
| `API_KEY` | (empty) | Generic API key fallback |

## 🛠️ Development

### Run Tests

```bash
pip install pytest pytest-cov coverage ruff
pytest tests/ -v
```

### Lint

```bash
pip install ruff
ruff check .
ruff format .
```

### Build Docker Image

```bash
docker build -t forge3d .
docker run -p 8000:8000 --env-file .env.example forge3d
```

## 📂 Project Structure

```text
forge3d/
├── app.py                  # Flask application factory
├── wsgi.py                 # WSGI entry point
├── config.py               # App configuration
├── ai_engine.py            # Description → spec + commercial copy
├── mesh_engine.py          # 3D mesh generation + STL writer
├── providers.py            # AI provider integrations
├── printers_materials.py   # Printer and material database
├── generators/             # Legacy generators module
│   ├── __init__.py
│   ├── parametric.py       # Alternative mesh builder
│   ├── commercial.py       # Alternative commercial kit builder
│   ├── printers.py         # Alternative printer database
│   ├── slicer.py           # Alternative slice estimator
│   └── ai_designer.py      # Alternative AI designer
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── app.js              # Frontend JavaScript
│   └── style.css           # Dark theme CSS
├── outputs/                # Generated STL/JSON files
├── tests/
│   └── test_app.py         # Comprehensive test suite
├── .github/workflows/
│   └── ci.yml              # CI/CD pipeline
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Local Docker Compose
├── pyproject.toml          # Python package configuration
├── requirements.txt        # Python dependencies
├── pytest.ini              # Test configuration
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker image
├── render.yaml             # Render deployment config
├── railway.toml            # Railway deployment config
├── heroku.yml              # Heroku deployment config
├── runtime.txt             # Heroku Python runtime
├── README.md               # This file
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guide
├── LICENSE                 # MIT License
└── start_local.py          # Local development entry point
```

## 📝 Notes

- Offline-first: no API key is required.
- STLs are generated as manifold-style procedural meshes and should be sliced with Bambu Studio, PrusaSlicer, or Cura before sale.
- Pricing uses built-in material cost and printer runtime assumptions; adjust them in `printers_materials.py`.
- `start_local.py` is the recommended local soft-run entry point when you want a server without any hosted provider dependency.
- All generated files are output to `outputs/` — add this to `.gitignore` before deploying.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📋 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/), [Three.js](https://threejs.org/), and [NumPy](https://numpy.org/)
- AI integrations powered by [OpenAI](https://openai.com/), [Anthropic](https://anthropic.com/), [Google](https://deepmind.com/), and more
- 3D models rendered with [Three.js](https://threejs.org/)
