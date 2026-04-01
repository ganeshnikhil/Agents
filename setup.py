import subprocess
import time
import socket
import os
import sys


QDRANT_CONTAINER = "qdrant"
QDRANT_HTTP_PORT = 6335
FASTAPI_PORT = 8000


def run_cmd(cmd):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
def run_cmd(cmd, check=False):
    """Run a shell command and return CompletedProcess."""
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=isinstance(cmd, str),
        check=check
    )


# ---------------- Docker ----------------

def is_docker_running():
    return run_cmd(["docker", "info"]).returncode == 0


def start_docker():
    print("🚀 Starting Docker...")
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Docker"])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["sudo", "systemctl", "start", "docker"])
    elif sys.platform == "win32":
        subprocess.Popen(["powershell", "Start-Process", "Docker Desktop"])

    for _ in range(30):
        if is_docker_running():
            print("✅ Docker is running")
            return
        time.sleep(2)

    raise RuntimeError("Docker failed to start")


# ---------------- Network ----------------

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


# ---------------- Qdrant ----------------

def container_exists():
    return QDRANT_CONTAINER in run_cmd(
        ["docker", "ps", "-a", "--format", "{{.Names}}"]
    ).stdout.splitlines()


def container_running():
    return QDRANT_CONTAINER in run_cmd(
        ["docker", "ps", "--format", "{{.Names}}"]
    ).stdout.splitlines()


def start_qdrant():
    if container_running():
        print("✅ Qdrant already running")
        return

    if container_exists():
        print("▶️ Starting existing Qdrant container")
        run_cmd(["docker", "start", QDRANT_CONTAINER])
    else:
        print("📦 Creating Qdrant container")
        run_cmd([
            "docker", "run", "-d",
            "--name", QDRANT_CONTAINER,
            "-p", "6335:6333",
            "-p", "6336:6334",
            "-v", f"{os.getcwd()}/qdrant_storage:/qdrant/storage",
            "qdrant/qdrant"
        ])

    for _ in range(20):
        if is_port_open(QDRANT_HTTP_PORT):
            print("✅ Qdrant ready")
            return
        time.sleep(1)

    raise RuntimeError("Qdrant failed to start")


# ---------------- FastAPI ----------------

def start_fastapi():
    if is_port_open(FASTAPI_PORT):
        print("✅ FastAPI already running")
        return

    print("🚀 Starting FastAPI (uvicorn)...")

    subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.app.main:app",
            "--host", "127.0.0.1",
            "--port", str(FASTAPI_PORT),
        ],
        stdout=sys.stdout,   # 👈 SHOW LOGS
        stderr=sys.stderr,   # 👈 SHOW ERRORS
    )

    for _ in range(30):
        if is_port_open(FASTAPI_PORT):
            print("✅ FastAPI ready")
            return
        time.sleep(1)

    raise RuntimeError("FastAPI failed to start")


# ---------------- Ollama ----------------

def is_ollama_installed():
    """Check if Ollama CLI is installed."""
    return run_cmd(["which", "ollama"]).returncode == 0


def is_ollama_running():
    """Check if Ollama CLI is functional by running `ollama list`."""
    return run_cmd(["ollama", "list"]).returncode == 0


def install_ollama():
    """Install Ollama and pull essential models."""
    print("📥 Installing Ollama...")

    if sys.platform == "darwin":
        run_cmd(["brew", "install", "ollama"], check=True)
    elif sys.platform.startswith("linux"):
        run_cmd("curl -fsSL https://ollama.com/install.sh | sh", check=True, shell=True)
    else:
        raise RuntimeError("Automatic Ollama installation only supported on macOS/Linux in this script.")

    # Pull models
    models = [
        "gemma3:4b",
        "qwen3:4b",
        "nomic-embed-text:latest"
    ]

    for model in models:
        print(f"📦 Pulling Ollama model: {model}")
        run_cmd(["ollama", "pull", model], check=True)

    # Show available models
    run_cmd(["ollama", "list"], check=True)


def setup_ollama():
    """Ensure Ollama is installed and functional."""
    if not is_ollama_installed():
        install_ollama()
    else:
        print("✅ Ollama CLI already installed")

    if not is_ollama_running():
        raise RuntimeError("Ollama CLI is installed but not working. Please check installation.")
    else:
        print("✅ Ollama CLI is functional and ready")


# ---------------- Model Setup ----------------

from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "cythonboy/multi-task-emotion-model"
MODEL_PATH = "data/Models/multi_task_model_with_emotion"


def setup_model():
    """Download model only if not present locally."""
    if os.path.exists(MODEL_PATH) and os.listdir(MODEL_PATH):
        print("✅ Model already exists locally. Skipping download.")
        return

    print("⬇️ Downloading model from Hugging Face...")

    os.makedirs(MODEL_PATH, exist_ok=True)

    AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=MODEL_PATH
    )

    AutoModel.from_pretrained(
        MODEL_NAME,
        cache_dir=MODEL_PATH
    )

    print("✅ Model downloaded and cached")
    
    
# ---------------- Bootstrap ----------------

def bootstrap():
    if not is_docker_running():
        start_docker()

    start_qdrant()

    setup_model()   # 👈 ADD HERE (before FastAPI)

    start_fastapi()

    setup_ollama()
