from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List
from pydantic import BaseModel
import shutil
import logging
import zipfile
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler
from utils.image_processing.generate import generate_images
from utils.image_processing.process import process_images

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clear_directories():
    processed_dir = "static/processed"
    uploads_dir = "static/uploads"

    if os.path.exists(processed_dir):
        shutil.rmtree(processed_dir)
        os.makedirs(processed_dir)

    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir)
        os.makedirs(uploads_dir) 

scheduler = BackgroundScheduler()
scheduler.add_job(clear_directories, 'cron', hour=0, minute=0)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()  

app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)

def get_session_directory(user_id: str, session_id: str, folder_type: str = "uploads") -> Path:
    """사용자 및 세션별 디렉토리를 반환합니다."""
    directory = Path(f"static/{folder_type}/{user_id}/{session_id}")
    directory.mkdir(parents=True, exist_ok=True)
    return directory

class TranslationResponse(BaseModel):
    translations: List[str]

@app.post("/upload/{user_id}/{session_id}")
async def upload_image(user_id: str, session_id: str, image: UploadFile = File(...)):
    try:
        logging.info(f"Uploading image for user: {user_id}, session: {session_id}")
        session_dir = get_session_directory(user_id, session_id, "uploads")
        image_path = session_dir / image.filename
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        logging.info(f"Image uploaded successfully at {image_path}")
        return {"message": "Image uploaded successfully", "file_path": str(image_path)}
    except Exception as e:
        logging.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed.")

@app.post("/process/{user_id}/{session_id}", response_model=TranslationResponse)
async def process_images_route(user_id: str, session_id: str):
    upload_dir = get_session_directory(user_id, session_id, "uploads")
    processed_dir = get_session_directory(user_id, session_id, "processed")
    processed_texts = []

    for image_file in upload_dir.iterdir():
        translated_text = f"Translated text for {image_file.stem}"
        # TODO:
        # translated_text = await generate_images()
        processed_texts.append(translated_text)

    logging.info(f"Processed images for user: {user_id}, session: {session_id}")
    return {"translations": processed_texts}

@app.post("/generate-images/{user_id}/{session_id}")
async def generate_images(user_id: str, session_id: str, translations: TranslationResponse):
    upload_dir = get_session_directory(user_id, session_id, "uploads")
    processed_dir = get_session_directory(user_id, session_id, "processed")
    
    for image_file in upload_dir.iterdir():
        new_filename = processed_dir / f"processed_{image_file.name}"
        # TODO:
        # generate_images()
        shutil.copy(image_file, new_filename)
    generated_files = [f"/static/processed/{user_id}/{session_id}/{file.name}" for file in processed_dir.iterdir()]
    return {"message": "Images generated successfully!", "generated_files": generated_files}

# 특정 세션의 파일을 ZIP으로 압축하는 함수
def create_zip_file(user_id: str, session_id: str) -> str:
    session_dir = get_session_directory(user_id, session_id, "processed")
    zip_filename = f"images.zip"
    zip_path = session_dir.parent / zip_filename  # 사용자 UUID 디렉토리에 ZIP 파일 저장

    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for file_path in session_dir.iterdir():
            if file_path.is_file():
                zip_file.write(file_path, arcname=file_path.name)
    return zip_path

# ZIP 파일 다운로드 엔드포인트
@app.get("/download/{user_id}/{session_id}")
async def download_zip(user_id: str, session_id: str):
    try:
        zip_path = create_zip_file(user_id, session_id)
        if not zip_path.exists():
            logging.error("ZIP file not found.")
            raise HTTPException(status_code=404, detail="ZIP file not found.")
        return FileResponse(path=zip_path, filename=f"images.zip", media_type="application/zip")
    except Exception as e:
        logging.error(f"Error serving ZIP file: {e}")
        raise HTTPException(status_code=500, detail="Could not create ZIP file.")