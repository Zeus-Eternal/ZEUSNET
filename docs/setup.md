## ZeusNet Dev Setup

### 🛠 Requirements
- Python 3.10+
- Node.js 20+
- Docker
- Virtualenv or venv

### 🔄 Quickstart
```bash
git clone https://github.com/your/zeusnet.git
cd zeusnet
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
npm install --prefix frontend
docker compose up -d mqtt
```

### 🚀 Launch

```bash
bash start-zeusnet.sh  # or start-zeusnet.bat on Windows
```
