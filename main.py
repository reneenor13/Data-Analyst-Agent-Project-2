from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import shutil
from model import handle_query

app = FastAPI()

@app.post("/api/")
async def analyze_data(
    questions: UploadFile = File(...),
    files: Optional[List[UploadFile]] = File(None)
):
    temp_dir = tempfile.mkdtemp()

    # Save files locally
    file_paths = {}
    for f in files or []:
        temp_path = f"{temp_dir}/{f.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        file_paths[f.filename] = temp_path

    # Save questions.txt
    question_path = f"{temp_dir}/questions.txt"
    with open(question_path, "wb") as qf:
        shutil.copyfileobj(questions.file, qf)

    # Run processing
    result = handle_query(question_path, file_paths)
    return JSONResponse(content=result)
