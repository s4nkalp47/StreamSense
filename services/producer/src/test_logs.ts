import { Kafka } from "kafkajs";

const kafka = new Kafka({
    clientId: 'producer',
    brokers: ['localhost:9092'],
});

const test_producer = kafka.producer();

await test_producer.connect();

await test_producer.send({
    topic: 'logs',
    messages: [
        {
            value: JSON.stringify({
                message: "Payment service is down, transactions failing",
                service: "payment-service",
                timestamp: new Date().toISOString()
            }),
        },
        {       value: JSON.stringify({
                    message: "Response time increased to 2000ms, approaching timeout threshold",
                    service: "api-gateway",
                    timestamp: new Date().toISOString()
                }),
        },
        {
            value: JSON.stringify({
                message: "User authentication successful",
                service: "auth-service",
                timestamp: new Date().toISOString()
            })
        }
    ],
});

await test_producer.disconnect();
