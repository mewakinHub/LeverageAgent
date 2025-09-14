from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI(title='Leverage LangGraph API')
class Health(BaseModel):
    status: str
@app.get('/health', response_model=Health)
def health():
    return {'status': 'ok'}
