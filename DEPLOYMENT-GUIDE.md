# HEIR Platform Deployment Guide
**Complete guide for deploying HEIR platform to any application (new or existing)**

## Overview
The HEIR platform provides a secure, doctrine-enforced foundation for AI agent systems. This guide will help you deploy the platform in any environment and integrate it with your applications.

## Prerequisites

### Required
- PostgreSQL 12+ (local, cloud, or managed service like Neon)
- Node.js 16+ (for setup scripts)
- Git (for repository management)

### Optional (but recommended)
- Docker (for containerized deployment)
- Redis (for enhanced rate limiting)
- Monitoring system (Prometheus, DataDog, etc.)

## Quick Start (5 Minutes)

### 1. Clone and Initialize
```bash
git clone https://github.com/djb258/HEIR-AGENT-SYSTEM.git
cd HEIR-AGENT-SYSTEM
```

### 2. Set Environment Variables
```bash
# Required: Your database connection string
export DATABASE_URL="postgresql://username:password@host:port/database"

# Optional: For enhanced features
export HEIR_MONITORING_ENDPOINT="https://your-monitoring-service.com/webhook"
```

### 3. Deploy Database Schema
```bash
# Deploy the complete HEIR schema
bash scripts/deploy-database.sh
```

### 4. Initialize Platform
```bash
# Set up platform configuration
node heir-drop-in.js
```

### 5. Verify Installation
The deployment script will confirm:
- ✅ Database schema deployed successfully
- ✅ All critical tables exist and accessible
- ✅ ORBT system functional
- ✅ Platform ready for application integration

## Integration Options

### Option A: New Application
```bash
# 1. Fill out configuration template
cp heir-project-config.json my-app-config.json
# Edit my-app-config.json with your requirements

# 2. Your application code integrates via:
# - Database writes through Database Gatekeeper
# - API calls through API Gateway
# - Required doctrine headers on all mutations
```

### Option B: Existing Application
```bash
# 1. Install HEIR alongside existing database
# (HEIR uses 'shq' schema - no conflicts with your app schema)

# 2. Gradually migrate writes to use doctrine headers:
const headers = {
  unique_id: "APP.01.PROC.DB.10000.001",
  process_id: "UpdateUser", 
  blueprint_id: "my-existing-app",
  agent_signature: "my-app:20250113153201:abc123"
};

# 3. Route writes through HEIR validation
```

## Environment-Specific Deployment

### Development
```bash
# Local PostgreSQL
export DATABASE_URL="postgresql://localhost:5432/heir_dev"
export PLATFORM_ENV="development"
export LOG_LEVEL="debug"

bash scripts/deploy-database.sh
node heir-drop-in.js
```

### Staging
```bash
# Cloud database (e.g., Neon)
export DATABASE_URL="postgresql://user:pass@cloud-db.com:5432/heir_staging"
export PLATFORM_ENV="staging"
export LOG_LEVEL="info"

bash scripts/deploy-database.sh
node heir-drop-in.js
```

### Production
```bash
# Production database with full security
export DATABASE_URL="postgresql://user:pass@prod-db.com:5432/heir_prod"
export PLATFORM_ENV="production"
export LOG_LEVEL="warn"
export TLS_REQUIRED="true"
export AUDIT_RETENTION_DAYS="365"

bash scripts/deploy-database.sh
node heir-drop-in.js
```

## Docker Deployment

### Single Container
```dockerfile
FROM node:18-alpine
COPY . /app
WORKDIR /app
RUN npm install
EXPOSE 3000
CMD ["node", "heir-drop-in.js"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  heir-platform:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/heir
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=heir
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Application Integration

### Required Doctrine Headers
All mutating operations MUST include:
```javascript
const doctrineHeaders = {
  unique_id: "[DB].[SUBHIVE].[MICROPROCESS].[TOOL].[ALTITUDE].[STEP]",
  process_id: "VerbObject", // e.g., "ProcessPayment", "UpdateUser"
  blueprint_id: "your-app-identifier", 
  agent_signature: "agent-id:timestamp:hash"
};
```

### Database Integration
```javascript
// Instead of direct database writes:
// await db.query('INSERT INTO users ...', data);

// Route through Database Gatekeeper:
const result = await heirPlatform.databaseGatekeeper.validateAndWrite({
  operation: {
    type: 'write',
    table: 'users',
    data: userData
  },
  headers: doctrineHeaders
});
```

### API Integration  
```javascript
// Instead of direct external API calls:
// await fetch('https://api.external.com/data');

// Route through API Gateway:
const result = await heirPlatform.apiGateway.routeRequest({
  api_request: {
    method: 'POST',
    url: 'https://api.external.com/data',
    payload: requestData
  },
  heir_headers: doctrineHeaders
});
```

## Configuration Examples

### Basic Application Config
```json
{
  "project_name": "my-application",
  "project_description": "My awesome application with HEIR platform",
  "project_type": "web-application",
  
  "heir_integration": {
    "database_gatekeeper_enabled": true,
    "api_gateway_enabled": true,
    "doctrine_enforcement": "strict"
  },
  
  "security": {
    "auth_required": true,
    "rate_limiting": true,
    "audit_logging": true
  }
}
```

### E-commerce Application Config  
```json
{
  "project_name": "ecommerce-platform",
  "project_description": "Online store with payment processing",
  "project_type": "ecommerce",
  
  "heir_integration": {
    "database_gatekeeper_enabled": true,
    "api_gateway_enabled": true,
    "doctrine_enforcement": "strict"
  },
  
  "required_capabilities": [
    "user_management",
    "product_catalog", 
    "payment_processing",
    "order_management"
  ],
  
  "external_integrations": [
    "stripe_payments",
    "email_service",
    "analytics_tracking"
  ]
}
```

## Testing Your Deployment

### Run Platform Tests
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires DATABASE_URL)
export TEST_DATABASE_URL="postgresql://localhost:5432/heir_test"
pytest tests/unit/ -m integration -v
```

### Validate Doctrine Enforcement
```bash
# Test that mutations without headers are rejected
curl -X POST http://localhost:3000/api/data \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' 
# Should return 400 with MISSING_HEADERS error

# Test that mutations with valid headers succeed
curl -X POST http://localhost:3000/api/data \
  -H "Content-Type: application/json" \
  -H "unique_id: TEST.01.PROC.API.10000.001" \
  -H "process_id: TestWrite" \
  -H "blueprint_id: test-app" \
  -H "agent_signature: test:20250113153201:abc123" \
  -d '{"test": "data"}'
# Should return 200 with success response
```

## Troubleshooting

### Common Issues

**"Database connection failed"**
```bash
# Verify DATABASE_URL is correct
echo $DATABASE_URL
# Test connection manually
psql $DATABASE_URL -c "SELECT version();"
```

**"Schema deployment failed"**  
```bash
# Check if database exists and is accessible
# Verify user has CREATE privileges
# Check logs in scripts/deploy-database.sh output
```

**"Doctrine header validation failed"**
```bash
# Ensure all 4 headers are present and properly formatted
# Check unique_id follows pattern: [DB].[SUBHIVE].[MICROPROCESS].[TOOL].[ALTITUDE].[STEP]
# Verify process_id uses VerbObject format
```

**"Permission denied errors"**
```bash
# Make scripts executable
chmod +x scripts/*.sh
# Verify database user has required permissions
```

### Getting Help

1. **Check the logs**: All scripts provide detailed error messages
2. **Run diagnostic commands**: Each script includes built-in health checks
3. **Validate configuration**: Use provided templates and examples
4. **Test incrementally**: Deploy to development environment first

## Migration Strategy

### For Existing Applications

**Phase 1: Parallel Deployment**
1. Deploy HEIR platform alongside existing system
2. No changes to existing application code
3. Validate platform functionality in isolation

**Phase 2: Gradual Integration**  
1. Start with new features using HEIR patterns
2. Gradually migrate existing writes to use doctrine headers
3. Route external API calls through HEIR gateway

**Phase 3: Full Integration**
1. All database writes flow through Database Gatekeeper
2. All external APIs route through API Gateway  
3. Complete audit trail and security enforcement

### Zero-Downtime Migration
```bash
# 1. Deploy HEIR to staging environment
bash scripts/deploy-database.sh

# 2. Test integration with copy of production data
# 3. Deploy to production during maintenance window
# 4. Gradually enable HEIR features
# 5. Monitor and validate functionality
```

## Success Criteria

Your HEIR deployment is successful when:

- ✅ Database schema deploys without errors
- ✅ Platform initialization completes successfully  
- ✅ Doctrine header validation works correctly
- ✅ Database writes are properly audited
- ✅ API calls route through gateway
- ✅ Cross-tenant isolation is enforced
- ✅ Performance meets requirements
- ✅ Monitoring and alerting function

## Next Steps

After successful deployment:

1. **Integrate your application** using doctrine headers
2. **Set up monitoring** for platform health and performance
3. **Configure alerting** for security violations and errors  
4. **Train your team** on HEIR concepts and best practices
5. **Plan for scaling** as your application grows

---

**The HEIR platform is now ready to provide secure, auditable, scalable infrastructure for your application. Welcome to enterprise-grade AI agent orchestration! 🚀**