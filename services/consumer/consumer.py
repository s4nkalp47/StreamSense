from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'logs',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='log-consumer-group',
    api_version=(0, 10, 2)
)

for msg in consumer:
    print(msg.value)