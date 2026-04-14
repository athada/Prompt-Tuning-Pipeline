# Prompt Tuning Pipeline

A full-stack, production-grade **Automated LLM Prompt Optimization System** using an "LLM-as-a-Judge" feedback loop. This system evaluates, iterates, and optimizes prompts using a microservices architecture powered by FastAPI, Temporal.io, PydanticAI, and React with proper MVC architecture.

## 🏗️ Architecture Overview

The system follows **MVC (Model-View-Controller) architecture** with clean separation of concerns:

### System Components
1. **API & Worker Service** (Python) - FastAPI + Temporal + PydanticAI with MVC structure
2. **MongoDB Database** - Stores prompts with agent names and chain tracking  
3. **Temporal Server** - Orchestrates workflows
4. **React Frontend** - TypeScript + Zustand + Tailwind CSS
5. **Ollama (Host)** - Local LLM engine (gemma2) with MPS acceleration

### MVC Structure (API/Worker)

```
api-worker/
├── api/                          # API Layer
│   ├── app.py                    # FastAPI app + lifespan
│   └── routes/                   # Route definitions by domain
│       ├── inference_routes.py
│       ├── prompt_routes.py
│       ├── evaluation_routes.py
│       └── optimization_routes.py
│
├── controller/                   # Controller Layer
│   ├── inference_controller.py   # Inference request handlers
│   ├── prompt_controller.py      # Prompt management handlers
│   ├── evaluation_controller.py  # Evaluation handlers
│   └── optimization_controller.py # Workflow handlers
│
├── service/                      # Service Layer (Business Logic)
│   ├── database_service.py       # MongoDB connection
│   ├── prompt_service.py         # Prompt CRUD + chain tracking
│   ├── llm_service.py            # PydanticAI agents (Generator/Judge/Inference)
│   ├── evaluation_service.py    # Evaluation logic
│   ├── temporal_service.py       # Worker lifecycle
│   ├── workflow_service.py       # Workflow execution
│   ├── workflows.py              # Temporal workflow definitions
│   └── workflow_activities.py    # Activity functions
│
├── models/                       # Data Models
│   ├── database_models.py        # MongoDB schemas (with agent_name, parent_chain)
│   └── api_models.py             # API request/response models
│
├── prompts/                      # Base Prompts Configuration
│   └── base_prompts.py           # 6 agents with descriptions
│
├── utils/                        # Utilities
│   ├── logging_utils.py
│   └── validation_utils.py
│
├── config.py                     # Configuration
├── main.py                       # Entry point
└── seed_db.py                    # Database seeding
```

## 🤖 Pre-configured Agents

The system includes 6 specialized agents with unique names:

1. **general_assistant** - General-purpose Q&A
2. **technical_expert** - Technical/coding questions  
3. **code_reviewer** - Code quality assessment
4. **data_analyst** - Data analysis and visualization
5. **creative_writer** - Content creation
6. **research_assistant** - Information gathering

Each agent has:
- `agent_name`: Unique identifier
- `prompt_text`: System prompt
- `parent_chain`: Full lineage tracking (e.g., `["id1", "id2", "id3"]`)
- `performance_score`: Quality metric

## 🔄 The Optimization Loop

```
1. User runs inference → Judge evaluates (0-10 score)
   ↓
2. Low scores detected (< threshold)
   ↓
3. Fetch recent poor evaluations
   ↓
4. Generator Agent analyzes feedback
   ↓
5. Creates improved experimental prompt
   ↓  (parent_chain: old_chain + parent_id)
6. Test new prompt with sample queries
   ↓
7. Compare scores
   ↓
8. Flag for human review if better
   ↓
9. User promotes → becomes new active prompt
   ↓  (parent_chain: old_chain + exp_id)
10. Cycle continues (full history preserved)
```

## 🚀 Quick Start

### Two Runtime Modes

#### 🔧 Development Mode (Recommended for Development)
- API/Worker and UI run **locally** with hot reload
- Only infrastructure (MongoDB, Temporal) runs in Docker
- Fast iteration, easy debugging

```bash
# One-time setup (run from repo root)
chmod +x scripts/*.sh
./scripts/startup-dev.sh

# Then in separate terminals:
# Terminal 1: API/Worker
cd api-worker && source venv/bin/activate && python main.py

# Terminal 2: UI
cd ui && npm run dev

# Access: http://localhost:5173 (UI), http://localhost:8000 (API)
```

#### 🐳 Production/Deploy Mode  
- Everything runs in Docker containers
- Production-ready deployment

```bash
chmod +x scripts/*.sh
./scripts/startup-prod.sh

# Access: http://localhost:3000
```

### Prerequisites
- macOS (for MPS acceleration via Ollama)
- **Docker** with a working **Compose** command: either `docker compose` (Compose V2 CLI plugin) or standalone `docker-compose`. Scripts and `make` use `scripts/dcompose`, which tries `docker compose` first, then `docker-compose`. If you see errors about missing `~/.docker/cli-plugins/docker-compose`, reinstall Docker Desktop or run `brew install docker-compose`.
- Ollama: `brew install ollama`
- Python 3.11+ (dev mode)
- Node.js 20+ (dev mode)

## 📊 Database Schema

### `active_prompts` (Production Prompts)
```javascript
{
  _id: ObjectId,
  agent_name: "general_assistant",      // NEW: Agent identifier
  prompt_text: "You are...",
  prompt_type: "system",
  parent_chain: ["id1", "id2", "id3"],  // NEW: Full lineage
  version: 1,
  performance_score: 8.2,
  usage_count: 156,
  created_at: ISODate,
  updated_at: ISODate,
  metadata: {...}
}
```

### `experimental_prompts` (Testing)
```javascript
{
  _id: ObjectId,
  agent_name: "general_assistant",
  prompt_text: "Improved version...",
  parent_prompt_id: "abc123",
  parent_chain: ["id1", "id2", "abc123"], // NEW: Includes parent
  generation_rationale: "Fixed...",
  test_score: 8.7,
  status: "experimental",
  created_at: ISODate,
  tested_at: ISODate,
  metadata: {...}
}
```

### `evaluation_logs` (Judge Feedback)
```javascript
{
  _id: ObjectId,
  prompt_id: "abc123",
  prompt_text: "...",
  input_query: "What is AI?",
  output_response: "AI is...",
  judge_feedback: "Good clarity, could be more concise",
  judge_score: 7.5,
  execution_time_ms: 1250,
  created_at: ISODate,
  metadata: {
    strengths: [...],
    weaknesses: [...],
    recommendations: [...]
  }
}
```

## 🎯 API Endpoints

### Inference
- `POST /api/inference` - Run inference
- `GET /api/health` - Health check

### Prompts  
- `GET /api/prompts/active` - List active prompts
- `GET /api/prompts/experimental` - List experimental
- `GET /api/prompts/experimental/top` - Top-scoring experimental
- `POST /api/prompts/promote` - Promote experimental to active

### Evaluations
- `GET /api/evaluations/recent` - Recent evaluations
- `GET /api/evaluations/prompt/{id}` - Evaluations for specific prompt

### Optimization
- `POST /api/optimization/trigger` - Trigger optimization workflow
- `GET /api/optimization/status/{id}` - Check workflow status

## 🖥️ Frontend Features

### Tab 1: Inference
- Chat interface with active prompts
- Real-time execution time
- Judge score display (0-10)
- Message history

### Tab 2: Prompt Tuning
- **Active Prompts**: Current production prompts with agent names
- **Experimental Prompts**: Top candidates with parent chain
- **Recent Evaluations**: Monitor all judge scores
- **Optimization Trigger**: Manual workflow start
- **Auto-refresh**: Updates after optimization

## 📋 Development Mode Details

### What Runs Where

| Service | Location | Port |
|---------|----------|------|
| MongoDB | Docker | 27017 |
| Temporal | Docker | 7233 |
| Temporal UI | Docker | 8088 |
| **API/Worker** | **Local (Python)** | **8000** |
| **UI** | **Local (Vite)** | **5173** |
| Ollama | Host | 11434 |

### Setup & Daily Workflow

```bash
# One-time setup
./scripts/startup-dev.sh

# Daily: Terminal 1 (API)
cd api-worker
source venv/bin/activate
python main.py

# Daily: Terminal 2 (UI)
cd ui
npm run dev

# Stop when done
./scripts/shutdown-dev.sh
```

### Configuration
- `api-worker/.env.dev` - Connects to `localhost:7233`, `localhost:27017`
- `ui/.env.dev` - Connects to `localhost:8000`

### Advantages
✅ Hot reload (Python + React)  
✅ Easy debugging (IDE breakpoints)  
✅ Fast iteration (no Docker rebuild)  
✅ Full IntelliSense  
✅ Low resource usage

## 🐳 Production Mode Details

### What Runs Where

| Service | Location | Port |
|---------|----------|------|
| MongoDB | Docker | 27017 |
| Temporal | Docker | 7233 |
| Temporal UI | Docker | 8088 |
| **API/Worker** | **Docker** | **8000** |
| **UI** | **Docker** | **3000** |
| Ollama | Host | 11434 |

### Setup & Deployment

```bash
./scripts/startup-prod.sh

# View logs
make prod-logs

# Rebuild
make prod-rebuild

# Stop
./scripts/shutdown-prod.sh
```

### Configuration
- `api-worker/.env` - Connects to `temporal:7233`, `mongodb:27017` (Docker network)
- `ui/.env` - Connects to `localhost:8000` (exposed port)

### Advantages
✅ Production-ready  
✅ Complete isolation  
✅ Easy deployment  
✅ Consistent environment  
✅ Scalable

## 🛠️ Common Commands

```bash
# Development Mode
make dev-start          # Start infrastructure
make dev-api            # Run API locally
make dev-ui             # Run UI locally
make dev-logs           # Infrastructure logs
make dev-stop           # Stop infrastructure

# Production Mode
make prod-start         # Start everything
make prod-logs          # All logs
make prod-rebuild       # Rebuild containers
make prod-stop          # Stop everything

# Utilities
make help               # Show all commands
make clean              # Remove all containers/volumes
make health             # Check service health
make status             # Show running services
```

## 🔧 Environment Configuration

This repository is **demo / educational code**: `.env` files are **not** listed in `.gitignore` so you can clone and run with the checked-in defaults. **If you use this project in production**, treat environment files as secrets: add `.env` (and any paths that hold credentials) back to `.gitignore`, use a secrets manager or CI/CD variables, and never commit real passwords or API keys.

### Root `.env`
```bash
MONGODB_PORT=27017
API_PORT=8000
UI_PORT=3000
TEMPORAL_PORT=7233
TEMPORAL_WEB_PORT=8088
```

### `api-worker/.env` (Production)
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Critical for Docker
TEMPORAL_HOST=temporal:7233
MONGODB_URI=mongodb://mongodb:27017
OLLAMA_MODEL=gemma2
SCORE_THRESHOLD=7.0
BATCH_SIZE=10
```

### `api-worker/.env.dev` (Development)
```bash
OLLAMA_BASE_URL=http://localhost:11434  # Direct host connection
TEMPORAL_HOST=localhost:7233
MONGODB_URI=mongodb://localhost:27017
```

## 🎓 How It Works

### Request Flow (MVC)
```
User Request (POST /api/inference)
  ↓
API Route (inference_routes.py)
  ↓
Controller (InferenceController)
  ├─→ PromptService.get_active_prompt()
  ├─→ LLMService.run_inference()
  └─→ EvaluationService.evaluate_and_log()
  ↓
Services interact with:
  ├─→ MongoDB (via database_service)
  ├─→ Ollama (via llm_service)
  └─→ Temporal (if needed)
  ↓
Response ← Controller ← Route ← HTTP
```

### Prompt Chain Example
```
Base: general_assistant (abc)
  parent_chain: []
  ↓
Experimental v2 (def)
  parent_chain: ["abc"]
  parent_prompt_id: "abc"
  ↓
Active v2 [Promoted] (ghi)
  parent_chain: ["abc", "def"]
  ↓
Experimental v3 (jkl)
  parent_chain: ["abc", "def", "ghi"]
  parent_prompt_id: "ghi"
```

### PydanticAI Integration
- **Structured Outputs**: Type-safe LLM responses
- **Three Agents**:
  - Generator: Creates improved prompts
  - Judge: Evaluates quality (0-10 score)
  - Inference: Generates responses
- **Ollama Connection**: Via `host.docker.internal:11434` (prod) or `localhost:11434` (dev)

### Temporal Workflows
- **PromptOptimizationWorkflow**: Main optimization loop
- **Activities**: Fetch data, run agents, update database
- **Fault Tolerance**: Automatic retries
- **Visibility**: Track in Temporal UI (http://localhost:8088)

## 🧪 Testing the System

1. **Run Inference**: Inference tab → Ask questions
2. **View Scores**: Tuning tab → See judge evaluations
3. **Trigger Optimization**: Click "Trigger Optimization"
4. **Review Experimental**: Check top-scoring prompts
5. **Promote**: Click "Promote to Active"
6. **View Chain**: See parent_chain in metadata

## 🐛 Troubleshooting

### Development Mode
**API won't start**:
```bash
cd api-worker && source venv/bin/activate
pip install -r requirements.txt
```

**UI won't start**:
```bash
cd ui && rm -rf node_modules && npm install
```

**Can't connect to infrastructure**:
```bash
./scripts/dcompose -f docker-compose.dev.yml ps
./scripts/shutdown-dev.sh && ./scripts/startup-dev.sh
```

### Production Mode
**Containers won't start**:
```bash
docker ps
make prod-logs
./scripts/dcompose -f docker-compose.prod.yml down -v
./scripts/startup-prod.sh
```

**Ollama connection fails**:
```bash
ollama list
pkill ollama && ollama serve &
curl http://localhost:11434/api/tags
```

### Both Modes
**Port already in use**:
```bash
lsof -i :8000  # Check what's using the port
```

## 🔒 Production Considerations

Before deploying:

1. **Security**: Change default passwords, add authentication, enable HTTPS
2. **Monitoring**: Add logging (ELK, Datadog), health checks, alerts
3. **Scalability**: Scale workers, add indexes, implement caching (Redis)
4. **Data**: Set up backups, retention policies, replication

## 📝 Key Features Recap

✅ **MVC Architecture** - Clean separation (api → controller → service)  
✅ **6 Specialized Agents** - Each with unique name and purpose  
✅ **Complete Chain Tracking** - Full lineage in parent_chain array  
✅ **LLM-as-a-Judge** - Automatic evaluation (0-10 score)  
✅ **Automated Optimization** - Temporal workflows improve prompts  
✅ **Dual Runtime Modes** - Dev (local) and Prod (Docker)  
✅ **Type Safety** - Pydantic AI + TypeScript throughout  
✅ **Hot Reload** - Fast iteration in dev mode  
✅ **Production Ready** - Fully containerized deployment

## 🎯 Quick Reference

```bash
# DEV MODE (Fast Iteration)
./scripts/startup-dev.sh
cd api-worker && source venv/bin/activate && python main.py  # Terminal 1
cd ui && npm run dev                                         # Terminal 2
./scripts/shutdown-dev.sh

# PROD MODE (Deployment)
./scripts/startup-prod.sh
./scripts/shutdown-prod.sh

# MAKE SHORTCUTS
make help          # All commands
make dev-start     # Dev infrastructure
make prod-start    # Production mode
make clean         # Remove everything
```

## 📚 File Structure

```
Prompt-Tuning-Pipeline/
├── api-worker/             # Backend (MVC)
│   ├── api/                # Routes + App
│   ├── controller/         # Request handlers
│   ├── service/            # Business logic
│   ├── models/             # Schemas
│   ├── prompts/            # Base agents config
│   ├── utils/              # Helpers
│   ├── .env / .env.dev
│   └── main.py
├── ui/                     # Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── api.ts
│   │   ├── store.ts
│   │   └── App.tsx
│   └── .env / .env.dev
├── scripts/                # startup/shutdown + dcompose (Compose V1/V2 shim)
├── docker-compose.dev.yml  # Dev infrastructure
├── docker-compose.prod.yml # Full production
├── Makefile                # All commands (uses ./scripts/dcompose)
└── README.md               # This file
```

## 📞 Support

For issues and questions, open an issue on GitHub.

## 📝 License

MIT License - See LICENSE file

---

**Made with ❤️ using FastAPI, Temporal.io, PydanticAI, React, and Ollama**
