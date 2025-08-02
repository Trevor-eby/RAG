from fastapi import FastAPI, Request, UploadFile, File, status
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.query_data import query_rag
from backend.file_processing import process_and_add_file_to_db
import os
import shutil
import traceback

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

@app.post("/ask")
def ask_question(request: QueryRequest):
    response = query_rag(request.query_text)
    return {"response": response}

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    print(f"Received file upload: {file.filename}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    await file.close()

    print(f"File saved to {file_path}")

    try:
        new_chunks_added = process_and_add_file_to_db(file_path)
        print(f"Processing result: {new_chunks_added}")

        if new_chunks_added:
            return {"message": f"{file.filename} uploaded and processed successfully with new chunks."}
        else:
            return {"message": f"{file.filename} uploaded, but no new chunks to add."}
    except Exception as e:
        print(f"Error processing file: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
