docker compose down -v
docker compose up -d
sleep 3 && uv run alembic upgrade head
uv run fastapi dev app/main.py

# product status management
# 