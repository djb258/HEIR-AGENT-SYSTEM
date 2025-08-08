# Simple Project Template

## Overview
**Complexity**: Low (Single service, minimal dependencies)  
**Timeline**: 1-2 hours  
**Agents Required**: CEO Orchestrator + 1-2 Division Managers + 2-3 Specialists  
**Example**: Basic API, simple database, single deployment  

## Project Structure
```
simple-project/
├── .claude/
│   └── agents/
│       ├── orchestrators/
│       ├── managers/
│       └── specialists/
├── src/
│   ├── api/
│   ├── database/
│   └── config/
├── tests/
├── package.json
├── .env.example
└── README.md
```

## Delegation Flow Example

### User Request
```
"Build a simple user management API with authentication"
```

### CEO Orchestrator Response
```
## Project Analysis

### Requirements Breakdown
- User registration and login
- JWT authentication
- Basic CRUD operations
- PostgreSQL database
- RESTful API design

### Division Assignment
- Backend Manager: API design, authentication, database schema
- Deployment Manager: Platform setup, environment configuration

### Timeline Estimate
- Development: 45 minutes
- Testing: 15 minutes
- Deployment: 30 minutes
- Total: 1.5 hours

### Success Criteria
- Users can register and login
- JWT tokens are generated and validated
- CRUD operations work for user management
- API is deployed and accessible
```

### Backend Manager → Neon Integrator
```
"Create database schema for user management with authentication"
```

### Neon Integrator Response
```
## Database Implementation

### Schema Created
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Connection Configuration
- Database URL: postgresql://user:pass@host:port/db
- Pool size: 10 connections
- SSL: enabled
- Timeout: 30 seconds

### ORBP Integration
- Connection retry logic implemented
- Query timeout handling
- Connection pool monitoring
```

### Backend Manager → Render Deployer
```
"Deploy the user management API to Render"
```

### Render Deployer Response
```
## Deployment Configuration

### Service Setup
- Platform: Render
- Environment: Node.js
- Build command: npm install && npm run build
- Start command: npm start

### Environment Variables
- DATABASE_URL: [configured]
- JWT_SECRET: [configured]
- NODE_ENV: production

### Health Check
- Endpoint: /health
- Interval: 30 seconds
- Timeout: 10 seconds

### SSL/HTTPS
- Automatic SSL certificate
- Custom domain support
- Force HTTPS redirect
```

## Implementation Checklist

### Phase 1: Setup (15 minutes)
- [ ] Initialize project structure
- [ ] Install dependencies (Express, JWT, bcrypt, pg)
- [ ] Configure environment variables
- [ ] Set up database connection

### Phase 2: Core Features (30 minutes)
- [ ] Create user registration endpoint
- [ ] Implement JWT authentication
- [ ] Add user CRUD operations
- [ ] Set up middleware (cors, json, auth)

### Phase 3: Testing & Deployment (45 minutes)
- [ ] Write basic tests
- [ ] Configure Render deployment
- [ ] Set up environment variables
- [ ] Deploy and verify functionality

## Code Examples

### Basic Express Server
```javascript
const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Authentication Middleware
```javascript
const jwt = require('jsonwebtoken');

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

module.exports = authenticateToken;
```

## Success Metrics
- ✅ API responds to health check
- ✅ User registration works
- ✅ JWT authentication functions
- ✅ CRUD operations successful
- ✅ Database connections stable
- ✅ Deployment accessible via HTTPS

## Common Issues & Solutions

### Database Connection Issues
- **Problem**: Connection timeout
- **Solution**: Check DATABASE_URL and SSL settings
- **ORBP**: Automatic retry with exponential backoff

### JWT Token Issues
- **Problem**: Token validation fails
- **Solution**: Verify JWT_SECRET environment variable
- **ORBP**: Token refresh mechanism

### Deployment Issues
- **Problem**: Build fails
- **Solution**: Check package.json and build commands
- **ORBP**: Automatic rollback to previous version

## Next Steps
After successful deployment:
1. Add input validation
2. Implement rate limiting
3. Add logging and monitoring
4. Set up automated testing
5. Configure backup strategies
