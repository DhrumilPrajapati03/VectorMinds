from fastapi import FastAPI

from routes import analyze, upload, voice

app = FastAPI(title="Lexo API")

app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(voice.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
