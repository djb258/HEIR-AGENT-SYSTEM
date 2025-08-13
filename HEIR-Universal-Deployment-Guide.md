# HEIR System Universal Deployment Guide
## Drop Into ANY Application - Complete Template

---

## Overview
The HEIR system is now completely templated for universal deployment. Drop it into any application and get instant AI organization with error logging, troubleshooting, resolution tracking, and 600-page doctrine integration.

**Universal Compatibility:** Works with any tech stack, any database, any application architecture.

---

## One-Command Universal Setup

### Step 1: Drop Into Any Project
```bash
# Copy heir-drop-in.js to your project root
curl -O https://raw.githubusercontent.com/djb258/HEIR-AGENT-SYSTEM/master/heir-drop-in.js

# Run setup (works in ANY project directory)
node heir-drop-in.js
```

### What This Creates (Universal Template)
```
your-project/
├── .heir/                                  ← HEIR system files
│   ├── database_schemas/
│   │   ├── orbt-schema.sql                ← Complete database structure  
│   │   └── troubleshooting-data.sql       ← Default error patterns
│   ├── institutional_knowledge/           ← Learning storage
│   ├── orbt_logs/                         ← Error tracking
│   └── project_configs/                   ← Configuration storage
├── .claude/                               ← Claude Code integration
│   └── agents/                            ← Agent definitions
├── heir-project-config.json               ← Your project configuration
└── [your existing application files]     ← Unchanged
```

---

## Universal Database Setup

### Option A: PostgreSQL/Neon (Recommended)
```bash
# Deploy complete HEIR database schema
psql -d your_database -f .heir/database_schemas/orbt-schema.sql

# Load default troubleshooting patterns
psql -d your_database -f .heir/database_schemas/troubleshooting-data.sql

# If you have existing dpr_doctrine table
psql -d your_database -c "SELECT shq.migrate_doctrine_from_dpr();"
```

### Option B: Any PostgreSQL Compatible Database
```bash
# Works with: Supabase, AWS RDS, Google Cloud SQL, Azure PostgreSQL, etc.
export DATABASE_URL="your_postgres_connection_string"
psql $DATABASE_URL -f .heir/database_schemas/orbt-schema.sql
```

### Option C: Other Databases
The SQL schema can be adapted to:
- **MySQL/MariaDB**: Replace TIMESTAMPTZ with TIMESTAMP, adjust array syntax
- **SQLite**: Replace arrays with JSON columns, simplify functions
- **MongoDB**: Use the schema as document structure reference

---

## Universal Application Integration

### Any Node.js Application
```javascript
// Add to your existing Node.js app
const { logErrorToHeir, consultDoctrine, getResolution } = require('./heir-integration');

// In your error handlers
app.use((error, req, res, next) => {
    // Log to HEIR system automatically
    logErrorToHeir({
        error_id: generateUniqueId(req),
        agent_id: 'your-app-name',
        error_type: error.name,
        error_message: error.message,
        subhive_code: '01' // SHQ for general app errors
    });
    
    next(error);
});

// Before making important decisions
async function processPayment(paymentData) {
    // Consult doctrine first
    const doctrine = await consultDoctrine('04', 'payment processing', paymentData.amount);
    
    if (doctrine.escalation_required) {
        return escalateToHuman(paymentData, doctrine);
    }
    
    // Proceed with doctrine compliance
    return executePayment(paymentData, doctrine.behavioral_rules);
}
```

### Any Python Application  
```python
# Add to your existing Python app
from heir_integration import log_error_to_heir, consult_doctrine, get_resolution

# In your error handlers
def handle_error(error, context):
    # Log to HEIR system automatically
    log_error_to_heir(
        error_id=generate_unique_id(context),
        agent_id='your-python-app',
        error_type=type(error).__name__,
        error_message=str(error),
        subhive_code='01'
    )

# Before important operations
def process_data(data_request):
    # Consult doctrine first
    doctrine = consult_doctrine('03', 'data processing', data_request.type)
    
    if not doctrine.is_compliant:
        raise DoctrineViolationError(doctrine.violation_reason)
    
    # Proceed with doctrine-approved processing
    return execute_data_processing(data_request, doctrine.rules)
```

### Any Web Framework
```javascript
// Express.js, FastAPI, Rails, Django, etc.
// HEIR error middleware (universal pattern)
function heirErrorMiddleware(error, context) {
    const uniqueId = generateUniqueId(context);
    
    // Log error
    heirSystem.logError({
        error_id: uniqueId,
        error_type: error.constructor.name,
        error_message: error.message,
        context: context.path || context.route
    });
    
    // Try to get automatic fix
    const resolution = heirSystem.getResolution(uniqueId);
    
    if (resolution.auto_resolvable && resolution.confidence > 0.8) {
        heirSystem.applyFix(resolution);
        return { status: 'auto_resolved', resolution: resolution };
    }
    
    // Escalate if needed
    return heirSystem.escalateError(error, context);
}
```

---

## Universal Configuration Template

### Project Configuration (heir-project-config.json)
```json
{
  "project_name": "ANY_PROJECT_NAME",
  "project_description": "Description of what you're building",
  "architecture_model": "skyscraper_construction",
  
  "database": {
    "type": "postgresql",
    "connection_string": "YOUR_DATABASE_URL",
    "schema": "shq",
    "existing_doctrine_table": "dpr_doctrine"
  },
  
  "agents_needed": {
    "master_orchestrator": { "use_this_agent": true },
    "data_orchestrator": { "use_this_agent": false },
    "payment_orchestrator": { "use_this_agent": false },
    "integration_orchestrator": { "use_this_agent": false },
    "platform_orchestrator": { "use_this_agent": false }
  },
  
  "orbt_system": {
    "error_logging": true,
    "troubleshooting_guide": true,
    "resolution_tracking": true,
    "doctrine_integration": true,
    "3_strike_escalation": true
  }
}
```

### Environment Variables (Universal)
```bash
# Required
HEIR_DATABASE_URL=your_database_connection_string
HEIR_PROJECT_NAME=your_project_name

# Optional  
HEIR_SUBHIVE_MAPPING='{"web":"02","api":"05","payments":"04"}'
HEIR_ESCALATION_WEBHOOK=https://your-domain.com/heir-escalation
HEIR_DOCTRINE_AUTO_MIGRATE=true
```

---

## Universal Integration Examples

### E-commerce Application
```javascript
// Existing e-commerce app + HEIR
const express = require('express');
const heir = require('./heir-integration');

app.post('/api/checkout', async (req, res) => {
    try {
        // Consult payment doctrine
        const doctrine = await heir.consultDoctrine('04', 'process payment', req.body);
        
        if (doctrine.requires_approval && req.body.amount > 1000) {
            return heir.requestHumanApproval(req.body, doctrine);
        }
        
        const result = await processPayment(req.body);
        res.json(result);
        
    } catch (error) {
        // Automatic HEIR error handling
        const resolution = await heir.handleError(error, {
            unique_id: '04.001.001.API.10000.001',
            context: 'payment processing',
            request: req.body
        });
        
        if (resolution.auto_resolved) {
            res.json({ success: true, note: 'Issue auto-resolved' });
        } else {
            res.status(500).json({ error: 'Payment failed', ticket: resolution.escalation_id });
        }
    }
});
```

### SaaS Application
```python
# Existing SaaS app + HEIR
from flask import Flask, request, jsonify
from heir_integration import HeirSystem

app = Flask(__name__)
heir = HeirSystem(project_name='my-saas', database_url=os.getenv('DATABASE_URL'))

@app.route('/api/data/export', methods=['POST'])
def export_data():
    try:
        # Consult data doctrine
        doctrine = heir.consult_doctrine('03', 'data export', request.json)
        
        if not doctrine.is_compliant:
            return jsonify({'error': doctrine.violation_reason}), 403
            
        result = perform_data_export(request.json, doctrine.rules)
        return jsonify(result)
        
    except Exception as error:
        # Automatic HEIR error handling  
        resolution = heir.handle_error(error, {
            'unique_id': '03.005.001.API.10000.001',
            'context': 'data export',
            'request': request.json
        })
        
        if resolution.auto_resolved:
            return jsonify({'success': True, 'note': 'Issue auto-resolved'})
        else:
            return jsonify({'error': 'Export failed', 'ticket': resolution.escalation_id}), 500
```

### API Service
```javascript
// Existing API + HEIR
const fastify = require('fastify')({ logger: true });
const heir = require('./heir-integration');

// Universal error handler
fastify.setErrorHandler(async (error, request, reply) => {
    const resolution = await heir.handleError(error, {
        unique_id: heir.generateUniqueId(request),
        context: `${request.method} ${request.url}`,
        request: request.body
    });
    
    if (resolution.auto_resolved) {
        reply.code(200).send({ success: true, resolved: true });
    } else {
        reply.code(500).send({ 
            error: 'Internal error', 
            ticket: resolution.escalation_id,
            human_notified: resolution.escalated
        });
    }
});

// Doctrine-aware route
fastify.post('/api/integration/:service', async (request, reply) => {
    const doctrine = await heir.consultDoctrine('05', 'external integration', request.params.service);
    
    if (doctrine.escalation_required) {
        return heir.escalateToHuman(request, doctrine);
    }
    
    return processIntegration(request, doctrine.behavioral_rules);
});
```

---

## Universal Monitoring Dashboard

### Real-time Status (Works with ANY application)
```sql
-- Universal system health query
SELECT 
    'System Status' as metric,
    CASE 
        WHEN red_count > 0 THEN '🔴 CRITICAL'
        WHEN yellow_count > 5 THEN '🟡 WARNING'  
        ELSE '🟢 HEALTHY'
    END as status,
    green_count as auto_resolved,
    yellow_count as warnings,
    red_count as critical_errors,
    escalation_pending as human_needed
FROM shq.orbt_system_status 
WHERE status_id = 'SYSTEM_STATUS_' || TO_CHAR(NOW(), 'YYYY_MM_DD')

UNION ALL

-- Doctrine compliance across all subhives
SELECT 
    'Doctrine Compliance' as metric,
    ROUND(AVG(CASE WHEN doctrine_compliance = 'COMPLIANT' THEN 100.0 ELSE 0.0 END), 1)::TEXT || '%' as status,
    COUNT(CASE WHEN doctrine_compliance = 'COMPLIANT' THEN 1 END) as compliant,
    COUNT(CASE WHEN doctrine_compliance = 'EXCEPTION' THEN 1 END) as exceptions,
    COUNT(CASE WHEN human_review_required THEN 1 END) as needs_review,
    NULL
FROM shq.orbt_doctrine_integration 
WHERE consulted_at > NOW() - INTERVAL '24 hours';
```

---

## Universal Deployment Checklist

### ✅ Pre-Deployment
- [ ] `node heir-drop-in.js` completed successfully
- [ ] Database connection string configured
- [ ] heir-project-config.json filled out
- [ ] Environment variables set

### ✅ Database Setup
- [ ] PostgreSQL schema deployed (`orbt-schema.sql`)
- [ ] Troubleshooting data loaded (`troubleshooting-data.sql`)
- [ ] Doctrine migrated (if `dpr_doctrine` exists)
- [ ] Database permissions configured

### ✅ Application Integration
- [ ] Error handlers updated to use HEIR logging
- [ ] Critical operations consult doctrine
- [ ] Unique ID generation implemented
- [ ] Escalation endpoints configured

### ✅ Production Monitoring
- [ ] System status dashboard accessible
- [ ] Error escalation notifications working
- [ ] Doctrine compliance monitoring active
- [ ] Resolution tracking functioning

---

## Universal Troubleshooting

### Common Issues & Solutions

#### "dpr_doctrine table not found"
```sql
-- Create sample doctrine for testing
CREATE TABLE dpr_doctrine (
    section VARCHAR(100),
    subsection VARCHAR(100),
    title VARCHAR(200),
    content TEXT,
    version VARCHAR(10) DEFAULT '1.0'
);

INSERT INTO dpr_doctrine VALUES 
('PAY.001', 'ProcessPayment', 'Payment Processing Rules', 'Must validate all payments. Must retry failed payments maximum 3 times.', '1.0'),
('DATA.001', 'DatabaseAccess', 'Database Security Rules', 'Must encrypt all data. Must audit all access attempts.', '1.0');
```

#### "Schema deployment fails"
- Check PostgreSQL version (9.4+ required)
- Ensure user has CREATE privileges
- Verify database connection string

#### "Agents not consulting doctrine"
- Verify doctrine migration completed
- Check subhive code mapping
- Ensure unique ID format correct

---

## Benefits of Universal Template

### For Any Application
- **Zero vendor lock-in** - Works with any tech stack
- **Instant intelligence** - 30 seconds from zero to AI organization
- **Universal patterns** - Same approach works everywhere
- **Gradual adoption** - Add HEIR features incrementally

### For Any Team
- **No learning curve** - Familiar database and API patterns
- **Immediate value** - See results from first error logged
- **Scalable complexity** - Start simple, add features as needed
- **Cross-project knowledge** - Solutions work across all applications

---

*The HEIR system is now universally templated. Drop into any application, any database, any architecture - get instant AI organization with error handling, doctrine compliance, and institutional learning.*