# HEIR Platform – Quick Integration + Visual Flow

---

## 1. Clone & Setup
```bash
git clone https://github.com/djb258/HEIR-AGENT-SYSTEM.git
cd HEIR-AGENT-SYSTEM

# Copy and fill environment variables
cp .env.example .env
# Edit .env with your DB URL:
# DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## 2. Deploy Platform Schema
```bash
bash scripts/deploy-database.sh
```
✅ Creates doctrine-enforced schema, audit tables, and all baseline structures.  
⚠️ **Never** bypass this — all writes must go through the Database Gatekeeper.

---

## 3. Initialize Platform
```bash
node heir-drop-in.js
```
✅ Creates required directory structure and baseline agent/orchestrator configs.  
📦 No vendor lock-in — works on Docker, bare metal, or any cloud.

---

## 4. Integrate With Your App
**Database Writes →** Always routed through Database Gatekeeper  
**API Calls →** Always routed through API Gateway

**Add doctrine headers to every write:**
```javascript
const doctrineHeaders = {
  unique_id: "APP.01.PROC.DB.10000.001",
  process_id: "ProcessData",
  blueprint_id: "your-app-name",
  agent_signature: "your-app:timestamp:hash"
};
```

---

## 5. Deploy Anywhere
**Option A – Local/Docker Compose**
```bash
docker-compose up -d
```

**Option B – Your Cloud Provider**
- Use `Dockerfile` for builds.
- Use `.env` for environment configs.
- Deploy with your CI/CD choice.

---

## 6. Verify Compliance
Run:
```bash
pytest --maxfail=1 --disable-warnings -q
```
✅ Confirms doctrine enforcement, schema validity, and role readiness.

---

## Integration Rules (Non-Negotiable)
1. **Systemic Roles Only**: Database Gatekeeper + API Gateway.
2. **Doctrine Headers Required**: `unique_id`, `process_id`, `blueprint_id`, `agent_signature` on all writes.
3. **Single Write Path**: Through Gatekeeper only.
4. **Optional Tools via ToolAdapter**: No hard dependencies.
5. **No Vendor Lock-In**.
6. **No App Logic in Platform Code**.

---

📖 **Full Guide:** See `DEPLOYMENT-GUIDE.md` for deep dive.  
⏱ **Time to integrate:** ~5–10 minutes for basic app connection.

---

## Visual Deployment Flow

```mermaid
graph TD
    A[Clone HEIR Repo] --> B[Configure .env with DB URL]
    B --> C[Deploy Database Schema<br/>scripts/deploy-database.sh]
    C --> D[Initialize Platform<br/>node heir-drop-in.js]
    D --> E[Integrate App<br/>Add Doctrine Headers to All Writes]
    E --> F[Deploy Anywhere<br/>Docker / Cloud / On-Prem]
    F --> G[Verify Compliance<br/>pytest]
    G --> H[Production Ready 🚀]

    classDef step fill:#0d6efd,stroke:#fff,color:#fff,font-weight:bold;
    class A,B,C,D,E,F,G,H step;
```