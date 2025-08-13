# HEIR System Resolution Tracking & Knowledge Base
## Never Start From Scratch - Document Every Fix

---

## Overview
This system captures exactly how every error was resolved, creating an institutional knowledge base that gets smarter with each fix. No more starting from scratch - every solution becomes permanent organizational capability.

**Core Principle:** Every error resolution becomes institutional knowledge for instant future application.

---

## Enhanced Resolution Tracking Tables

### 1. Master Resolution Library (`shq.orbt_resolution_library`)
**Purpose:** Permanent knowledge base of proven fixes

```sql
CREATE TABLE shq.orbt_resolution_library (
    -- Primary Keys
    id SERIAL PRIMARY KEY,
    resolution_id VARCHAR(50) UNIQUE NOT NULL, -- RES-[timestamp]-[sequence]
    
    -- Error Identification
    error_signature VARCHAR(500) NOT NULL,     -- Normalized error pattern
    error_type VARCHAR(50) NOT NULL,
    error_code VARCHAR(20) NOT NULL,
    unique_id_pattern VARCHAR(50) NOT NULL,
    process_id VARCHAR(50) NOT NULL,
    
    -- Resolution Details (THE ACTUAL FIX)
    fix_title VARCHAR(200) NOT NULL,           -- "Restart Connection Pool"
    fix_description TEXT NOT NULL,             -- Detailed explanation
    fix_category VARCHAR(50) NOT NULL,         -- restart/config/code/scale/etc
    
    -- Step-by-Step Fix Instructions
    diagnostic_commands TEXT[] NOT NULL,       -- Commands to verify problem
    fix_commands TEXT[] NOT NULL,              -- Exact commands to fix
    verification_commands TEXT[] NOT NULL,     -- Commands to verify fix worked
    rollback_commands TEXT[] NOT NULL,         -- Commands to undo if needed
    
    -- Context & Environment
    affected_systems TEXT[] NOT NULL,          -- Which systems needed fix
    prerequisites TEXT[] NULL,                 -- What must be true to apply fix
    side_effects TEXT[] NULL,                  -- Potential impacts of fix
    environment_type VARCHAR(20) NOT NULL,     -- production/staging/development
    
    -- Who Fixed It & When
    fixed_by VARCHAR(100) NOT NULL,            -- human name or agent ID
    fixed_by_type VARCHAR(20) NOT NULL,        -- human/agent/automated
    original_error_id VARCHAR(50) NOT NULL,    -- Link to original error
    resolution_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Effectiveness Tracking
    resolution_time_minutes INTEGER NOT NULL,  -- How long fix took
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 100.0, -- % success when applied
    application_count INTEGER NOT NULL DEFAULT 1,      -- Times this fix used
    last_applied TIMESTAMPTZ NULL,             -- When last used
    
    -- Knowledge Enhancement
    lessons_learned TEXT NOT NULL,             -- Key insights from this fix
    improvement_suggestions TEXT NULL,         -- How to make fix better
    related_resolutions VARCHAR(50)[] NULL,    -- Similar fixes
    
    -- Documentation & References
    documentation_created TEXT[] NULL,         -- New docs created
    code_changes_required BOOLEAN DEFAULT FALSE,
    config_changes_required BOOLEAN DEFAULT FALSE,
    infrastructure_changes_required BOOLEAN DEFAULT FALSE,
    
    -- Validation & Quality
    peer_reviewed BOOLEAN DEFAULT FALSE,
    peer_reviewer VARCHAR(100) NULL,
    review_notes TEXT NULL,
    approved_for_automation BOOLEAN DEFAULT FALSE,
    automation_confidence DECIMAL(5,2) DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version VARCHAR(10) NOT NULL DEFAULT '1.0.0'
);
```

### 2. Resolution Application Log (`shq.orbt_resolution_applications`)
**Purpose:** Track every time a documented fix is used

```sql
CREATE TABLE shq.orbt_resolution_applications (
    -- Primary Keys
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Resolution Reference
    resolution_id VARCHAR(50) NOT NULL REFERENCES shq.orbt_resolution_library(resolution_id),
    applied_to_error_id VARCHAR(50) NOT NULL,
    
    -- Application Context
    applied_by VARCHAR(100) NOT NULL,           -- Who applied the fix
    applied_by_type VARCHAR(20) NOT NULL,       -- human/agent/automated
    application_method VARCHAR(50) NOT NULL,    -- manual/semi-auto/full-auto
    
    -- Execution Details
    steps_executed TEXT[] NOT NULL,             -- Which steps were run
    modifications_made TEXT[] NULL,             -- Any changes to standard fix
    execution_time_minutes INTEGER NOT NULL,
    
    -- Outcome Tracking
    fix_successful BOOLEAN NOT NULL,
    success_verification TEXT NOT NULL,         -- How success was confirmed
    partial_success BOOLEAN DEFAULT FALSE,      -- Worked partially
    side_effects_observed TEXT[] NULL,
    
    -- Learning Capture
    what_worked_well TEXT NOT NULL,
    what_could_improve TEXT NULL,
    new_insights TEXT NULL,
    environment_differences TEXT NULL,
    
    -- Follow-up Actions
    additional_fixes_needed BOOLEAN DEFAULT FALSE,
    monitoring_recommendations TEXT[] NULL,
    prevention_actions_taken TEXT[] NULL,
    
    -- Metadata
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3. Fix Evolution Tracking (`shq.orbt_fix_evolution`)
**Purpose:** Track how fixes improve over time

```sql
CREATE TABLE shq.orbt_fix_evolution (
    id SERIAL PRIMARY KEY,
    evolution_id VARCHAR(50) UNIQUE NOT NULL,
    
    base_resolution_id VARCHAR(50) NOT NULL,
    improved_resolution_id VARCHAR(50) NOT NULL,
    
    improvement_type VARCHAR(50) NOT NULL,      -- faster/safer/simpler/automated
    improvement_description TEXT NOT NULL,
    
    performance_improvement DECIMAL(5,2) NULL, -- % improvement in metrics
    risk_reduction TEXT NULL,
    automation_enhancement TEXT NULL,
    
    evolved_by VARCHAR(100) NOT NULL,
    evolution_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Resolution Documentation Workflow

### 1. Real-Time Fix Capture
```sql
-- Function to capture fix as it happens
CREATE OR REPLACE FUNCTION capture_resolution_start(
    p_error_id VARCHAR(50),
    p_fix_title VARCHAR(200),
    p_fixed_by VARCHAR(100),
    p_fixed_by_type VARCHAR(20)
) RETURNS VARCHAR(50) AS $$
DECLARE
    v_resolution_id VARCHAR(50);
    v_error_info RECORD;
BEGIN
    -- Generate resolution ID
    v_resolution_id := 'RES-' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '-' || 
                       LPAD(nextval('resolution_seq')::TEXT, 3, '0');
    
    -- Get error details
    SELECT error_type, error_message, error_id, agent_id 
    INTO v_error_info
    FROM shq.orbt_error_log 
    WHERE error_id = p_error_id;
    
    -- Create resolution record
    INSERT INTO shq.orbt_resolution_library (
        resolution_id, error_signature, error_type, 
        unique_id_pattern, fix_title, fix_description,
        fixed_by, fixed_by_type, original_error_id,
        diagnostic_commands, fix_commands, 
        verification_commands, rollback_commands,
        affected_systems, environment_type, lessons_learned
    ) VALUES (
        v_resolution_id,
        v_error_info.error_message,
        v_error_info.error_type,
        p_error_id,
        p_fix_title,
        'Fix in progress - will be updated with details',
        p_fixed_by,
        p_fixed_by_type,
        p_error_id,
        ARRAY[]::TEXT[], -- Will be populated as fix progresses
        ARRAY[]::TEXT[],
        ARRAY[]::TEXT[],
        ARRAY[]::TEXT[],
        ARRAY[v_error_info.agent_id],
        'production', -- Default
        'Fix in progress'
    );
    
    RETURN v_resolution_id;
END;
$$ LANGUAGE plpgsql;
```

### 2. Step-by-Step Documentation
```sql
-- Function to add fix steps as they're executed
CREATE OR REPLACE FUNCTION add_fix_step(
    p_resolution_id VARCHAR(50),
    p_step_type VARCHAR(20), -- diagnostic/fix/verification/rollback
    p_command TEXT,
    p_result TEXT,
    p_notes TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Add step to appropriate array
    UPDATE shq.orbt_resolution_library 
    SET 
        diagnostic_commands = CASE 
            WHEN p_step_type = 'diagnostic' THEN 
                array_append(diagnostic_commands, p_command || ' -- ' || p_result)
            ELSE diagnostic_commands 
        END,
        fix_commands = CASE 
            WHEN p_step_type = 'fix' THEN 
                array_append(fix_commands, p_command || ' -- ' || p_result)
            ELSE fix_commands 
        END,
        verification_commands = CASE 
            WHEN p_step_type = 'verification' THEN 
                array_append(verification_commands, p_command || ' -- ' || p_result)
            ELSE verification_commands 
        END,
        rollback_commands = CASE 
            WHEN p_step_type = 'rollback' THEN 
                array_append(rollback_commands, p_command || ' -- ' || p_result)
            ELSE rollback_commands 
        END,
        updated_at = NOW()
    WHERE resolution_id = p_resolution_id;
    
    -- Add detailed step log
    INSERT INTO resolution_step_log (
        resolution_id, step_type, command_executed, 
        result_observed, notes, timestamp
    ) VALUES (
        p_resolution_id, p_step_type, p_command, 
        p_result, p_notes, NOW()
    );
END;
$$ LANGUAGE plpgsql;
```

### 3. Resolution Completion
```sql
-- Function to finalize resolution documentation
CREATE OR REPLACE FUNCTION complete_resolution(
    p_resolution_id VARCHAR(50),
    p_resolution_time_minutes INTEGER,
    p_lessons_learned TEXT,
    p_success BOOLEAN DEFAULT TRUE,
    p_improvement_suggestions TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE shq.orbt_resolution_library 
    SET 
        resolution_time_minutes = p_resolution_time_minutes,
        lessons_learned = p_lessons_learned,
        improvement_suggestions = p_improvement_suggestions,
        fix_description = CASE 
            WHEN p_success THEN 'Successfully resolved - see commands for details'
            ELSE 'Resolution attempted but not fully successful'
        END,
        success_rate = CASE WHEN p_success THEN 100.0 ELSE 0.0 END,
        updated_at = NOW()
    WHERE resolution_id = p_resolution_id;
    
    -- Mark original error as resolved if successful
    IF p_success THEN
        UPDATE shq.orbt_error_log 
        SET 
            resolved = TRUE,
            resolved_timestamp = NOW(),
            resolution_method = 'documented_fix'
        WHERE error_id = (
            SELECT original_error_id 
            FROM shq.orbt_resolution_library 
            WHERE resolution_id = p_resolution_id
        );
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## Intelligent Fix Recommendation System

### 1. Find Similar Fixes
```sql
-- Function to find applicable fixes for new errors
CREATE OR REPLACE FUNCTION find_applicable_fixes(
    p_error_message TEXT,
    p_error_type VARCHAR(50),
    p_agent_id VARCHAR(100) DEFAULT NULL
) RETURNS TABLE(
    resolution_id VARCHAR(50),
    fix_title VARCHAR(200),
    success_rate DECIMAL(5,2),
    last_used TIMESTAMPTZ,
    confidence_score DECIMAL(5,2),
    fix_commands TEXT[],
    estimated_time INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.resolution_id,
        r.fix_title,
        r.success_rate,
        r.last_applied,
        -- Calculate confidence based on similarity and success rate
        (
            CASE 
                WHEN similarity(r.error_signature, p_error_message) > 0.8 THEN 90.0
                WHEN similarity(r.error_signature, p_error_message) > 0.6 THEN 70.0
                WHEN r.error_type = p_error_type THEN 50.0
                ELSE 20.0
            END * (r.success_rate / 100.0)
        ) as confidence_score,
        r.fix_commands,
        r.resolution_time_minutes
    FROM shq.orbt_resolution_library r
    WHERE 
        (similarity(r.error_signature, p_error_message) > 0.5 OR r.error_type = p_error_type)
        AND r.success_rate > 50.0
        AND r.approved_for_automation = TRUE
    ORDER BY confidence_score DESC, r.success_rate DESC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;
```

### 2. Apply Documented Fix
```sql
-- Function to apply a known fix
CREATE OR REPLACE FUNCTION apply_documented_fix(
    p_error_id VARCHAR(50),
    p_resolution_id VARCHAR(50),
    p_applied_by VARCHAR(100),
    p_applied_by_type VARCHAR(20)
) RETURNS VARCHAR(50) AS $$
DECLARE
    v_application_id VARCHAR(50);
    v_fix_record RECORD;
    v_start_time TIMESTAMPTZ := NOW();
BEGIN
    -- Get fix details
    SELECT * INTO v_fix_record
    FROM shq.orbt_resolution_library
    WHERE resolution_id = p_resolution_id;
    
    -- Generate application ID
    v_application_id := 'APP-' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '-' || 
                        LPAD(nextval('application_seq')::TEXT, 3, '0');
    
    -- Create application record
    INSERT INTO shq.orbt_resolution_applications (
        application_id, resolution_id, applied_to_error_id,
        applied_by, applied_by_type, application_method,
        steps_executed, execution_time_minutes,
        fix_successful, success_verification,
        what_worked_well, applied_at
    ) VALUES (
        v_application_id, p_resolution_id, p_error_id,
        p_applied_by, p_applied_by_type, 'automated',
        v_fix_record.fix_commands, 0, -- Will be updated
        FALSE, 'Pending verification',
        'Application initiated', NOW()
    );
    
    -- Update resolution usage stats
    UPDATE shq.orbt_resolution_library 
    SET 
        application_count = application_count + 1,
        last_applied = NOW()
    WHERE resolution_id = p_resolution_id;
    
    RETURN v_application_id;
END;
$$ LANGUAGE plpgsql;
```

---

## Usage Examples

### 1. Human Fixing Error (Real-Time Documentation)
```python
# Human starts fixing error
resolution_id = capture_resolution_start(
    error_id='01.03.001.API.20000.005',
    fix_title='Restart Connection Pool for Database Timeout',
    fixed_by='john.doe@company.com',
    fixed_by_type='human'
)

# Document each step as it's performed
add_fix_step(
    resolution_id, 
    'diagnostic', 
    'SELECT count(*) FROM pg_stat_activity',
    '150 connections (pool limit 100)'
)

add_fix_step(
    resolution_id,
    'fix',
    'sudo systemctl restart pgbouncer',
    'Service restarted successfully'
)

add_fix_step(
    resolution_id,
    'verification',
    'curl -f https://api.company.com/health',
    'HTTP 200 OK - API responding normally'
)

# Complete documentation
complete_resolution(
    resolution_id,
    resolution_time_minutes=8,
    lessons_learned='Connection pool was exhausted due to long-running queries. Restarting pool immediately resolved issue. Should implement query timeout monitoring.',
    success=True,
    improvement_suggestions='Add automated pool restart when utilization > 95%'
)
```

### 2. AI Agent Applying Known Fix
```python
# AI encounters similar error
error_id = '01.03.002.API.20000.012'
error_message = 'Database connection timeout after 30 seconds'

# Find applicable fixes
fixes = find_applicable_fixes(error_message, 'connection')

if fixes and fixes[0].confidence_score > 80:
    # Apply documented fix
    application_id = apply_documented_fix(
        error_id,
        fixes[0].resolution_id,
        'database-specialist-agent',
        'agent'
    )
    
    # Execute fix commands
    for command in fixes[0].fix_commands:
        result = execute_command(command)
        log_step_execution(application_id, command, result)
    
    # Update application record with outcome
    update_application_success(application_id, True, 'Fix applied successfully using documented procedure')
```

### 3. Dashboard View of Knowledge Base
```sql
-- Show resolution effectiveness dashboard
SELECT 
    r.fix_title,
    r.error_type,
    r.success_rate,
    r.application_count,
    r.resolution_time_minutes as avg_fix_time,
    COUNT(a.application_id) as times_reused,
    AVG(a.execution_time_minutes) as avg_reuse_time,
    r.last_applied
FROM shq.orbt_resolution_library r
LEFT JOIN shq.orbt_resolution_applications a ON r.resolution_id = a.resolution_id
WHERE r.success_rate > 70
GROUP BY r.resolution_id, r.fix_title, r.error_type, 
         r.success_rate, r.application_count, r.resolution_time_minutes, r.last_applied
ORDER BY r.application_count DESC, r.success_rate DESC;
```

---

## Knowledge Evolution Features

### 1. Fix Improvement Tracking
- **Performance Optimization:** Track when fixes get faster
- **Risk Reduction:** Document safety improvements
- **Automation Enhancement:** Progress from manual to automated
- **Simplification:** Evolution toward simpler solutions

### 2. Pattern Recognition
- **Error Clustering:** Group similar errors together
- **Fix Families:** Related fixes for related problems
- **Success Prediction:** Predict fix success before applying
- **Context Matching:** Match fixes to specific environments

### 3. Quality Assurance
- **Peer Review:** Human validation of documented fixes
- **Success Verification:** Confirm fixes work in practice
- **Automation Approval:** Validate fixes safe for automation
- **Continuous Testing:** Regular validation of documented procedures

---

## Benefits

### For Immediate Problem Solving
- **No Starting From Scratch:** Every error has documented resolution path
- **Proven Solutions:** Only apply fixes with verified success rates
- **Time Savings:** Average resolution time drops with each application
- **Quality Assurance:** Documented steps reduce human error

### For Institutional Learning
- **Permanent Knowledge:** Fixes are never lost when people leave
- **Continuous Improvement:** Each application makes fixes better
- **Pattern Recognition:** System learns what works in what contexts
- **Automation Evolution:** Manual fixes become automated over time

### For Team Development
- **Knowledge Sharing:** Junior team members can apply senior-level fixes
- **Best Practice Capture:** Expertise becomes organizational asset
- **Training Materials:** Real fixes become training examples
- **Competency Building:** Team capabilities compound over time

---

*This resolution tracking system ensures that every fix becomes permanent organizational intelligence, transforming reactive troubleshooting into proactive knowledge application.*