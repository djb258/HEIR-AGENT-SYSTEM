# Medium Project Template

## Overview
**Complexity**: Medium (Multiple services, external integrations)  
**Timeline**: 4-8 hours  
**Agents Required**: CEO Orchestrator + Project Planner + All Division Managers + 4-6 Specialists  
**Example**: E-commerce platform, content management system, data pipeline  

## Project Structure
```
medium-project/
├── .claude/
│   └── agents/
│       ├── orchestrators/
│       ├── managers/
│       └── specialists/
├── services/
│   ├── api-gateway/
│   ├── user-service/
│   ├── product-service/
│   ├── payment-service/
│   └── notification-service/
├── shared/
│   ├── database/
│   ├── messaging/
│   └── utils/
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── monitoring/
├── tests/
├── package.json
├── docker-compose.yml
└── README.md
```

## Delegation Flow Example

### User Request
```
"Build an e-commerce platform with product catalog, user management, payments, and order processing"
```

### Project Planner Response
```
## Complex Project Analysis

### System Architecture
- Microservices architecture
- API Gateway for routing
- Event-driven communication
- Shared database with service-specific schemas
- External payment integration

### Service Breakdown
1. **API Gateway**: Request routing, authentication, rate limiting
2. **User Service**: Registration, profiles, authentication
3. **Product Service**: Catalog management, inventory
4. **Payment Service**: Stripe integration, order processing
5. **Notification Service**: Email, SMS, webhooks

### Dependencies & Coordination
- User Service → Database (Neon)
- Product Service → Database (Neon)
- Payment Service → Stripe API
- All Services → Message Queue (Redis)
- API Gateway → All Services

### Timeline Estimate
- Architecture Design: 1 hour
- Service Development: 4 hours
- Integration Testing: 2 hours
- Deployment & Monitoring: 1 hour
- Total: 8 hours

### Resource Requirements
- Database: Neon PostgreSQL
- Payment: Stripe
- Deployment: Render (multiple services)
- Monitoring: Health checks, logging
```

### CEO Orchestrator → Division Managers
```
"Coordinate development of e-commerce platform with the following requirements:
- Backend Manager: Design API architecture and database schemas
- Integration Manager: Handle Stripe payments and external integrations
- Deployment Manager: Set up multi-service deployment and monitoring"
```

### Backend Manager → Neon Integrator
```
"Create database schemas for e-commerce platform:
- Users table with authentication
- Products table with categories
- Orders table with order items
- Inventory tracking
- Support for multiple payment methods"
```

### Neon Integrator Response
```
## Database Schema Implementation

### Core Tables
```sql
-- Users and Authentication
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  phone VARCHAR(20),
  address JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products and Categories
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  parent_id INTEGER REFERENCES categories(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  category_id INTEGER REFERENCES categories(id),
  sku VARCHAR(100) UNIQUE,
  inventory_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders and Order Items
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  status VARCHAR(50) DEFAULT 'pending',
  total_amount DECIMAL(10,2) NOT NULL,
  shipping_address JSONB,
  billing_address JSONB,
  payment_intent_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES orders(id),
  product_id INTEGER REFERENCES products(id),
  quantity INTEGER NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL
);

-- Payment Methods
CREATE TABLE payment_methods (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  stripe_payment_method_id VARCHAR(255),
  type VARCHAR(50),
  last_four VARCHAR(4),
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Performance
- Composite indexes on frequently queried columns
- Full-text search on product names and descriptions
- Partitioning strategy for orders table
- Connection pooling with 20 connections
```

### Integration Manager → Stripe Handler
```
"Implement payment processing for e-commerce orders:
- Payment intent creation
- Subscription management for recurring orders
- Webhook processing for payment events
- Refund handling
- Multiple payment method support"
```

### Stripe Handler Response
```
## Payment System Implementation

### Payment Flow
1. **Order Creation**: Create payment intent with order details
2. **Payment Processing**: Handle card payments, digital wallets
3. **Webhook Processing**: Update order status on payment events
4. **Subscription Management**: Handle recurring payments
5. **Refund Processing**: Handle returns and refunds

### Endpoints Created
- POST /api/payments/create-intent
- POST /api/payments/confirm
- POST /api/payments/refund
- POST /api/subscriptions/create
- POST /api/webhooks/stripe

### Webhook Events Handled
- payment_intent.succeeded
- payment_intent.payment_failed
- invoice.payment_succeeded
- invoice.payment_failed
- customer.subscription.created
- customer.subscription.updated

### Security Implementation
- Webhook signature verification
- PCI compliance measures
- Rate limiting on payment endpoints
- Input validation and sanitization
```

### Integration Manager → Firecrawl Scraper
```
"Implement product data enrichment:
- Scrape competitor pricing
- Extract product images and descriptions
- Monitor price changes
- Gather product reviews and ratings"
```

### Firecrawl Scraper Response
```
## Data Enrichment Implementation

### Scraping Strategy
- Target: Major e-commerce competitors
- Frequency: Daily price monitoring
- Data: Pricing, availability, reviews
- Rate limiting: 10 requests/minute

### Data Pipeline
1. **Extraction**: Scrape competitor websites
2. **Transformation**: Clean and structure data
3. **Enrichment**: Match with internal products
4. **Storage**: Update product database
5. **Alerting**: Notify on significant price changes

### Ethical Configuration
- Respect robots.txt
- Proper user agent identification
- Reasonable request delays
- Data usage compliance
```

### Deployment Manager → Render Deployer
```
"Deploy multi-service e-commerce platform:
- API Gateway service
- User service
- Product service
- Payment service
- Notification service
- Shared database
- Message queue
- Monitoring and health checks"
```

### Render Deployer Response
```
## Multi-Service Deployment

### Service Configuration
```yaml
services:
  - type: web
    name: api-gateway
    env: node
    plan: starter
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        sync: false
    healthCheckPath: /health

  - type: web
    name: user-service
    env: node
    plan: starter
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        sync: false
    healthCheckPath: /health

  - type: web
    name: product-service
    env: node
    plan: starter
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        sync: false
    healthCheckPath: /health

  - type: web
    name: payment-service
    env: node
    plan: starter
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
    healthCheckPath: /health
```

### Infrastructure Setup
- **Database**: Neon PostgreSQL with connection pooling
- **Message Queue**: Redis for inter-service communication
- **Monitoring**: Health checks for all services
- **SSL**: Automatic HTTPS for all endpoints
- **Scaling**: Auto-scaling based on CPU/memory usage
```

## Implementation Phases

### Phase 1: Architecture & Setup (2 hours)
- [ ] Design microservices architecture
- [ ] Set up shared database
- [ ] Configure message queue
- [ ] Create service templates

### Phase 2: Core Services (3 hours)
- [ ] Implement API Gateway
- [ ] Build User Service
- [ ] Create Product Service
- [ ] Develop Payment Service

### Phase 3: Integration & Testing (2 hours)
- [ ] Integrate services via message queue
- [ ] Test payment flows
- [ ] Validate data consistency
- [ ] Performance testing

### Phase 4: Deployment & Monitoring (1 hour)
- [ ] Deploy all services
- [ ] Configure monitoring
- [ ] Set up alerts
- [ ] Load testing

## Code Examples

### API Gateway Configuration
```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');

const app = express();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use(limiter);

// Service routing
app.use('/api/users', createProxyMiddleware({
  target: process.env.USER_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: { '^/api/users': '' }
}));

app.use('/api/products', createProxyMiddleware({
  target: process.env.PRODUCT_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: { '^/api/products': '' }
}));

app.use('/api/payments', createProxyMiddleware({
  target: process.env.PAYMENT_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: { '^/api/payments': '' }
}));
```

### Event-Driven Communication
```javascript
// Message queue setup
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

// Publish event
const publishEvent = async (eventType, data) => {
  await redis.publish('events', JSON.stringify({
    type: eventType,
    data: data,
    timestamp: new Date().toISOString()
  }));
};

// Subscribe to events
const subscribeToEvents = (eventTypes, handler) => {
  redis.subscribe('events', (err) => {
    if (err) console.error('Subscription error:', err);
  });

  redis.on('message', (channel, message) => {
    const event = JSON.parse(message);
    if (eventTypes.includes(event.type)) {
      handler(event);
    }
  });
};

// Example: Order created event
await publishEvent('order.created', {
  orderId: order.id,
  userId: order.userId,
  totalAmount: order.totalAmount
});
```

## Success Metrics
- ✅ All services deployed and healthy
- ✅ API Gateway routing correctly
- ✅ Database connections stable
- ✅ Payment processing working
- ✅ Event-driven communication functional
- ✅ Monitoring and alerting active
- ✅ Performance benchmarks met

## Common Issues & Solutions

### Service Communication Issues
- **Problem**: Services can't communicate
- **Solution**: Check message queue configuration
- **ORBP**: Automatic service restart and reconnection

### Database Connection Issues
- **Problem**: Connection pool exhaustion
- **Solution**: Optimize connection pooling settings
- **ORBP**: Connection retry with exponential backoff

### Payment Processing Issues
- **Problem**: Webhook verification fails
- **Solution**: Verify webhook secret and signature
- **ORBP**: Manual payment status reconciliation

### Deployment Issues
- **Problem**: Service startup failures
- **Solution**: Check environment variables and dependencies
- **ORBP**: Automatic rollback to previous version

## Next Steps
After successful deployment:
1. Implement caching layer (Redis)
2. Add comprehensive logging
3. Set up automated testing pipeline
4. Configure backup and disaster recovery
5. Implement user analytics and reporting
6. Add A/B testing capabilities
