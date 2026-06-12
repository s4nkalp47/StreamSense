import { Kafka } from "kafkajs";

const kafka = new Kafka({
    clientId: 'producer',
    brokers: ['localhost:9092'],
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


