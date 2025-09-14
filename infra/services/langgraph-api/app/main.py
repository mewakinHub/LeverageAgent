from fastapi import FastAPI
import os

app = FastAPI(title="Leverage LangGraph API", version="0.1.0")

@app.get('/health')
def health():
    return {
        'ok': True,
        's3_endpoint': os.getenv('S3_ENDPOINT',''),
        'bucket': os.getenv('S3_BUCKET',''),
        'qdrant_url': os.getenv('QDRANT_URL',''),
    }
