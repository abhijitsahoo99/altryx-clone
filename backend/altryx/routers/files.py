import shutil

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from altryx.config import UPLOAD_DIR
from altryx.database import get_db
from altryx.models import UploadedFile
from altryx.models import gen_id
from altryx.schemas import FileResponse

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload", response_model=FileResponse, status_code=201)
async def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx", "xls", "json"):
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    file_id = gen_id()
    stored_name = f"{file_id}_{file.filename}"
    dest = UPLOAD_DIR / stored_name

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    size = dest.stat().st_size

    record = UploadedFile(
        id=file_id,
        filename=stored_name,
        original_name=file.filename,
        file_format=ext,
        size_bytes=size,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return FileResponse.model_validate(record)


@router.get("", response_model=list[FileResponse])
def list_files(db: Session = Depends(get_db)):
    files = db.query(UploadedFile).order_by(UploadedFile.created_at.desc()).all()
    return [FileResponse.model_validate(f) for f in files]


@router.get("/{file_id}/preview")
def preview_file(file_id: str, rows: int = 50, db: Session = Depends(get_db)):
    record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    path = UPLOAD_DIR / record.filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing from disk")

    fmt = record.file_format
    if fmt == "csv":
        df = pd.read_csv(path, nrows=rows)
    elif fmt in ("xlsx", "xls"):
        df = pd.read_excel(path, nrows=rows)
    elif fmt == "json":
        df = pd.read_json(path)
        df = df.head(rows)
    else:
        raise HTTPException(status_code=400, detail=f"Cannot preview format: {fmt}")

    return {
        "columns": list(df.columns),
        "row_count": len(df),
        "data": df.fillna("").to_dict(orient="records"),
    }


@router.delete("/{file_id}", status_code=204)
def delete_file(file_id: str, db: Session = Depends(get_db)):
    record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    path = UPLOAD_DIR / record.filename
    if path.exists():
        path.unlink()

    db.delete(record)
    db.commit()
