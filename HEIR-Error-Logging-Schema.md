# HEIR System Master Error Logging Schema
## Centralized ORBT Error Tracking in SHQ Database

---

## Overview
All HEIR system errors are centrally logged in the SHQ (System Headquarters) database schema. This provides unified error tracking, pattern recognition, and automated escalation across all domains and agents.

**Database Schema:** `shq`  
**Primary Table:** `shq.orbt_error_log`  
**Supporting Tables:** 6 interconnected tables for complete error lifecycle management

---

## Core Error Logging Tables

### 1. Master Error Log Table (`shq.orbt_error_log`)
**Purpose:** Central repository for all system errors across all agents and domains

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| error_id | VARCHAR(50) | Unique ID: [DB].[SUBHIVE].[MICROPROCESS].[TOOL].[ALTITUDE].[STEP] | Yes |
| orbt_status | VARCHAR(10) | GREEN/YELLOW/RED classification | Yes |
| timestamp | TIMESTAMPTZ | When error occurred | Yes |
| agent_id | VARCHAR(100) | Which agent encountered error | Yes |
| agent_hierarchy | VARCHAR(20) | orchestrator/manager/specialist | Yes |
| error_type | VARCHAR(50) | connection/validation/doctrine/escalation | Yes |
| error_message | TEXT | Detailed error description | Yes |
| error_stack | TEXT | Full stack trace | No |
| occurrence_count | INTEGER | Times this error has occurred | Yes |
| escalation_level | INTEGER | 0=first, 1=second, 2=escalated | Yes |
| requires_human | BOOLEAN | Needs human intervention | Yes |
| resolved | BOOLEAN | Has been resolved | Yes |
| resolution_method | VARCHAR(50) | How it was resolved | No |

**Automatic Actions:**
- Triggers escalation at 2+ occurrences
- Updates system status in real-time
- Links to pattern recognition

### 2. Agent Performance Metrics (`shq.orbt_agent_metrics`)
**Purpose:** Track agent performance and resource usage

| Column | Type | Description |
|--------|------|-------------|
| metric_id | VARCHAR(50) | Unique metric ID |
| agent_id | VARCHAR(100) | Agent being measured |
| execution_time_ms | INTEGER | Operation duration |
| token_usage | INTEGER | AI tokens consumed |
| success | BOOLEAN | Operation succeeded |
| error_count | INTEGER | Errors encountered |
| retry_count | INTEGER | Retry attempts |

### 3. System Status Overview (`shq.orbt_system_status`)
**Purpose:** Real-time system health dashboard

| Column | Type | Description |
|--------|------|-------------|
| status_id | VARCHAR(50) | Daily status ID |
| overall_status | VARCHAR(10) | System-wide GREEN/YELLOW/RED |
| green_count | INTEGER | Green errors (last 24h) |
| yellow_count | INTEGER | Yellow warnings (last 24h) |
| red_count | INTEGER | Red critical errors (last 24h) |
| active_agents | INTEGER | Currently active agents |
| escalation_pending | INTEGER | Pending escalations |

### 4. Training Log (`shq.orbt_training_log`)
**Purpose:** Capture institutional learning from error resolutions

| Column | Type | Description |
|--------|------|-------------|
| training_id | VARCHAR(50) | Unique training entry |
| intervention_type | VARCHAR(50) | manual_fix/auto_repair/escalation |
| agent_id | VARCHAR(100) | Agent that learned |
| problem_description | TEXT | What went wrong |
| solution_applied | TEXT | How it was fixed |
| success | BOOLEAN | Solution worked |
| pattern_recognized | BOOLEAN | Matches known pattern |
| lessons_learned | TEXT | Knowledge captured |

### 5. Error Pattern Recognition (`shq.orbt_error_patterns`)
**Purpose:** Identify recurring errors for automated resolution

| Column | Type | Description |
|--------|------|-------------|
| pattern_id | VARCHAR(50) | Unique pattern ID |
| error_signature | VARCHAR(500) | Pattern identifier |
| occurrence_count | INTEGER | Times seen |
| confidence_score | DECIMAL(5,2) | Pattern confidence (0-1) |
| known_solution | TEXT | Proven fix |
| auto_resolution_available | BOOLEAN | Can auto-fix |

### 6. Escalation Queue (`shq.orbt_escalation_queue`)
**Purpose:** Manage human intervention requests

| Column | Type | Description |
|--------|------|-------------|
| escalation_id | VARCHAR(50) | Unique escalation ID |
| priority | VARCHAR(10) | LOW/MEDIUM/HIGH/CRITICAL |
| status | VARCHAR(20) | PENDING/IN_PROGRESS/RESOLVED |
| error_id | VARCHAR(50) | Link to error log |
| assigned_to | VARCHAR(100) | Human assignee |
| escalated_at | TIMESTAMPTZ | When escalated |
| resolution_notes | TEXT | How resolved |

---

## ORBT Integration Points

### Operate Stage
- Log all operational metrics to `shq.orbt_agent_metrics`
- Track success rates and performance baselines
- Monitor resource consumption patterns

### Repair Stage (PRIMARY FOCUS)
- **Every error MUST create entry in `shq.orbt_error_log`**
- Automatic pattern matching against `shq.orbt_error_patterns`
- Strike 1: Query known solutions, log attempt
- Strike 2: Try alternatives, update occurrence count
- Strike 3: Create escalation in `shq.orbt_escalation_queue`

### Build Stage
- Analyze error patterns to identify enhancement opportunities
- Track which builds introduce new error types
- Monitor build success/failure rates

### Train Stage
- All resolutions logged to `shq.orbt_training_log`
- Successful fixes become patterns in `shq.orbt_error_patterns`
- Knowledge accumulates for future auto-resolution

---

## Automatic Escalation Rules

### Rule 1: Occurrence-Based Escalation
```sql
IF occurrence_count >= 2 THEN
    SET orbt_status = 'RED'
    SET requires_human = TRUE
    CREATE escalation_queue entry
```

### Rule 2: Pattern Recognition
```sql
IF error matches known_pattern AND confidence > 0.8 THEN
    APPLY known_solution
    LOG to training_log
ELSE
    ESCALATE to next strike level
```

### Rule 3: Business Impact
```sql
IF affected_users > threshold OR downtime_seconds > limit THEN
    SET priority = 'CRITICAL'
    IMMEDIATE human escalation
```

---

## Error ID Generation Format

### Standard Format
`[DB].[SUBHIVE].[MICROPROCESS].[TOOL].[ALTITUDE].[STEP]`

### Component Breakdown
- **DB:** Database code (01 for SHQ)
- **SUBHIVE:** 01-10 per Barton Doctrine
- **MICROPROCESS:** Process within subhive (001-999)
- **TOOL:** Tool/system code (API, WEB, CLI)
- **ALTITUDE:** Operational level (30000, 20000, 10000, 5000, 1000)
- **STEP:** Sequential step (001-999)

### Example Error IDs
- `01.01.001.API.20000.001` - SHQ API error at 20k altitude
- `01.03.042.WEB.10000.015` - Data web interface error at 10k
- `01.04.001.PAY.5000.003` - Payment processing detailed error

---

## Implementation Requirements

### For All Agents
1. **Import error logging client library**
2. **Wrap all operations in try-catch blocks**
3. **Log every exception to `shq.orbt_error_log`**
4. **Include full context in error messages**
5. **Update metrics after each operation**

### For Orchestrators
1. **Monitor specialist error rates**
2. **Coordinate cross-domain error handling**
3. **Manage escalation decisions**
4. **Aggregate metrics for reporting**

### For Specialists
1. **Log detailed error context**
2. **Report to domain orchestrator**
3. **Apply known fixes from patterns**
4. **Document new solutions**

---

## Query Examples

### Get Current System Status
```sql
SELECT * FROM shq.orbt_system_status 
ORDER BY timestamp DESC 
LIMIT 1;
```

### Find Recurring Errors
```sql
SELECT error_message, COUNT(*) as occurrences
FROM shq.orbt_error_log
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY error_message
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;
```

### Check Escalation Queue
```sql
SELECT * FROM shq.orbt_escalation_queue
WHERE status = 'PENDING'
ORDER BY priority DESC, escalated_at ASC;
```

### Analyze Agent Performance
```sql
SELECT agent_id, 
       AVG(execution_time_ms) as avg_time,
       COUNT(CASE WHEN success THEN 1 END)::FLOAT / COUNT(*) as success_rate
FROM shq.orbt_agent_metrics
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY agent_id
ORDER BY success_rate ASC;
```

---

## Monitoring Dashboard Metrics

### Real-Time Indicators
- System Status: GREEN/YELLOW/RED
- Active Agents: Count
- Pending Escalations: Count
- Error Rate: Errors per minute
- Success Rate: Percentage

### Historical Trends
- Error patterns over time
- Agent performance trends
- Resolution time averages
- Escalation frequency

### Pattern Analysis
- Most common errors
- Fastest growing error types
- Successfully auto-resolved patterns
- Human intervention requirements

---

## Best Practices

### Error Logging
1. **Be Specific:** Include exact error conditions
2. **Add Context:** Include relevant state/variables
3. **Use Consistent Types:** Stick to defined error_type values
4. **Include Stack Traces:** For debugging complex issues
5. **Link Related Errors:** Reference parent error_id if applicable

### Pattern Recognition
1. **Normalize Messages:** Strip timestamps/IDs for matching
2. **Track Confidence:** Update based on resolution success
3. **Version Solutions:** Track which fixes work best
4. **Share Knowledge:** Propagate patterns across projects

### Escalation Management
1. **Set Clear Priorities:** Use business impact for priority
2. **Include Context:** Full error history in escalations
3. **Track Resolution:** Document how issues were fixed
4. **Update Patterns:** Turn resolutions into knowledge

---

## Compliance Requirements

### Data Retention
- Error logs: 90 days minimum
- Training logs: Permanent
- Pattern library: Permanent
- Metrics: 30 days rolling

### Security
- No sensitive data in error messages
- Encrypt error_stack if contains secrets
- Audit all human escalations
- Role-based access to logs

### Performance
- Index all timestamp fields
- Partition large tables by date
- Archive old data to cold storage
- Monitor query performance

---

*This schema ensures complete error tracking and automated learning across the entire HEIR system, enabling the 3-strike ORBT protocol to achieve 95%+ automated resolution rates.*