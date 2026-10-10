import os
import json
import psycopg2
from kafka import KafkaConsumer
from groq import Groq
import redis
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

r = redis.Redis(host='redis',port=6379)

cursor.execute("CREATE TABLE IF NOT EXISTS alerts(" \
"id SERIAL PRIMARY KEY," \
"service TEXT," \
"message TEXT," \
"classification TEXT," \
"timestamp TIMESTAMP)")

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

consumer = KafkaConsumer(
    'logs',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    group_id='log-consumer-group',
    api_version=(0, 10, 2)
)

VALID_CLASSIFICATIONS = ("CRITICAL", "WARNING", "NORMAL")

def normalize_classification(reply):
    cleaned = (reply or "").strip().upper().strip(".!")
    if cleaned in VALID_CLASSIFICATIONS:
        return cleaned
    for label in VALID_CLASSIFICATIONS:
        if label in cleaned:
            return label
    print(f"Unexpected classification {reply!r}, defaulting to WARNING")
    return "WARNING"


for msg in consumer:
    try:
        log = json.loads(msg.value.decode('utf-8'))
        log_for_classification = {k: v for k, v in log.items() if k != 'level'}
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"You are a log classifier. Classify the severity of this log into exactly one of these three categories: CRITICAL, WARNING, or NORMAL. Do not use any other words. Do not explain. Reply with one word only.\n\nLog: {json.dumps(log_for_classification)}"
                }
            ],
            model="openai/gpt-oss-120b"
        )
        classification = normalize_classification(chat_completion.choices[0].message.content)
        cursor.execute(
            "INSERT INTO alerts (service,message,classification,timestamp) VALUES (%s,%s,%s,%s)", (log['service'], log['message'], classification, log['timestamp'])
        )
        conn.commit()

        r.publish('alerts',json.dumps({
            'service' : log['service'],
            'message' : log['message'],
            'classification' : classification,
            'timestamp' : log['timestamp']
        }))

        print(f"[{log['service']}] {log['message']} → {classification}")
    except Exception as e:
        conn.rollback()
        print(f"Failed to process message at offset {msg.offset}: {e}")

