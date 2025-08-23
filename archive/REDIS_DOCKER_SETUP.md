# Redis Docker Setup for RMS

## 🐳 Docker Redis Configuration

This project uses Docker for Redis caching with the following setup:

### Quick Start
```bash
# Start Redis container
docker-compose up -d redis

# Check Redis status
docker exec rms-redis redis-cli ping

# View Redis logs
docker logs rms-redis

# Stop Redis
docker-compose down redis
```

### Services

#### Redis (Port 6379)
- **Image**: `redis:7-alpine`
- **Container**: `rms-redis` 
- **Port**: `6379:6379`
- **Persistence**: Volume mounted for data persistence
- **Configuration**: Append-only file enabled for durability

#### Redis Commander (Port 8081) - Optional
- **Image**: `rediscommander/redis-commander:latest`
- **Container**: `rms-redis-commander`
- **Port**: `8081:8081`
- **Purpose**: Web-based Redis GUI management tool
- **Access**: http://localhost:8081

### Redis Commands
```bash
# Connect to Redis CLI
docker exec -it rms-redis redis-cli

# View all keys
docker exec rms-redis redis-cli KEYS "*"

# Check database size
docker exec rms-redis redis-cli DBSIZE

# Monitor Redis commands in real-time
docker exec rms-redis redis-cli MONITOR

# Flush all data (development only!)
docker exec rms-redis redis-cli FLUSHALL
```

### Environment Configuration

The application automatically connects to Redis at `redis://localhost:6379/0`.

**Environment Variables:**
- `REDIS_ENABLED=true` (default)
- `REDIS_URL=redis://localhost:6379/0` (default)
- `REDIS_TTL_DEFAULT=300` (5 minutes default TTL)
- `REDIS_TTL_AVAILABILITY=60` (1 minute for availability data)
- `REDIS_TTL_TABLES=600` (10 minutes for table data)
- `REDIS_TTL_RESERVATIONS=300` (5 minutes for reservations)
- `REDIS_TTL_RESTAURANT_INFO=1800` (30 minutes for restaurant info)

### Cache Keys Pattern
- `tables:*` - Table data and operations
- `availability:*` - Availability queries and calendars  
- `reservations:*` - Reservation data and queries
- `waitlist:*` - Waitlist entries and analytics
- `public_availability:*` - Public customer availability queries
- `public_restaurant_info:*` - Public restaurant information

### Data Persistence
- Redis data is persisted in Docker volume `rms_redis_data`
- Append-only file (AOF) enabled for crash recovery
- Data survives container restarts and updates

### Development Tips
- Use Redis Commander (http://localhost:8081) for visual cache inspection
- Monitor cache hit/miss rates during development
- Clear cache during development: `docker exec rms-redis redis-cli FLUSHALL`
- Check cache keys: `docker exec rms-redis redis-cli KEYS "*"`

### Production Considerations
- Configure Redis password authentication
- Set up Redis cluster for high availability
- Monitor memory usage and configure eviction policies
- Enable Redis persistence backup strategies
- Configure proper network security
