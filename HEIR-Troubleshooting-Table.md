# HEIR System Master Troubleshooting Table
## Quick Error Resolution Based on IDs and Codes

---

## Overview
This table enables instant troubleshooting by looking up any error using Unique ID, Process ID, or Error Codes. Every error in the system maps to specific troubleshooting steps that both humans and AI can follow.

**Database Table:** `shq.orbt_troubleshooting_guide`  
**Purpose:** Instant error resolution lookup for any system participant

---

## Enhanced Error Table Schema

### Primary Troubleshooting Table (`shq.orbt_troubleshooting_guide`)

```sql
CREATE TABLE shq.orbt_troubleshooting_guide (
    -- Primary Keys
    id SERIAL PRIMARY KEY,
    lookup_key VARCHAR(100) UNIQUE NOT NULL, -- For fast searching
    
    -- Identification Fields (What You See)
    unique_id_pattern VARCHAR(50) NOT NULL, -- [DB].[SUBHIVE].[MICRO].[TOOL].[ALT].[STEP]
    process_id VARCHAR(50) NOT NULL,        -- VerbObject format
    error_code VARCHAR(20) NOT NULL,        -- Standard error codes
    error_type VARCHAR(50) NOT NULL,        -- connection/validation/etc
    
    -- Human-Readable Info (What It Means)
    error_title VARCHAR(200) NOT NULL,      -- "Database Connection Failed"
    error_description TEXT NOT NULL,        -- Plain English explanation
    business_impact VARCHAR(100) NOT NULL,  -- "Users cannot log in"
    urgency_level VARCHAR(20) NOT NULL,     -- CRITICAL/HIGH/MEDIUM/LOW
    
    -- Troubleshooting Steps (What To Do)
    immediate_action TEXT NOT NULL,         -- First thing to try (30 seconds)
    diagnostic_steps TEXT[] NOT NULL,       -- Array of check commands
    resolution_steps TEXT[] NOT NULL,       -- Array of fix commands
    escalation_criteria TEXT NOT NULL,      -- When to escalate to human
    
    -- Prevention & Context (Why It Happens)
    common_causes TEXT[] NOT NULL,          -- Array of typical causes
    prevention_tips TEXT[] NOT NULL,        -- How to prevent
    related_errors VARCHAR(50)[] NULL,      -- Related error codes
    
    -- System Context (Where It Applies)
    affected_agents VARCHAR(50)[] NOT NULL, -- Which agents see this error
    affected_domains VARCHAR(50)[] NOT NULL,-- Which domains affected
    system_components TEXT[] NOT NULL,      -- Databases, APIs, etc.
    
    -- Resolution Tracking (How Often Fixed)
    auto_resolvable BOOLEAN NOT NULL DEFAULT FALSE,
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 0.0, -- Fix success %
    avg_resolution_time_minutes INTEGER NOT NULL DEFAULT 0,
    requires_human_expertise BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Documentation Links (Where To Learn More)
    documentation_links TEXT[] NULL,       -- URLs to docs
    code_examples TEXT NULL,               -- Sample fixes
    monitoring_queries TEXT[] NULL,        -- SQL to check status
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NULL,            -- When last encountered
    version VARCHAR(10) NOT NULL DEFAULT '1.0.0'
);
```

### Quick Lookup Views

```sql
-- View for AI agents to get instant troubleshooting
CREATE VIEW shq.ai_troubleshooting_lookup AS
SELECT 
    lookup_key,
    unique_id_pattern,
    process_id,
    error_code,
    error_title,
    immediate_action,
    diagnostic_steps[1] as first_diagnostic,
    resolution_steps[1] as first_resolution,
    auto_resolvable,
    success_rate
FROM shq.orbt_troubleshooting_guide
WHERE auto_resolvable = TRUE;

-- View for human troubleshooters
CREATE VIEW shq.human_troubleshooting_lookup AS
SELECT 
    unique_id_pattern,
    process_id,
    error_code,
    error_title,
    error_description,
    business_impact,
    urgency_level,
    immediate_action,
    diagnostic_steps,
    resolution_steps,
    escalation_criteria,
    documentation_links
FROM shq.orbt_troubleshooting_guide;
```

---

## Lookup Key Format

### Standard Lookup Keys
- **By Unique ID:** `UID:{unique_id_pattern}`
- **By Process ID:** `PID:{process_id}`
- **By Error Code:** `ERR:{error_code}`
- **By Combined:** `{process_id}:{error_code}`

### Examples
- `UID:01.03.001.API.20000.*` - All API errors at 20k altitude in data domain
- `PID:ValidateInput` - All input validation errors
- `ERR:CONN_TIMEOUT` - All connection timeout errors
- `ProcessPayment:PAY_DECLINED` - Payment declines in payment processing

---

## Sample Troubleshooting Entries

### Example 1: Database Connection Error
```sql
INSERT INTO shq.orbt_troubleshooting_guide VALUES (
    1,
    'ProcessData:CONN_TIMEOUT',
    '01.03.*.DB.*.*',
    'ProcessData',
    'CONN_TIMEOUT',
    'connection',
    'Database Connection Timeout',
    'The system cannot connect to the database within the timeout period (30 seconds)',
    'Data operations completely blocked, users cannot access app features',
    'HIGH',
    
    -- Immediate Action
    'Retry connection immediately, check database status endpoint',
    
    -- Diagnostic Steps
    ARRAY[
        'ping database_host',
        'SELECT 1 FROM pg_stat_activity LIMIT 1',
        'Check connection pool status',
        'Review recent database logs'
    ],
    
    -- Resolution Steps
    ARRAY[
        'Restart connection pool',
        'Scale up database instance if CPU > 80%',
        'Clear connection pool if > 90% utilized',
        'Switch to read replica if available'
    ],
    
    -- Escalation Criteria
    'If 3 retry attempts fail OR database is completely unresponsive OR >100 affected users',
    
    -- Common Causes
    ARRAY[
        'Database overload from traffic spike',
        'Connection pool exhaustion',
        'Network connectivity issues',
        'Database maintenance window'
    ],
    
    -- Prevention Tips
    ARRAY[
        'Monitor connection pool utilization',
        'Set up database auto-scaling',
        'Implement circuit breaker pattern',
        'Regular connection pool maintenance'
    ],
    
    ARRAY['CONN_REFUSED', 'CONN_LOST'],
    
    ARRAY['database-specialist', 'data-orchestrator'],
    ARRAY['data', 'platform'],
    ARRAY['PostgreSQL', 'Connection Pool', 'Neon Database'],
    
    TRUE,  -- auto_resolvable
    85.0,  -- success_rate
    5,     -- avg_resolution_time_minutes
    FALSE, -- requires_human_expertise
    
    ARRAY['https://docs.neon.tech/troubleshooting'],
    '-- Check connection status\nSELECT count(*) FROM pg_stat_activity;',
    ARRAY['SELECT * FROM pg_stat_activity WHERE state = ''active'''],
    
    NOW(), NOW(), NULL, '1.0.0'
);
```

### Example 2: Payment Processing Error
```sql
INSERT INTO shq.orbt_troubleshooting_guide VALUES (
    2,
    'ProcessPayment:PAY_DECLINED',
    '01.04.001.PAY.10000.*',
    'ProcessPayment',
    'PAY_DECLINED',
    'payment',
    'Payment Card Declined',
    'Customer payment was declined by the payment processor (Stripe)',
    'Customer cannot complete purchase, potential revenue loss',
    'MEDIUM',
    
    'Check decline reason code, notify customer with appropriate message',
    
    ARRAY[
        'Check Stripe dashboard for decline reason',
        'Verify card details format',
        'Check for fraud detection flags',
        'Review customer payment history'
    ],
    
    ARRAY[
        'Show user-friendly decline message',
        'Suggest alternative payment method',
        'Retry with 3D Secure if available',
        'Log decline for analytics'
    ],
    
    'If >10 declines in 5 minutes OR customer reports working card declined',
    
    ARRAY[
        'Insufficient funds',
        'Expired or invalid card',
        'Fraud detection triggered',
        'International card restrictions'
    ],
    
    ARRAY[
        'Pre-validate cards before processing',
        'Implement retry logic with delays',
        'Use address verification',
        'Monitor decline patterns'
    ],
    
    ARRAY['PAY_FAILED', 'PAY_FRAUD'],
    
    ARRAY['payment-specialist', 'payment-orchestrator'],
    ARRAY['payment'],
    ARRAY['Stripe API', 'Payment Gateway'],
    
    TRUE,  -- auto_resolvable
    95.0,  -- success_rate
    2,     -- avg_resolution_time_minutes
    FALSE, -- requires_human_expertise
    
    ARRAY['https://stripe.com/docs/declines'],
    'stripe.charges.retrieve(charge_id)',
    ARRAY['SELECT * FROM payments WHERE status = ''declined'' AND created_at > NOW() - INTERVAL ''1 hour'''],
    
    NOW(), NOW(), NULL, '1.0.0'
);
```

---

## Instant Lookup Functions

### For AI Agents
```sql
CREATE OR REPLACE FUNCTION get_ai_fix(error_code VARCHAR, process_id VARCHAR DEFAULT NULL)
RETURNS TABLE(
    action TEXT,
    diagnostic TEXT,
    resolution TEXT,
    can_auto_fix BOOLEAN,
    confidence DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.immediate_action,
        t.diagnostic_steps[1],
        t.resolution_steps[1],
        t.auto_resolvable,
        t.success_rate / 100.0
    FROM shq.orbt_troubleshooting_guide t
    WHERE t.error_code = error_code
    AND (process_id IS NULL OR t.process_id = process_id)
    ORDER BY t.success_rate DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

### For Human Troubleshooters
```sql
CREATE OR REPLACE FUNCTION get_human_guide(unique_id VARCHAR)
RETURNS TABLE(
    title TEXT,
    description TEXT,
    impact TEXT,
    urgency TEXT,
    immediate_action TEXT,
    diagnostic_steps TEXT[],
    resolution_steps TEXT[],
    escalation_criteria TEXT,
    documentation TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.error_title,
        t.error_description,
        t.business_impact,
        t.urgency_level,
        t.immediate_action,
        t.diagnostic_steps,
        t.resolution_steps,
        t.escalation_criteria,
        t.documentation_links
    FROM shq.orbt_troubleshooting_guide t
    WHERE unique_id LIKE t.unique_id_pattern
    ORDER BY t.success_rate DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
```

---

## Integration with Error Logging

### Enhanced Error Log Table (Updated)
```sql
-- Add troubleshooting reference to main error log
ALTER TABLE shq.orbt_error_log 
ADD COLUMN troubleshooting_key VARCHAR(100),
ADD COLUMN auto_fix_attempted BOOLEAN DEFAULT FALSE,
ADD COLUMN auto_fix_success BOOLEAN DEFAULT NULL,
ADD COLUMN human_guide_referenced BOOLEAN DEFAULT FALSE;

-- Auto-populate troubleshooting key
CREATE OR REPLACE FUNCTION link_troubleshooting()
RETURNS TRIGGER AS $$
BEGIN
    -- Try to find troubleshooting entry
    UPDATE shq.orbt_error_log 
    SET troubleshooting_key = (
        SELECT lookup_key 
        FROM shq.orbt_troubleshooting_guide t
        WHERE NEW.error_type = t.error_type
        OR NEW.error_id LIKE t.unique_id_pattern
        LIMIT 1
    )
    WHERE error_id = NEW.error_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_link_troubleshooting
    AFTER INSERT ON shq.orbt_error_log
    FOR EACH ROW
    EXECUTE FUNCTION link_troubleshooting();
```

---

## Usage Examples

### For AI Agents
```python
# AI agent encounters error
error_result = db.query("""
    SELECT * FROM get_ai_fix('CONN_TIMEOUT', 'ProcessData')
""")

if error_result.can_auto_fix and error_result.confidence > 0.8:
    # Execute auto-fix
    execute_fix(error_result.resolution)
    log_attempt(error_id, 'auto_fix_attempted', True)
else:
    # Escalate to human
    escalate_to_human(error_id, error_result.action)
```

### For Human Troubleshooters
```python
# Human sees error ID: 01.03.001.API.20000.005
guide = db.query("""
    SELECT * FROM get_human_guide('01.03.001.API.20000.005')
""")

print(f"Error: {guide.title}")
print(f"Impact: {guide.impact}")
print(f"Urgency: {guide.urgency}")
print(f"First Action: {guide.immediate_action}")
print("\nDiagnostic Steps:")
for step in guide.diagnostic_steps:
    print(f"  - {step}")
```

### For Dashboard Display
```sql
-- Show all active errors with troubleshooting info
SELECT 
    e.error_id,
    e.agent_id,
    t.error_title,
    t.urgency_level,
    t.immediate_action,
    e.occurrence_count,
    CASE 
        WHEN t.auto_resolvable THEN 'Auto-fixable'
        WHEN t.requires_human_expertise THEN 'Needs Expert'
        ELSE 'Standard Process'
    END as resolution_type
FROM shq.orbt_error_log e
JOIN shq.orbt_troubleshooting_guide t ON e.troubleshooting_key = t.lookup_key
WHERE e.resolved = FALSE
ORDER BY 
    CASE t.urgency_level 
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    e.occurrence_count DESC;
```

---

## Maintenance Procedures

### Regular Updates
1. **Weekly:** Review error patterns and update success rates
2. **Monthly:** Add new troubleshooting entries for novel errors
3. **Quarterly:** Review and optimize resolution steps
4. **As Needed:** Update documentation links and code examples

### Quality Assurance
1. **Test all resolution steps** before adding to table
2. **Validate all diagnostic commands** work correctly
3. **Ensure escalation criteria** are clear and actionable
4. **Keep documentation links** current and accessible

---

## Benefits

### For AI Agents
- **Instant decisions:** Know immediately if error is auto-fixable
- **Proven solutions:** Apply steps with known success rates
- **Smart escalation:** Only escalate when truly needed
- **Learning capability:** Understand why fixes work

### For Human Troubleshooters
- **Fast resolution:** Get right to the solution
- **Complete context:** Understand business impact
- **Clear escalation:** Know when to involve experts
- **Prevention focus:** Avoid recurring issues

### For System Operations
- **Reduced downtime:** Faster resolution of all errors
- **Higher automation:** More errors resolved without humans
- **Better documentation:** Knowledge base grows over time
- **Predictable performance:** Known resolution times

---

*This troubleshooting table transforms error handling from reactive debugging to proactive problem-solving with instant access to proven solutions.*