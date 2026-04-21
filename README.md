# RAG Assistant

A Demo Retrieval-Augmented Generation system for document question-answering, built with FastAPI and React.

**Live Demo:** https://demoragassistant.web.app

**Tech Stack:** FastAPI, React, OpenAI GPT-3.5-turbo, FAISS, Docker

---

## What This Project Does

- Upload PDF and TXT documents for intelligent Q&A
- Chunks documents and generates embeddings using OpenAI's text-embedding-3-small
- Performs semantic search over document vectors using FAISS
- Generates contextually-aware answers using GPT-3.5-turbo
- Implements rate limiting and usage tracking for cost control
- Provides production-ready deployment configuration with Docker

---

## Why This Project Matters

This is a production-grade AI system demonstrating core competencies in building real-world LLM applications:

**Retrieval-Augmented Generation (RAG):** Combines vector search with LLMs to answer questions based on custom documents, reducing hallucinations and grounding responses in factual content.

**Vector Search Infrastructure:** Implements FAISS-based semantic search with persistent storage, enabling efficient similarity matching across embedded document chunks.

**Cost Control & Rate Limiting:** Enforces per-IP hourly/daily query limits and global monthly caps to prevent API cost overruns in production environments.

**Production Deployment:** Includes Docker containerization, comprehensive deployment documentation, and cold-start UX optimizations for free-tier hosting platforms.

---

## Features

- Document upload with validation (PDF, TXT)
- Intelligent text chunking with overlap for context preservation
- Vector embedding generation and storage
- Semantic similarity search across document corpus
- Context-aware answer generation with source attribution
- Multi-tier rate limiting (hourly, daily, global)
- Session-based upload tracking
- Persistent FAISS vector store with document removal capability
- Responsive UI with real-time usage indicators
- Cold-start notifications for serverless deployments
- Comprehensive test coverage (backend & frontend)

---

## Architecture Overview

### Data Flow

```
1. Document Upload
   └─> Text Extraction (PyMuPDF for PDF, plain text for TXT)
   └─> Text Chunking (configurable size with overlap)
   └─> Embedding Generation (OpenAI text-embedding-3-small)
   └─> Vector Storage (FAISS index with metadata)

2. Query Processing
   └─> Query Embedding Generation
   └─> Similarity Search (FAISS top-k retrieval)
   └─> Context Assembly (relevant chunks with source attribution)
   └─> LLM Answer Generation (GPT-3.5-turbo with chat history)
   └─> Response Delivery (answer + sources)
```

### Key Architecture Decisions

**Chunking Strategy:** Uses overlapping chunks (default 1000 chars, 200 overlap) to preserve context across boundaries while maintaining reasonable embedding sizes.

**Vector Store:** FAISS CPU implementation with pickle persistence provides fast similarity search without GPU requirements, suitable for demo-scale deployment.

**Rate Limiting:** Three-tier approach (hourly, daily, global) with IP-based tracking prevents abuse while allowing legitimate usage patterns.

**Embedding Storage:** Stores embeddings alongside document metadata to enable efficient document removal without full index reconstruction.

**Source Attribution:** Prepends source filenames to context chunks to improve LLM's ability to cite specific documents in answers.

---

## Tech Stack

### Backend
- **Framework:** FastAPI 0.115.0
- **Server:** Uvicorn 0.30.6
- **LLM & Embeddings:** OpenAI 1.51.0 (GPT-3.5-turbo, text-embedding-3-small)
- **Vector Search:** FAISS 1.9.0 (CPU)
- **Document Processing:** PyMuPDF 1.27.2 (PDF text extraction)
- **Testing:** pytest 8.3.4, pytest-asyncio 0.24.0
- **Environment:** Python 3.11

### Frontend
- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.2.0
- **Testing:** Vitest 1.0.4, @testing-library/react 14.1.2
- **Runtime:** Node.js 20

### Infrastructure
- **Containerization:** Docker with docker-compose
- **Deployment:** Render (backend), Firebase/Netlify (frontend recommended)
- **Storage:** Local file system with bind mounts

---

## Live Demo

https://demoragassistant.web.app

### How to Use
1. Upload a PDF or TXT document
2. Wait for processing confirmation
3. Ask questions about the uploaded content
4. View answers with source file attribution

**Demo Limitations:** Free-tier hosting may experience 30-60 second cold starts on first request after inactivity.

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenAI API key

### Local Development

1. Clone the repository
```bash
git clone https://github.com/JCoder9/DemoRagAssistant.git
cd DemoRagAssistant
```

2. Set up backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment
```bash
# Create .env file in backend directory
echo "OPENAI_API_KEY=your_key_here" > .env
```

4. Set up frontend
```bash
cd ../frontend
npm install
```

5. Run development servers
```bash
# Terminal 1 - Backend (from backend directory)
uvicorn app.main:app --reload

# Terminal 2 - Frontend (from frontend directory)
npm run dev
```

Access the application at `http://localhost:5173`

### Docker Setup

```bash
# Set environment variable
export OPENAI_API_KEY=your_key_here

# Start all services
docker-compose up --build
```

Access at `http://localhost:5173` (frontend) and `http://localhost:8000/docs` (API docs)

---

## Deployment

### Current Setup
- **Backend:** Deployable to Render, AWS Elastic Beanstalk, or any Docker-compatible platform
- **Frontend:** Recommended for Firebase Hosting, Netlify, or Vercel (CDN + no cold starts)

### Quick Deploy to Render

1. Create Web Service for backend
   - Runtime: Docker
   - Environment: `OPENAI_API_KEY=your_key`
   - Region: US West

2. Create Static Site for frontend
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
   - Environment: `VITE_API_URL=https://your-backend.onrender.com`

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including AWS, VPS, and production optimization.

---

## Limitations & Demo Mode

### Rate Limits (Cost Control)
- **10 queries per hour** per IP address
- **30 queries per day** per IP address
- **500 queries per month** globally
- **2 second cooldown** between requests
- **5 file uploads** per session

These limits prevent API cost overruns while demonstrating rate limiting implementation for production systems.

### Technical Constraints
- **Maximum file size:** 10 MB
- **Supported formats:** PDF, TXT only
- **Vector store:** In-memory FAISS (resets on server restart in non-persistent deployments)
- **Cold starts:** Free-tier deployments may sleep after 15 minutes of inactivity

### Production Considerations

For production deployment, consider:
- Persistent vector storage (database or cloud storage)
- Increased rate limits or usage-based pricing
- Redis-based rate limiting for distributed systems
- File upload to cloud storage (S3, GCS)
- Enhanced security (authentication, input validation)
- Monitoring and observability (logging, metrics, alerts)

---

## Testing

### Backend Tests
```bash
cd backend
pytest
```

Test coverage includes:
- Document loading and chunking
- Embedding service integration
- Vector store operations
- Rate limiting logic
- API endpoint validation

### Frontend Tests
```bash
cd frontend
npm test
```

Test coverage includes:
- Component rendering and interactions
- API service mocking
- File upload workflows
- Chat interface behavior

---

## Project Structure

```
RagAssistant/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── config.py        # Configuration defaults
│   │   └── main.py          # FastAPI application
│   ├── tests/               # Backend test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

---

## License

This project is a portfolio demonstration piece. Feel free to reference for learning purposes.

---

## Contact

For questions or collaboration opportunities, please reach out via GitHub.
