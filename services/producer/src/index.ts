import { Kafka } from "kafkajs";

const kafka = new Kafka({
    clientId: 'producer',
    brokers: [process.env.KAFKA_BROKER || 'localhost:29092']
});

const producer = kafka.producer();

await producer.connect();

await producer.send({
    topic: 'logs',
    messages: [
        {
            value: JSON.stringify({
                level: "WARN",
                message: "High memory usage detected: 99%",
                service: "payment-service",
                timestamp: new Date().toISOString()
})
        },
    ],
});

await producer.disconnect();


