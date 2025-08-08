import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.get_embedding_function import get_embedding_function
from backend.query_data import query_rag
from backend.file_processing import process_and_add_file_to_db
import os
import shutil
import uvicorn

# Load environment variables from .env
load_dotenv()


app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query_text: str

# Load embedding function once at startup
try:
    embed_text = get_embedding_function()
except Exception as e:
    raise RuntimeError(f"Failed to initialize embedding function: {e}")

#Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

#Home page
@app.get("/")
def read_index():
    return FileResponse("frontend/webfront.html")

@app.post("/ask")
async def ask_question(req: QueryRequest):
    question = req.query_text.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        answer = query_rag(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    await file.close()

    try:
        new_chunks_added = process_and_add_file_to_db(file_path)

        if new_chunks_added:
            return {"message": f"{file.filename} uploaded and processed successfully with new chunks."}
        else:
            return {"message": f"{file.filename} uploaded, but no new chunks to add."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    print(f"🔥 Internal Server Error:\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8080)
