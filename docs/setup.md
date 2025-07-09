## ZeusNet Dev Setup

### 🛠 Requirements
- Python 3.10+
- Docker
- Virtualenv or venv

### 🔄 Quickstart
```bash
git clone https://github.com/your/zeusnet.git
cd zeusnet
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
docker compose up -d mqtt
```

### 🚀 Launch

```bash
bash start-zeusnet.sh  # or start-zeusnet.bat on Windows
```

### 📺 GTK Desktop Viewer

Launch the desktop UI with tabs for network lists, signal charts,
map view and attack controls:

```bash
python frontend/main.py
```

Requires the `PyGObject` package with GTK **4** support.
If you encounter an error about `Gtk.ApplicationFlags` when launching the
UI, ensure you are not using leftover GTK 3 snippets; the new code relies
solely on GTK 4 APIs. The `Application.run()` method also no longer takes a
`None` parameter in GTK 4.

### 🌐 Web UI (React)

Run the browser-based dashboard with Vite:

```bash
cd webui
npm install
npm run dev
```

### ⚙️ Enable systemd Service (Optional)

```bash
sudo cp systemd/zeusnet-serial.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable zeusnet-serial
sudo systemctl start zeusnet-serial
```

### Production Deployment

Run the backend without autoreload and adjust the unit file path to your
installation directory (default `/opt/zeusnet`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
docker compose up -d mqtt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
```
