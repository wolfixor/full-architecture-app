#!/bin/bash
set -e

echo "Waiting for database to be ready..."

max_retries=30
counter=0

until PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h "$POSTGRES_HOST" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -c '\q' 2>/dev/null; do

    counter=$((counter + 1))

    if [ $counter -gt $max_retries ]; then
        echo "❌ Failed to connect to database after $max_retries attempts"
        exit 1
    fi

    echo "⏳ Waiting for postgres... ($counter/$max_retries) POSTGRES_HOST:($POSTGRES_HOST) POSTGRES_USER:($POSTGRES_USER) POSTGRES_DB:($POSTGRES_DB) POSTGRES_PASSWORD:($POSTGRES_PASSWORD)"
    sleep 2
done

echo "✅ Database is ready!"

echo "Waiting for Redis to be ready..."

counter=0
until redis-cli -h $REDIS_HOST -p $REDIS_PORT ping 2>/dev/null | grep -q PONG; do
    counter=$((counter + 1))

    if [ $counter -gt $max_retries ]; then
        echo "⚠️ Failed to connect to Redis after $max_retries attempts (continuing anyway)"
        break
    fi

    echo "⏳ Waiting for Redis... ($counter/$max_retries)"
    sleep 2
done

echo "✅ Redis is ready! (or at least attempted)"

echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Migrations completed successfully!"

echo "🚀 Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000