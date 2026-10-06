# optillm-gateway # 🚀 OptiLLM-Gateway

An intelligent LLM proxy designed for **FinOps cost management**, **smart model routing**, and precise latency/token tracking. Built with Python and Flask.

🛠️ Features
Smart Routing: Automatically redirects lightweight requests (e.g., short prompts) from high-cost models like gpt-4o to cost-effective alternatives like gpt-3.5-turbo, reducing operational expenses.

FinOps Cost Breakdown: Calculates precise input and output costs in USD per request based on granular token usage.

SQLite Audit Logging: Automatically persists all transaction metrics, latencies, and routing decisions into a local database for financial auditing.

Fallback & Mock Mode: Seamlessly switches to simulation mode for zero-cost offline testing and development.

📦 Tech Stack
Python / Flask

SQLite (Audit database)

Requests (HTTP client)

🚀 Quick Start
Clone the repository:

Bash
git clone [https://github.com/Isaa-dev/optillm-gateway.git](https://github.com/Isaa-dev/optillm-gateway.git)
cd optillm-gateway
Create and activate a virtual environment:

Bash
python -m venv venv
# Windows PowerShell:
venv\Scripts\Activate.ps1
Install dependencies:

Bash
pip install -r requirements.txt
Run the Gateway:

Bash
python main.py
📡 Endpoints
POST /v1/chat/completions: Main proxy endpoint with smart routing and FinOps injection.

GET /logs: Retrieves the recent financial audit trail from the SQLite database.

GET /health: Service health check.
