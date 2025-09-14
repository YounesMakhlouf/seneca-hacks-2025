# 🔧 Feedback Worker

Async feedback processor for the Body-to-Behavior Recommender system.

## Overview

This worker processes user feedback messages asynchronously using Kafka, implementing the **complete and identical business logic** as the backend's synchronous endpoint but in a separate, scalable service. No logic has been simplified or changed - this is a full, independent implementation.

## Key Features

- **Complete Backend Logic**: Full implementation of user state computation, contextual bandits, and preference updates
- **Independent Operation**: Designed to run as a separate container with its own database access
- **Identical Business Logic**: No simplifications - exact same algorithms as the main backend
- **Kafka Integration**: Consumes feedback messages for async processing
- **MongoDB Integration**: Direct database access for user data and state computation

## Architecture

```
Kafka Topic (feedback) → Worker → MongoDB
                           ↓
                    Contextual Bandits + 
                    Preference Updates
```

## State Computation

The worker implements the complete state computation logic from the backend:

- **Readiness**: Sleep-based recovery (duration, efficiency, bedtime consistency, recovery factor)
- **Fuel**: Nutritional status (protein targets, fiber, sugar/sodium penalties)  
- **Strain**: Activity load (steps z-score, heart rate, active minutes normalized)

## Machine Learning

- **Thompson Sampling**: Contextual multi-armed bandits using MABWiser
- **3D Context Vector**: [Readiness/100, Fuel/100, Strain/100]
- **Dynamic Arms**: Music (lofi_low, synth_mid, pop_up), Meals (shake, bowl, wrap), Workouts (z2_walk, z2_cycle, tempo_intervals, mobility)

## Dependencies

- `kafka-python`: Kafka message consumption
- `pymongo`: MongoDB database access
- `mabwiser`: Contextual bandit algorithms
- `numpy`: Mathematical computations
- `pydantic`: Data validation and parsing

## Usage

```bash
# Build and run with Docker
docker build -t feedback-worker .
docker run -e MONGODB_URI="..." -e BBR_DB_NAME="bbr" feedback-worker

# Or run directly
cd worker
uv run python -m src.feedback_worker.main
```

## Testing

```bash
# Run the test script
cd worker
python test_worker.py
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string
- `BBR_DB_NAME`: Database name (default: "bbr")
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka servers (default: "kafka:9092")
- `KAFKA_TOPIC`: Feedback topic (default: "feedback")
- `KAFKA_GROUP_ID`: Consumer group (default: "feedback-worker")
Mobile App → API Server → Kafka → Feedback Worker → MongoDB
```

## Features

- **Async Processing**: Non-blocking feedback processing
- **Kafka Integration**: Reliable message consumption
- **Same Logic**: Identical processing logic as sync endpoint
- **Error Handling**: Retry logic and dead letter queues
- **Monitoring**: Comprehensive logging and metrics

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `MONGODB_URI`: MongoDB connection string
- `WORKER_POLL_TIMEOUT`: Kafka polling timeout
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## Running

```bash
# With Docker Compose
make up

# Standalone (for development)
uv run python -m src.feedback_worker.main
```