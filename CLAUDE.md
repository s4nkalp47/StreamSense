# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

StreamSense is a real-time log ingestion, LLM-based classification, and alerting pipeline. Logs flow through Kafka, get classified for severity by an LLM (Groq), land in Postgres, and are fanned out live to a React dashboard over Server-Sent Events backed by Redis pub/sub.

## Architecture (data flow)

```
producer (TS)  -->  Kafka topic "logs"  -->  consumer (Python)  -->  Postgres "alerts" table
services/producer                           services/consumer         + Redis "alerts" channel (publish)
                                                                              |
                                                                              v
                                                                  api (FastAPI, services/api)
                                                                   - GET /alerts, /alerts/{classification}, /stats  (reads Postgres)
                                                                   - GET /stream  (SSE, subscribes to Redis "alerts" channel)
                                                                              |
                                                                              v
                                                                  dashboard (React/Vite, services/dashboard)
                                                                   - StatsChart / AlertTable: fetch() against REST endpoints
                                                                   - LiveFeed: EventSource against /stream (SSE)
```

Each piece is an independently deployable service under `services/`, orchestrated for local dev via the root `docker-compose.yml` (zookeeper, kafka, postgres, redis, producer, consumer, api — the dashboard is run separately, not in compose).

Key behavior to know before touching `consumer.py`:
- It classifies each log by sending it to Groq (`model="openai/gpt-oss-120b"`) asking for exactly one of `CRITICAL`/`WARNING`/`NORMAL`, strips the `level` field before classification, then writes the result to Postgres and publishes the same payload to the Redis `alerts` channel for live streaming.
- The `alerts` table is created with `CREATE TABLE IF NOT EXISTS` at process startup — there are no separate migrations.

`packages/shared` and `infra/docker` currently exist as empty placeholder directories (no code yet).

## Commands

### Infra + backend services (via Docker Compose, from repo root)
```
docker-compose up                 # start zookeeper, kafka, postgres, redis, producer, consumer, api
docker-compose up api consumer    # start a subset
docker-compose up --build         # rebuild images after dependency/Dockerfile changes
```
Requires a root `.env` with `GROQ_API_KEY`, `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (see `.env.example`); `.env` is loaded by both `api` and `consumer` via `env_file` in compose and via `python-dotenv` locally.

### Producer (`services/producer`, TypeScript/kafkajs)
```
npm install
npm run dev     # tsx watch src/index.ts — sends one sample log to the "logs" topic then exits
npm run build    # tsc -> dist/
npm start        # node dist/index.js
```
`src/test_logs.ts` is a manual script for pushing a few varied sample logs to Kafka; run it directly with `tsx src/test_logs.ts` (not wired to an npm script).

### Consumer (`services/consumer`, Python)
Run via the `consumer` Docker service, or locally with the venv in `services/consumer/.venv`:
```
pip install -r requirements.txt
python consumer.py
```
Connects to Kafka at `kafka:9092` and Redis at host `redis` — these hostnames only resolve inside the Compose network, so running it outside Docker requires overriding those connections.

### API (`services/api`, FastAPI)
```
pip install -r requirements.txt
uvicorn main:app --reload
```
Serves on `:8000`. Also expects Postgres/Redis reachable at the hostnames above.

### Dashboard (`services/dashboard`, React + Vite)
```
npm install
npm run dev       # Vite dev server
npm run build
npm run lint      # eslint .
npm run preview
```
Talks to the API directly at `http://localhost:8000` (hardcoded in the three components under `src/components/`), so the API must be running on that port for the dashboard to show data.

## Notes

- There is no automated test suite in this repo yet.
- Python dependency files (`services/api/requirements.txt`, `services/consumer/requirements.txt`) are UTF-16 encoded — edit them with a tool that preserves that encoding, or re-save as UTF-8 if normalizing.
