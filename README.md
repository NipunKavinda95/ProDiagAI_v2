⚙️ ProDiag AI V2

Agentic Predictive Maintenance Copilot for Industrial Assets

From machine signals to maintenance decisions.

ProDiag AI V2 is an industrial predictive maintenance platform combining Industrial IoT, Machine Learning, Anomaly Detection, RAG, and AI-powered maintenance intelligence to help engineers monitor machine health, identify potential failures, investigate faults, and plan maintenance actions.

🚀 Product Vision

flowchart LR
A["🏭 Machine Sensors"] --> B["📡 MQTT / IIoT"]
B --> C["🧠 Machine Health"]
C --> D["📊 ML Prediction"]
D --> E["🚨 Anomaly & Fault Detection"]
E --> F["🔔 Alerts"]
F --> G["🤖 AI Diagnosis"]
G --> H["👨‍🔧 Engineer Copilot"]
H --> I["🔧 Maintenance Recommendation"]
I --> J["✅ Engineer Approval"]
J --> K["📝 Work Order"]

ProDiag AI is designed to move maintenance from reactive maintenance → predictive maintenance → AI-assisted maintenance decision-making.

✨ Key Capabilities

Capability

Description

📡 Industrial IoT

Real-time MQTT machine telemetry

🏭 Fleet Monitoring

20 simulated industrial machines

🧠 ML Prediction

Failure probability and health prediction

❤️ Health Intelligence

Continuous 0–100 machine health score

🚨 Anomaly Detection

Isolation Forest + engineering rules

🔔 Alerts

Machine condition and risk alerts

📚 RAG

Engineering maintenance knowledge retrieval

🤖 AI Diagnosis

Evidence-based potential fault diagnosis

💬 Engineer Copilot

Conversational maintenance assistance

📝 Work Orders

Engineer-approved maintenance execution

🛡️ Guardrails

Input, output, API and AI security controls

🤖 Agentic Roadmap

Planning, parts, cost, PM and scheduling

🏗️ System Architecture

flowchart TB
subgraph IIOT["🏭 Industrial Layer"]
S["Machine Sensors / PLC"]
M["MQTT Broker"]
SIM["PLC / Sensor Simulator"]
end

    subgraph BACKEND["⚙️ ProDiag Backend"]
        API["Flask API"]
        HEALTH["Health Service"]
        ML["ML Prediction"]
        ANOM["Anomaly Detection"]
        ALERT["Alert Service"]
        EVENT["Fault Event Service"]
        WO["Work Order Service"]
    end

    subgraph AI["🤖 AI Intelligence"]
        DIAG["AI Diagnosis"]
        COPILOT["Engineer Copilot"]
        RAG["RAG Retrieval"]
        PINE["Pinecone"]
        LLM["OpenAI"]
    end

    subgraph DATA["💾 Data"]
        DB["SQLite / Future PostgreSQL"]
        KB["Engineering Knowledge Base"]
    end

    SIM --> M
    S --> M
    M --> API
    API --> HEALTH
    API --> ML
    API --> ANOM
    API --> ALERT
    API --> EVENT
    API --> WO
    ML --> DIAG
    ANOM --> DIAG
    HEALTH --> DIAG
    DIAG --> LLM
    COPILOT --> LLM
    COPILOT --> RAG
    RAG --> PINE
    KB --> PINE
    API --> DB
    ALERT --> DB
    EVENT --> DB
    WO --> DB

🏭 Industrial IoT

ProDiag V2 includes a simulated industrial environment containing 20 machines with independent machine conditions and progressive fault behavior.

Machine lifecycle

stateDiagram-v2
[*] --> HEALTHY
HEALTHY --> DEGRADING
DEGRADING --> WARNING
WARNING --> CRITICAL
CRITICAL --> FAULTED
FAULTED --> REPAIRING
REPAIRING --> RESTART
RESTART --> HEALTHY

Supported conditions

HEALTHY

DEGRADING

WARNING

CRITICAL

FAULTED

REPAIRING

RESTART

Simulated fault types

Bearing wear

Cavitation

Overload

Belt misalignment

Fan imbalance

Gear wear

🧠 Machine Learning

ProDiag uses machine learning to continuously evaluate machine condition and failure risk.

Failure prediction

The failure prediction model was evaluated using:

F1-score

Precision

Recall

Confusion matrix

Classification threshold analysis

Selected model: XGBoost

❤️ ML Health Score

Score

Condition

80–100

🟢 HEALTHY

60–79

🔵 DEGRADING

40–59

🟡 WARNING

20–39

🟠 CRITICAL

0–19

🔴 FAULT

The ML health score and actual machine operational condition are treated as separate signals.

📊 Anomaly Detection

ProDiag combines machine-learning anomaly detection with engineering validation rules.

flowchart LR
A["Live Telemetry"] --> B["Feature Processing"]
B --> C["Isolation Forest"]
B --> D["Engineering Rules"]
C --> E["Anomaly Score"]
D --> F["Engineering Evidence"]
E --> G["Combined Anomaly Result"]
F --> G
G --> H["Alert / Maintenance Intelligence"]

🚨 Alerts & Fault Events

ProDiag tracks machine condition transitions and generates alerts for significant machine conditions.

HEALTHY → DEGRADING → WARNING → CRITICAL → FAULTED
↓
REPAIRING
↓
RESTART
↓
HEALTHY

Fault events are persisted so maintenance activity can be associated with the machine condition that triggered it.

📚 RAG Engineering Knowledge

ProDiag uses Retrieval-Augmented Generation to ground AI maintenance recommendations in engineering knowledge.

knowledge-base/
├── maintenance_manuals/
├── fault_codes/
├── bearing_failure_modes/
├── maintenance_sop/
├── spare_parts/
├── industry_standards/
└── historical_faults/

RAG pipeline

flowchart LR
A["Engineering Documents"] --> B["Preprocessing"]
B --> C["Section-Aware Chunking"]
C --> D["OpenAI Embeddings"]
D --> E["Pinecone"]

    Q["Engineer Question"] --> F["Query Embedding"]
    F --> E
    E --> G["Relevant Knowledge"]
    G --> H["AI Maintenance Copilot"]

Configuration

Embedding Model: text-embedding-3-small
Dimension: 1536
Vector Database: Pinecone
Index: prodiag-ai
Namespace: prodiag
Metric: cosine

Retrieved documents are treated as reference evidence, not AI instructions.

🤖 AI Maintenance Intelligence

ProDiag currently provides two connected AI capabilities.

AI Diagnosis

Provides:

Probable fault

Diagnosis

Confidence

Evidence

Recommended actions

Urgency

Escalation recommendation

Engineer Copilot

Uses:

Current Machine Context +
ML Prediction +
Anomaly Evidence +
RAG Knowledge +
Conversation Context
↓
AI Maintenance Recommendation

AI is called on demand when the engineer requests diagnosis or assistance.

💬 Engineer Copilot

The Engineer Copilot is integrated into the Machine Detail experience.

flowchart TD
A["Engineer selects machine"] --> B["Current machine context"]
B --> C["ML + anomaly information"]
C --> D["Fresh RAG retrieval"]
D --> E["Engineer question"]
E --> F["AI Copilot"]
F --> G["Grounded response"]
G --> H["Engineer decision"]

🛡️ AI Safety & Guardrails

Implemented protections include:

Input

Question validation

Question length limits

Conversation history limits

Message validation

Control-character sanitization

Prompt-injection detection

API

CORS restrictions

Request payload limits

Rate limiting

Global error handling

Safe API error messages

AI Output

Structured response validation

Required-field validation

Data-type validation

Response length limits

Evidence validation

Recommendation validation

Source validation

RAG

Retrieved engineering documents are explicitly treated as untrusted reference data and cannot override system instructions.

📝 Work Orders

AI does not automatically create work orders.

flowchart LR
A["Machine Risk"] --> B["AI Diagnosis"]
B --> C["Maintenance Recommendation"]
C --> D["Engineer Review"]
D --> E["Create Work Order"]
E --> F["Maintenance Execution"]

🤖 Agentic Maintenance Roadmap

The next major evolution is the ProDiag Maintenance Agent.

The existing AI Maintenance Copilot will evolve into an agentic maintenance decision layer.

flowchart TB
A["🤖 ProDiag Maintenance Agent"]
A --> B["🔍 Diagnosis"]
A --> C["🔧 Maintenance Planning"]
A --> D["📦 Spare Parts"]
A --> E["💰 Cost Estimation"]
A --> F["🛠️ Preventive Maintenance"]
A --> G["📅 PM Scheduling"]
A --> H["📝 Work Order Proposal"]

    B --> I["👨‍🔧 Engineer Approval"]
    C --> I
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J["Maintenance Execution"]

Planned capabilities

Diagnostic reasoning

Maintenance planning

Spare-parts recommendation

Maintenance cost estimation

Preventive maintenance planning

PM scheduling

Work-order proposal generation

Engineer approval workflow

🧑‍🔧 Human-in-the-Loop

ProDiag is designed as a decision-support system, not an autonomous machine-control system.

flowchart LR
A["AI Analysis"] --> B["Recommendation"]
B --> C["👨‍🔧 Engineer Review"]
C -->|Approve| D["Work Order / PM"]
C -->|Reject / Modify| E["Engineer Decision"]
E --> D

🖥️ Application Routes

/ Fleet Dashboard
/machines/:machineId Machine Detail
/alerts Alerts
/work-orders Work Orders

🧰 Technology Stack

Frontend

React · TypeScript · Vite · Tailwind CSS · Recharts

Backend

Python · Flask · Flask-CORS · Flask-Limiter · SQLAlchemy

Industrial IoT

MQTT · Mosquitto · Paho MQTT

Machine Learning

NumPy · Pandas · scikit-learn · XGBoost · Joblib

AI

OpenAI · LlamaIndex · Pinecone

Scheduling

APScheduler

Testing

pytest

Deployment

Vercel · Render

📁 Project Structure

ProdiagAI-v2/
├── backend/
│ ├── app.py
│ ├── database.py
│ ├── machine_config.py
│ └── services/
│ ├── ai_diagnosis_service.py
│ ├── anomaly_service.py
│ ├── alert_service.py
│ ├── copilot_service.py
│ ├── fault_event_service.py
│ ├── health_service.py
│ ├── ml_feature_service.py
│ ├── ml_prediction_service.py
│ ├── pinecone_service.py
│ ├── rag_ingestion_service.py
│ ├── rag_retrieval_service.py
│ ├── security_service.py
│ └── work_order_service.py
├── frontend/
├── simulator/
│ ├── plc_simulator.py
│ └── fault_profiles.py
├── ml/
│ ├── training/
│ ├── models/
│ └── evaluation/
├── knowledge-base/
│ ├── maintenance_manuals/
│ ├── fault_codes/
│ ├── bearing_failure_modes/
│ ├── maintenance_sop/
│ ├── spare_parts/
│ ├── industry_standards/
│ └── historical_faults/
├── .env
├── .gitignore
├── requirements.txt
└── README.md

⚙️ Local Setup

python -m venv venv
venv\Scriptsctivate
pip install -r requirements.txt

Create .env with your OpenAI and Pinecone configuration.

Run backend

python backendpp.py

Backend:

http://127.0.0.1:5000

Run frontend

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173

Run PLC simulator

From the project root:

python simulator\plc_simulator.py

🔐 Environment Variables

OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key

PINECONE_INDEX_NAME=prodiag-ai
PINECONE_NAMESPACE=prodiag
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

SECRET_KEY=
ALLOWED_ORIGINS=
INGEST=false

⚠️ Never commit real API keys to Git.

🧪 Testing

python -m py_compile backendpp.py
python -m py_compile backend\services\security_service.py
pytest

📊 Evaluation

ML

F1-score · Precision · Recall · Confusion Matrix · Threshold Analysis · MAE · RMSE · R²

RAG

Retrieval similarity · Source relevance · Engineering knowledge grounding

LLM / Copilot

Response validity · Grounding · Evidence consistency · Recommendation usefulness · Safety · Prompt-injection resistance · Conversation consistency · Error handling

Evaluation artifacts are stored under:

ml/evaluation/

☁️ Deployment Architecture

flowchart TB
U["🌐 User"] --> V["▲ Vercel<br/>React Frontend"]
V -->|HTTPS API| R["⚡ Render<br/>Flask Backend"]
R --> O["OpenAI"]
R --> P["Pinecone"]
R --> DB["Production Database"]

Frontend

Vercel → React + Vite

Backend

Render → Flask API

Production CORS

ALLOWED_ORIGINS=https://your-frontend-domain.com

🔌 API Overview

Machines

GET /api/machines
GET /api/machines/<machine_id>
GET /api/machines/<machine_id>/ai-diagnosis

Engineer Copilot

POST /api/machines/<machine_id>/ai-diagnosis/chat

Alerts

GET /api/alerts

Work Orders

GET /api/work-orders
POST /api/work-orders

RAG

GET /api/rag/search

📈 Current Project Status

Component

Status

Industrial IoT

✅

20-Machine Fleet

✅

MQTT Telemetry

✅

Machine Health

✅

ML Failure Prediction

✅

ML Health Score

✅

Anomaly Detection

✅

Alerts

✅

Fault Event Tracking

✅

RAG Knowledge Base

✅

Pinecone Retrieval

✅

AI Diagnosis

✅

Engineer Copilot

✅

Work Orders

✅

AI Guardrails

✅

ML Evaluation

✅

Application Evaluation

🔄

End-to-End Validation

🔄

Production Deployment

🔄

Agentic Maintenance Layer

🚀 Next

🗺️ Development Roadmap

timeline
title ProDiag AI V2 Roadmap

    section Foundation
        Industrial IoT : MQTT / PLC Simulator
        Fleet Monitoring : Machine Health
        ML : Failure Prediction
        Anomaly Detection : Alerts

    section AI
        RAG : Engineering Knowledge
        AI Diagnosis : Evidence-based Diagnosis
        Engineer Copilot : Conversational Support

    section Reliability
        Evaluation : ML / RAG / LLM
        Guardrails : Security / Validation
        End-to-End Testing : System Validation

    section Agentic
        Maintenance Agent : Diagnosis + Tools
        Maintenance Planning : Action Plans
        Spare Parts : Parts Recommendation
        Cost Estimation : Maintenance Cost
        Preventive Maintenance : PM Planning
        PM Scheduling : Maintenance Windows
        Work Order Agent : Engineer Approval

    section Deployment
        Vercel : Frontend
        Render : Backend
        Production Database : Scalable Storage

🎯 Final Product Direction

flowchart TB
A["🏭 Industrial Asset"] --> B["📡 Telemetry"]
B --> C["🧠 ML + Anomaly Detection"]
C --> D["🚨 Risk / Alert"]
D --> E["🤖 ProDiag Maintenance Agent"]

    E --> F["🔍 Diagnose"]
    E --> G["🔧 Plan"]
    E --> H["📚 Retrieve"]
    E --> I["📦 Spare Parts"]
    E --> J["💰 Cost Estimate"]
    E --> K["🛠️ PM Recommendation"]
    E --> L["📅 PM Schedule"]

    F --> M["👨‍🔧 Engineer Approval"]
    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M

    M --> N["📝 Work Order"]
    N --> O["Maintenance Execution"]

💡 Core Principle

AI should help engineers make better maintenance decisions — not replace engineering responsibility.

ProDiag AI V2 combines machine data, predictive analytics, engineering knowledge, AI reasoning, and agentic automation to create a practical path from:

Prediction → Diagnosis → Planning → Maintenance Action

⚙️ ProDiag AI V2

Agentic Predictive Maintenance Copilot for Industrial Assets

Industrial IoT · Machine Learning · RAG · AI · Agentic Automation
