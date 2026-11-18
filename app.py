import os, uuid, subprocess, secrets
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import FileResponse

app = FastAPI(title="Dante Studio API", version="0.1.0")
ROOT = Path(os.getenv("DATA_DIR", "data")).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
SADTALKER_DIR = Path(os.getenv("SADTALKER_DIR", "/opt/SadTalker")).resolve()
API_KEY = os.getenv("DANTE_API_KEY")

def authorize(value):
    if not API_KEY or not value or not secrets.compare_digest(value, API_KEY):
        raise HTTPException(401, "API key invalida ou nao configurada")

@app.get("/health")
def health():
    return {"status": "ok", "engine_installed": (SADTALKER_DIR / "inference.py").exists()}

@app.post("/generate")
async def generate(image: UploadFile = File(...), audio: UploadFile = File(...), x_api_key: str | None = Header(default=None)):
    authorize(x_api_key)
    if image.content_type not in {"image/png", "image/jpeg"} or audio.content_type not in {"audio/wav", "audio/mpeg", "audio/mp3"}:
        raise HTTPException(415, "Envie PNG/JPEG e WAV/MP3")
    if not (SADTALKER_DIR / "inference.py").exists():
        raise HTTPException(503, "SadTalker nao instalado")
    job = uuid.uuid4().hex
    work = ROOT / job
    work.mkdir()
    img = work / ("avatar.png" if image.content_type == "image/png" else "avatar.jpg")
    aud = work / ("voice.wav" if audio.content_type == "audio/wav" else "voice.mp3")
    for source, dest in ((image, img), (audio, aud)):
        content = await source.read(25 * 1024 * 1024 + 1)
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(413, "Arquivo excede 25 MB")
        dest.write_bytes(content)
    command = ["python", str(SADTALKER_DIR / "inference.py"), "--driven_audio", str(aud), "--source_image", str(img), "--result_dir", str(work / "results"), "--still", "--preprocess", "crop"]
    try:
        subprocess.run(command, cwd=SADTALKER_DIR, check=True, timeout=1200, capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Geracao excedeu o tempo limite")
    except subprocess.CalledProcessError:
        raise HTTPException(500, "Falha na geracao; consulte os logs do servidor")
    videos = list((work / "results").rglob("*.mp4"))
    if not videos:
        raise HTTPException(500, "Nenhum MP4 gerado")
    output = work / "dante.mp4"
    output.write_bytes(videos[-1].read_bytes())
    return {"job_id": job, "download_path": f"/videos/{job}"}

@app.get("/videos/{job_id}")
def download(job_id: str, x_api_key: str | None = Header(default=None)):
    authorize(x_api_key)
    if len(job_id) != 32 or any(c not in "0123456789abcdef" for c in job_id):
        raise HTTPException(400, "ID invalido")
    path = ROOT / job_id / "dante.mp4"
    if not path.is_file():
        raise HTTPException(404, "Video nao encontrado")
    return FileResponse(path, media_type="video/mp4", filename="dante.mp4")
