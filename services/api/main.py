import os
import psycopg2
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()


conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cursor = conn.cursor()

app = FastAPI()


@app.get("/alerts")
def get_alerts():
    cursor.execute("SELECT id, service, message, classification, timestamp FROM alerts")
    rows = cursor.fetchall()
    alerts = [
        {
            "id": row[0],
            "service": row[1],
            "message": row[2],
            "classification": row[3],
            "timestamp": row[4]
        }
        for row in rows
    ]
    return {"alerts": alerts}

@app.get("/alerts/{classification}")
def getAlertsByClass(classification: str):
    cursor.execute("SELECT id,service,message,timestamp FROM alerts WHERE classification = %s",(classification,))
    rows = cursor.fetchall()
    alerts = [
        {
         "id": row[0],
         "service": row[1],
         "message": row[2],
         "timestamp": row[3]   
        }
        for row in rows
    ]
    return {"alerts": alerts}

@app.get("/stats")
def get_stats():
    cursor.execute("SELECT classification, COUNT(*) FROM alerts GROUP BY classification")
    rows = cursor.fetchall()
    stats = [
        {
        "classification": row[0],
        "count": row[1]
        }
        for row in rows
    ]
    return {"stats": stats}
