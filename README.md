# Resume Analyzer — Final (Professional)

Resume Analyzer is a RAG-based (Retrieval-Augmented Generation) resume analysis and optimization tool. It provides an ATS-focused score, highlights matches and gaps against a job description, and can generate an optimized, ATS-friendly resume. The app uses a Streamlit frontend and a LangChain-style backend with vector search and LLM-powered analysis/rewrites.

--

**Status:** Prototype — UI and optimization flows implemented

## Key Features

- Upload a PDF resume and paste a job description to compare.
- Side-by-side resume preview with matched terms highlighted.
- Extracted "Matched" and "Unmatched" skills and action suggestions.
- LLM-powered analysis output available inline.
- Optimize Resume: generate a tailored, ATS-friendly rewrite and suggested removals/adds.
- Chat interface to ask questions about the resume (conversational retrieval).
- Download suggestions or optimized resume as TXT.

## Architecture

The project is split into two main layers: Frontend (Streamlit) and Backend (ingestion, vector store, LLM analysis).

```mermaid
flowchart LR
  U[User Browser / Streamlit UI] -->|Upload PDF + JD| F[Streamlit Frontend]
  F -->|sends file| I[PDF Ingestion]
  I -->|text chunks| V[Vector Store (FAISS)]
  V -->|retriever| R[Retrieval Layer]
  R -->|context| L[LLM (Groq / LangChain)]
  L -->|analysis JSON| F
  L -->|optimized_resume| F
  style F fill:#0b1020,stroke:#5865F2,color:#c9d1d9
  style L fill:#071019,stroke:#21a1f1,color:#c9d1d9
```

Components:
- Frontend: `app.py`, `frontend/main_app.py`, `frontend/chat_interface.py`
- PDF ingestion: `backend/pdf_ingestion.py` — extracts text and splits into chunks
- Vector store: `backend/vector_store.py` — creates FAISS index and embeddings (HuggingFace)
- Analysis: `backend/analysis.py` — contains `analyze_resume()` and `optimize_resume()` that call the LLM

## File Structure (top-level)

- app.py — Streamlit entrypoint
- requirements.txt — Python dependencies
- backend/
  - analysis.py
  - pdf_ingestion.py
  - vector_store.py
- frontend/
  - main_app.py
  - chat_interface.py

## Prerequisites

- Python 3.10+ (project uses 3.13 in CI, but 3.10+ is recommended)
- Git (optional)
- Internet connection for model API calls and HuggingFace downloads

## Recommended virtualenv setup (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# If installation of sentence-transformers stalls, install CPU torch wheel first:
pip install --index-url https://download.pytorch.org/whl/cpu torch --upgrade
pip install sentence-transformers
```

POSIX / WSL (bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install --index-url https://download.pytorch.org/whl/cpu torch --upgrade
pip install sentence-transformers
```

## Environment variables

Create a `.env` file in the repository root or set these in your environment:

- `GROQ_API_KEY` — API key for Groq LLM backend (used by `backend/analysis.py`).

Example (PowerShell):

```powershell
Set-Content -Path .env -Value 'GROQ_API_KEY=your_key_here'
# or set for current session
$env:GROQ_API_KEY="your_key_here"
```

## Run the app

Start the Streamlit UI (from project root):

```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Usage

1. Upload a PDF resume using the left upload control.
2. Paste the target job description into the Job Description field.
3. Click **Smart ATS Analysis** to extract resume text, build vectors, and get analysis.
4. Review the side-by-side preview: matched terms are highlighted; suggestions show missing skills (red) and matches (green).
5. Click **Optimize Resume** to request an LLM-tailored, ATS-friendly rewrite. Download via the provided button.

## Notes about LLM output

- `optimize_resume()` in `backend/analysis.py` asks the LLM to return JSON only. Real-world LLMs sometimes add commentary around JSON; the code attempts to extract the first JSON object, but for production you should use a structured output API (or strict response parsing validation).
- For consistent results, adjust prompts in `backend/analysis.py` and test with a variety of resumes and job descriptions.

## Testing and QA

- Manual smoke test: start app, upload a sample resume PDF and a job description, verify analysis and optimize flows.
- For automated tests: add unit tests around `backend/pdf_ingestion.py` and `backend/analysis.py` (stub LLM responses).

## Contribution

1. Fork the repo
2. Create a feature branch
3. Run tests and linters (if added)
4. Open a pull request with a clear title and description

## Troubleshooting

- If you see an ImportError about `sentence_transformers`, install it manually as shown above.
- If Streamlit fails to start due to a port issue, specify another port: `streamlit run app.py --server.port 8502`.
- If the LLM returns non-JSON for optimization, inspect logs and refine the prompt in `backend/analysis.py`.

## License & Acknowledgements

This project is provided as-is for educational and prototyping purposes. Credit to the Streamlit, LangChain, HuggingFace, and FAISS projects used in this repository.

---

If you'd like, I can also:

- Add a sample resume PDF and job description for a one-click smoke test.
- Convert `analyze_resume()` to return structured JSON like `optimize_resume()`.
- Add CI tests for dependency installation and static checks.
