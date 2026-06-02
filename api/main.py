from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, dialogs, knowledge

app = FastAPI(title="Expert Bot Admin API", version="1.0.0")

# CORS для React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роуты
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dialogs.router, prefix="/api/dialogs", tags=["dialogs"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])

@app.get("/")
def root():
    return {"message": "Expert Bot Admin API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}
