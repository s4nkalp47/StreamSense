import os
import json
import psycopg2
from kafka import KafkaConsumer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

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

for msg in consumer:
    log = json.loads(msg.value.decode('utf-8'))
    log_for_classification = {k: v for k, v in log.items() if k != 'level'}
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You are a log classifier. Classify the severity of this log into exactly one of these three categories: CRITICAL, WARNING, or NORMAL. Do not use any other words. Do not explain. Reply with one word only.\n\nLog: {json.dumps(log_for_classification)}"
            }
        ],
        model="llama-3.1-8b-instant"
    )
    classification = chat_completion.choices[0].message.content
    cursor.execute(
        "INSERT INTO alerts (service,message,classification,timestamp) VALUES (%s,%s,%s,%s)", (log['service'], log['message'], classification, log['timestamp'])
    )
    conn.commit()
    print(f"[{log['service']}] {log['message']} → {classification}")

