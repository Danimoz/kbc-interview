# Rate-Limited Notification System

A high-performance, scalable notification delivery system built with FastAPI, SQLAlchemy, RabbitMQ, and Redis. This system efficiently processes and delivers email/SMS notifications to users while implementing rate limiting to prevent abuse.

## Features

- **REST API Endpoints**: Well-defined API for sending and tracking notifications
- **Asynchronous Processing**: Queue-based architecture for handling high volume requests
- **Rate Limiting**: Redis-based rate limiting to prevent API abuse
- **Status Tracking**: Real-time status tracking of notification delivery
- **Scalable Workers**: Horizontally scalable worker architecture
- **Containerized Deployment**: Docker-based setup for easy deployment

The system consists of the following components:

- **API Service**: FastAPI application that handles incoming requests
- **Message Queue**: RabbitMQ for asynchronous task processing
- **Rate Limiter**: Redis for implementing rate limiting
- **Database**: PostgreSQL for storing notification data
- **Worker Service**: Processes queued notifications and handles delivery

## API Endpoints

### Send Notification

```
POST /notifications/send
```

Accepts a notification request and places it in a message queue for asynchronous processing.

**Request Body:**

```json
{
  "user_id": "12345",
  "message": "Your order has been shipped!",
  "delivery_type": "email"
}
```

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "Pending",
  "created_at": "2025-02-27T12:34:56.789Z"
}
```

### Get Notification Status

```
GET /notifications/status/{job_id}
```

Retrieves the status of a notification request.

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "Delivered",
  "created_at": "2025-02-27T12:34:56.789Z",
  "updated_at": "2025-02-27T12:35:12.345Z"
}
```

### Get User Notifications

```
GET /notifications/user/{user_id}
```

Fetches the last 10 notifications for a user.

**Response:**

```json
{
  "notifications": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "Delivered",
      "created_at": "2025-02-27T12:34:56.789Z"
    },
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440001",
      "status": "Failed",
      "created_at": "2025-02-27T10:22:33.444Z"
    }
  ]
}
```

## Rate Limiting

The system implements a sliding window rate limit of 10 requests per minute per user. This prevents abuse while allowing legitimate traffic to flow through.

## Installation and Setup

### Prerequisites

- Docker and Docker Compose
- Git

### Getting Started

1. Clone the repository:

```bash
git clone https://github.com/yourusername/rate-limited-notification-system.git
cd rate-limited-notification-system
```

2. Start the services:

```bash
docker-compose up -d
```

3. Initialize the database:

```bash
docker-compose exec api python init.py
```

4. The API will be available at: http://localhost:8000

### Environment Variables

The following environment variables can be configured:

- `DATABASE_URL`: PostgreSQL connection string, it should be async so add asyncpg to it
- `POSTGRES_DB`: Db name
- `POSTGRES_USER`: DB User name
- `POSTGRES_PASSWORD`: Db password
- `REDIS_URL`: Redis connection string
- `REDIS_HOST`:redis
- `REDIS_PORT`:6379
- `REDIS_URL`:redis://localhost:6379/0
- `SECRET_KEY`: generate a secret key
- `HASH_ALGORITHM`: HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`:30
- `CELERY_BROKER_URL`:amqp://guest:guest@localhost:5672//
- `CELERY_RESULT_BACKEND`:redis://localhost:6379/0

## Scaling

To scale the worker service horizontally:

```bash
docker-compose up -d --scale worker=5
```

This will create 5 worker instances to process notifications in parallel.

## Monitoring

- RabbitMQ Management UI: http://localhost:15672 (guest/guest)
- PostgreSQL can be monitored using standard database monitoring tools

## Performance Considerations

- The system is designed to handle high API traffic through rate limiting
- Asynchronous processing ensures the API remains responsive
- Database queries are optimized with proper indexing
- Workers can be scaled based on notification volume

## Security Considerations

- All services run inside Docker containers
- Database credentials are stored as environment variables
- API input is validated using Pydantic models
- Rate limiting helps prevent DoS attacks

## License

[MIT License](LICENSE)

## Contact

For any clarification, contact Michael at projects@kogunababura.com
