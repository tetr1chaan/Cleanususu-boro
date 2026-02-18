from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import uvicorn
import shutil
import os

app = FastAPI()

# Папки
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# База данных (Создаем таблицу, если нет)
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lat REAL,
        lon REAL,
        description TEXT,
        photo_path TEXT,
        status TEXT DEFAULT 'new'
    )
""")
conn.commit()

# Главная страница (Карта для юзера)
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Прием заявки (Сохраняем фото и координаты)
@app.post("/submit")
async def submit_report(lat: float = Form(...), lon: float = Form(...), desc: str = Form(...), photo: UploadFile = Form(...)):
    file_location = f"static/uploads/{photo.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(photo.file, file_object)
    
    cursor.execute("INSERT INTO reports (lat, lon, description, photo_path) VALUES (?, ?, ?, ?)", (lat, lon, desc, file_location))
    conn.commit()
    return {"message": "Заявка принята! Рахмет за чистоту!"}

# Админка (Отдаем список мусора)
@app.get("/api/reports")
def get_reports():
    cursor.execute("SELECT id, lat, lon, description, photo_path, status FROM reports")
    data = cursor.fetchall()
    # Превращаем в JSON
    return [{"id": r[0], "lat": r[1], "lon": r[2], "desc": r[3], "photo": r[4], "status": r[5]} for r in data]

@app.post("/api/reports/{report_id}/clean")
def mark_as_cleaned(report_id: int):
    cursor.execute("UPDATE reports SET status = 'cleaned' WHERE id = ?", (report_id,))
    conn.commit()
    return{"message": "Успешно убрано!"}
@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)