from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess, tempfile
from pathlib import Path
import os

app = FastAPI(title="Leverage LangGraph API", version="0.1.0")
# app = FastAPI()

@app.get('/health')
def health():
    return {
        'ok': True,
        's3_endpoint': os.getenv('S3_ENDPOINT',''),
        'bucket': os.getenv('S3_BUCKET',''),
        'qdrant_url': os.getenv('QDRANT_URL',''),
    }

class YTReq(BaseModel):
    url: str                        # YouTube URL
    langs: str = "th"               # language(s) to request (e.g., "th,en")
    auto: bool = True               # auto-subs vs creator subs
    cookies_txt: str | None = None  # optional: for private/members-only videos

def _run(cmd: list[str], cwd: str | None = None):
    # running subprocess with pipes, text mode to process cmd list as command and args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    # (pause) wait for process to complete and get output and error
    out, err = p.communicate()
    return p.returncode, out, err

def _srt_to_text(srt: str) -> str:
    lines = []
    for line in srt.splitlines():
        l = line.strip()
        if not l or l.isdigit() or "-->" in l:
            continue
        lines.append(l)
    return "\n".join(lines)

@app.post("/yt/subtitles")
def yt_subtitles(req: YTReq):
    with tempfile.TemporaryDirectory() as tmp:  # auto-cleaned temp dir
        cookies_path = None
        if req.cookies_txt:                     # write cookies as file inside if provided
            cookies_path = Path(tmp) / "cookies.txt"
            cookies_path.write_text(req.cookies_txt, encoding="utf-8")
        
        outtmpl = "%(id)s.%(ext)s"        # file lands in cwd (the tmp dir)

        cmd = [
            "yt-dlp",
            "--skip-download",
            "--sub-format", "srt",
            "--convert-subs", "srt",
            "--sub-langs", req.langs,
            "-o", outtmpl,                # <— write into cwd
        ]
        cmd += ["--write-auto-subs"] if req.auto else ["--write-subs"]
        if cookies_path:
            cmd += ["--cookies", str(cookies_path)]
        cmd += [req.url]
        code, out, err = _run(cmd, cwd=tmp)
        # logger.debug(out) or err for debugging, but mainly we want just integer exit `code` to check success
        # yt-dlp writes subtitles to current dir, so we set temp dir as cwd to run command there

        # pick any .srt produced inside temp dir as list of Path
        srt_files = list(Path(tmp).glob("*.srt"))
        if code != 0 or not srt_files:
            raise HTTPException(status_code=404, detail=f"No subtitles found. {err[-300:]}")

        # read first .srt file found and convert to plain text (future: change, if needed, to handle multiple files)
        text = _srt_to_text(srt_files[0].read_text(encoding="utf-8"))
        return {"ok": True, "text": text}
