# HEIR Granular Doctrine System
## Process-Level Behavioral Control by Subhive

---

## Overview
Each subhive operates under its own doctrine section, and within each subhive, individual processes have specific behavioral rules. This creates a hierarchical doctrine system that mirrors the HEIR agent structure.

**Granular Control:** Subhive → Process → Step-Level Doctrine Compliance

---

## Doctrine Hierarchy Structure

### **Level 1: Subhive Doctrine (10 Main Sections)**
```
01 = SHQ (System Headquarters) - Master coordination doctrine
02 = CLNT (Client Management) - Customer interaction rules
03 = DATA (Data Operations) - Information handling procedures
04 = PAY (Payment Processing) - Financial transaction rules
05 = INT (Integration Services) - External system protocols
06 = PLAT (Platform Infrastructure) - System operation standards
07 = MON (Monitoring & Analytics) - Observation and reporting rules
08 = SEC (Security & Compliance) - Protection and audit requirements
09 = COMM (Communication Systems) - Messaging and notification rules
10 = AI (Artificial Intelligence) - AI decision-making guidelines
```

### **Level 2: Process Doctrine (Within Each Subhive)**
```
Example for 04 (PAY - Payment Processing):
├── 04.001 = ProcessPayment
├── 04.002 = ValidateCard
├── 04.003 = HandleDecline
├── 04.004 = ProcessRefund
├── 04.005 = ManageSubscription
├── 04.006 = FraudDetection
└── 04.XXX = (Additional payment processes)
```

### **Level 3: Step-Level Doctrine (Within Each Process)**
```
Example for 04.001 (ProcessPayment):
├── 04.001.001 = ValidateAmount
├── 04.001.002 = CheckCardDetails
├── 04.001.003 = AuthorizeTransaction
├── 04.001.004 = HandleResponse
└── 04.001.XXX = (Additional steps)
```

---

## Granular Doctrine Database Schema

### 1. Enhanced Doctrine Reference Table
```sql
-- Replaces the simple doctrine integration - now hierarchical
CREATE TABLE IF NOT EXISTS shq.orbt_doctrine_hierarchy (
    id SERIAL PRIMARY KEY,
    doctrine_id VARCHAR(50) UNIQUE NOT NULL, -- Matches unique_id format
    
    -- Hierarchical Structure
    subhive_code VARCHAR(2) NOT NULL,        -- 01-10
    process_code VARCHAR(3) NULL,            -- 001-999 (NULL for subhive-level)
    step_code VARCHAR(3) NULL,               -- 001-999 (NULL for process-level)
    
    -- Doctrine Content
    doctrine_title VARCHAR(200) NOT NULL,
    doctrine_content TEXT NOT NULL,
    behavioral_rules TEXT[] NOT NULL,        -- Array of specific rules
    decision_criteria TEXT[] NOT NULL,       -- When this doctrine applies
    escalation_triggers TEXT[] NOT NULL,     -- When to escalate up hierarchy
    
    -- Enforcement Level
    enforcement_level VARCHAR(20) NOT NULL CHECK (enforcement_level IN ('MANDATORY', 'RECOMMENDED', 'INFORMATIONAL')),
    violation_consequences VARCHAR(100) NULL, -- What happens if violated
    
    -- Context & Conditions
    applicable_conditions TEXT[] NULL,       -- When this applies
    exceptions_allowed TEXT[] NULL,          -- Documented exceptions
    requires_approval BOOLEAN DEFAULT FALSE, -- Needs human approval
    
    -- References to DPR Doctrine
    dpr_doctrine_section VARCHAR(100) NULL,  -- Link to original dpr_doctrine table
    dpr_doctrine_version VARCHAR(10) NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_referenced TIMESTAMPTZ NULL,
    reference_count INTEGER DEFAULT 0
);
```

### 2. Process-Specific Doctrine Lookup
```sql
-- Function to get doctrine for specific process/step
CREATE OR REPLACE FUNCTION shq.get_process_doctrine(
    p_unique_id VARCHAR(50),              -- Full unique ID or pattern
    p_decision_context TEXT DEFAULT NULL
) RETURNS TABLE(
    doctrine_level VARCHAR(20),           -- SUBHIVE, PROCESS, STEP
    doctrine_title VARCHAR(200),
    behavioral_rules TEXT[],
    decision_criteria TEXT[],
    enforcement_level VARCHAR(20),
    escalation_required BOOLEAN,
    approval_required BOOLEAN,
    applicable_rules TEXT[]
) AS $$
DECLARE
    v_subhive VARCHAR(2);
    v_process VARCHAR(3);
    v_step VARCHAR(3);
BEGIN
    -- Parse unique ID components
    SELECT 
        SPLIT_PART(p_unique_id, '.', 2),
        SPLIT_PART(p_unique_id, '.', 3), 
        SPLIT_PART(p_unique_id, '.', 6)
    INTO v_subhive, v_process, v_step;
    
    -- Return hierarchical doctrine (most specific first)
    RETURN QUERY
    WITH doctrine_hierarchy AS (
        -- Step-level doctrine (most specific)
        SELECT 'STEP' as doctrine_level, d.*
        FROM shq.orbt_doctrine_hierarchy d
        WHERE d.subhive_code = v_subhive 
        AND d.process_code = v_process 
        AND d.step_code = v_step
        
        UNION ALL
        
        -- Process-level doctrine
        SELECT 'PROCESS' as doctrine_level, d.*
        FROM shq.orbt_doctrine_hierarchy d
        WHERE d.subhive_code = v_subhive 
        AND d.process_code = v_process 
        AND d.step_code IS NULL
        
        UNION ALL
        
        -- Subhive-level doctrine (most general)
        SELECT 'SUBHIVE' as doctrine_level, d.*
        FROM shq.orbt_doctrine_hierarchy d
        WHERE d.subhive_code = v_subhive 
        AND d.process_code IS NULL 
        AND d.step_code IS NULL
    )
    SELECT 
        dh.doctrine_level,
        dh.doctrine_title,
        dh.behavioral_rules,
        dh.decision_criteria,
        dh.enforcement_level,
        -- Check if escalation required
        (array_length(dh.escalation_triggers, 1) > 0 AND 
         (p_decision_context IS NULL OR 
          EXISTS(SELECT 1 FROM unnest(dh.escalation_triggers) as trigger 
                 WHERE p_decision_context ILIKE '%' || trigger || '%'))) as escalation_required,
        dh.requires_approval,
        -- Filter applicable rules based on context
        CASE 
            WHEN p_decision_context IS NOT NULL THEN
                array(SELECT rule FROM unnest(dh.behavioral_rules) as rule 
                      WHERE p_decision_context ILIKE '%' || rule || '%')
            ELSE dh.behavioral_rules
        END as applicable_rules
    FROM doctrine_hierarchy dh
    ORDER BY 
        CASE dh.doctrine_level 
            WHEN 'STEP' THEN 1 
            WHEN 'PROCESS' THEN 2 
            WHEN 'SUBHIVE' THEN 3 
        END;
        
    -- Update reference tracking
    UPDATE shq.orbt_doctrine_hierarchy 
    SET reference_count = reference_count + 1,
        last_referenced = NOW()
    WHERE subhive_code = v_subhive;
END;
$$ LANGUAGE plpgsql;
```

### 3. Doctrine Compliance Validation
```sql
-- Validate specific action against hierarchical doctrine
CREATE OR REPLACE FUNCTION shq.validate_action_compliance(
    p_unique_id VARCHAR(50),
    p_agent_id VARCHAR(100),
    p_proposed_action TEXT,
    p_action_context TEXT
) RETURNS TABLE(
    compliance_level VARCHAR(20),         -- FULL, PARTIAL, VIOLATION, UNCLEAR
    violated_rules TEXT[],
    required_approvals TEXT[],
    escalation_required BOOLEAN,
    recommended_actions TEXT[],
    doctrine_sources TEXT[]               -- Which doctrine sections were checked
) AS $$
DECLARE
    v_doctrine_record RECORD;
    v_violations TEXT[] := ARRAY[]::TEXT[];
    v_approvals TEXT[] := ARRAY[]::TEXT[];
    v_escalation BOOLEAN := FALSE;
    v_recommendations TEXT[] := ARRAY[]::TEXT[];
    v_sources TEXT[] := ARRAY[]::TEXT[];
BEGIN
    -- Check all applicable doctrine levels
    FOR v_doctrine_record IN 
        SELECT * FROM shq.get_process_doctrine(p_unique_id, p_action_context)
    LOOP
        v_sources := array_append(v_sources, v_doctrine_record.doctrine_level || ':' || v_doctrine_record.doctrine_title);
        
        -- Check for rule violations
        IF array_length(v_doctrine_record.applicable_rules, 1) > 0 THEN
            -- Look for prohibitive rules
            DECLARE
                rule TEXT;
            BEGIN
                FOREACH rule IN ARRAY v_doctrine_record.applicable_rules
                LOOP
                    IF rule ILIKE 'must not%' AND p_proposed_action ILIKE '%' || SUBSTRING(rule FROM 'must not (.*)') || '%' THEN
                        v_violations := array_append(v_violations, 'Violates: ' || rule);
                    END IF;
                    
                    IF rule ILIKE 'requires%' AND p_proposed_action NOT ILIKE '%' || SUBSTRING(rule FROM 'requires (.*)') || '%' THEN
                        v_violations := array_append(v_violations, 'Missing requirement: ' || rule);
                    END IF;
                END LOOP;
            END;
        END IF;
        
        -- Check approval requirements
        IF v_doctrine_record.approval_required THEN
            v_approvals := array_append(v_approvals, v_doctrine_record.doctrine_title || ' requires approval');
        END IF;
        
        -- Check escalation requirements
        IF v_doctrine_record.escalation_required THEN
            v_escalation := TRUE;
        END IF;
        
        -- Add recommendations
        IF v_doctrine_record.enforcement_level = 'RECOMMENDED' THEN
            v_recommendations := array_append(v_recommendations, 'Consider: ' || array_to_string(v_doctrine_record.behavioral_rules, ', '));
        END IF;
    END LOOP;
    
    -- Determine overall compliance
    RETURN QUERY
    SELECT 
        CASE 
            WHEN array_length(v_violations, 1) > 0 THEN 'VIOLATION'
            WHEN array_length(v_approvals, 1) > 0 THEN 'PARTIAL'
            WHEN array_length(v_sources, 1) = 0 THEN 'UNCLEAR'
            ELSE 'FULL'
        END as compliance_level,
        v_violations,
        v_approvals,
        v_escalation,
        v_recommendations,
        v_sources;
END;
$$ LANGUAGE plpgsql;
```

---

## Subhive-Specific Doctrine Examples

### 1. Payment Processing Subhive (04) Doctrine
```sql
-- Subhive-level payment doctrine
INSERT INTO shq.orbt_doctrine_hierarchy (
    doctrine_id, subhive_code, doctrine_title, doctrine_content,
    behavioral_rules, decision_criteria, escalation_triggers, enforcement_level
) VALUES (
    '04.000.000', '04', 
    'Payment Processing General Doctrine',
    'All payment operations must follow PCI compliance and fraud prevention protocols',
    ARRAY[
        'must validate all payment amounts before processing',
        'must log all payment attempts for audit',
        'must not store raw credit card data',
        'requires two-factor authentication for refunds over $500'
    ],
    ARRAY[
        'any payment operation',
        'financial transaction processing',
        'customer billing activity'
    ],
    ARRAY[
        'fraud detection triggered',
        'amount over $1000',
        'international transaction'
    ],
    'MANDATORY'
);

-- Process-level: Specific payment processing
INSERT INTO shq.orbt_doctrine_hierarchy (
    doctrine_id, subhive_code, process_code, doctrine_title, doctrine_content,
    behavioral_rules, decision_criteria, escalation_triggers, enforcement_level
) VALUES (
    '04.001.000', '04', '001',
    'ProcessPayment Specific Rules',
    'Direct payment processing workflow requirements',
    ARRAY[
        'must retry failed payments maximum 3 times',
        'must wait 30 seconds between retry attempts',
        'must notify customer of payment status within 60 seconds',
        'requires manager approval for manual payment processing'
    ],
    ARRAY[
        'processing customer payment',
        'charging credit card',
        'handling payment gateway response'
    ],
    ARRAY[
        'payment gateway unavailable',
        '3 consecutive failures',
        'customer disputes charge'
    ],
    'MANDATORY'
);

-- Step-level: Card validation step
INSERT INTO shq.orbt_doctrine_hierarchy (
    doctrine_id, subhive_code, process_code, step_code, doctrine_title, doctrine_content,
    behavioral_rules, decision_criteria, escalation_triggers, enforcement_level
) VALUES (
    '04.001.002', '04', '001', '002',
    'Card Validation Step Requirements',
    'Specific rules for validating payment card details',
    ARRAY[
        'must validate card number using Luhn algorithm',
        'must check expiration date is future',
        'must validate CVV is 3-4 digits',
        'must not accept cards from blocked countries list'
    ],
    ARRAY[
        'validating credit card information',
        'processing card details',
        'checking card validity'
    ],
    ARRAY[
        'card fails validation',
        'suspicious card pattern detected',
        'card from high-risk country'
    ],
    'MANDATORY'
);
```

### 2. Data Operations Subhive (03) Doctrine
```sql
-- Subhive-level data doctrine
INSERT INTO shq.orbt_doctrine_hierarchy (
    doctrine_id, subhive_code, doctrine_title, doctrine_content,
    behavioral_rules, decision_criteria, escalation_triggers, enforcement_level
) VALUES (
    '03.000.000', '03',
    'Data Operations Security Doctrine',
    'All data operations must maintain confidentiality, integrity, and availability',
    ARRAY[
        'must encrypt all data at rest and in transit',
        'must implement row-level security for sensitive data',
        'must audit all data access attempts',
        'must not expose PII in logs or error messages',
        'requires backup verification before destructive operations'
    ],
    ARRAY[
        'any database operation',
        'data processing activity',
        'information storage or retrieval'
    ],
    ARRAY[
        'accessing customer PII',
        'bulk data operations',
        'cross-database queries',
        'data export requests'
    ],
    'MANDATORY'
);

-- Process-level: Database connection management
INSERT INTO shq.orbt_doctrine_hierarchy (
    doctrine_id, subhive_code, process_code, doctrine_title, doctrine_content,
    behavioral_rules, decision_criteria, escalation_triggers, enforcement_level
) VALUES (
    '03.001.000', '03', '001',
    'Database Connection Management',
    'Rules for establishing and maintaining database connections',
    ARRAY[
        'must use connection pooling for all database access',
        'must implement circuit breaker pattern for connection failures',
        'must timeout connections after 30 seconds',
        'must retry connections maximum 3 times with exponential backoff',
        'requires DBA approval for new database connections'
    ],
    ARRAY[
        'connecting to database',
        'managing connection pools',
        'handling connection failures'
    ],
    ARRAY[
        'connection pool exhausted',
        'database unavailable for 5+ minutes',
        'suspicious connection patterns'
    ],
    'MANDATORY'
);
```

---

## Agent Integration with Granular Doctrine

### 1. Enhanced Agent Decision Workflow
```python
class PaymentSpecialistAgent:
    def process_payment(self, payment_request):
        # Get step-specific doctrine for this exact operation
        unique_id = self.generate_unique_id('04', '001', '002')  # Card validation step
        
        doctrine = self.get_process_doctrine(unique_id, 'card validation')
        
        # Check if action is compliant before executing
        proposed_action = f"validate card {payment_request.card_number[:4]}****"
        compliance = self.validate_action_compliance(
            unique_id=unique_id,
            proposed_action=proposed_action,
            context='customer payment processing'
        )
        
        if compliance['compliance_level'] == 'VIOLATION':
            self.log_doctrine_violation(compliance['violated_rules'])
            return self.escalate_to_orchestrator(payment_request, compliance)
        
        elif compliance['compliance_level'] == 'PARTIAL':
            # Requires approval
            return self.request_human_approval(payment_request, compliance)
        
        else:
            # Proceed with doctrine-compliant processing
            return self.execute_payment_processing(payment_request, doctrine)

    def get_process_doctrine(self, unique_id, context):
        query = """
        SELECT * FROM shq.get_process_doctrine(%s, %s)
        ORDER BY CASE doctrine_level 
            WHEN 'STEP' THEN 1 
            WHEN 'PROCESS' THEN 2 
            WHEN 'SUBHIVE' THEN 3 
        END
        """
        return db.execute(query, [unique_id, context])
```

### 2. Real-time Doctrine Monitoring Dashboard
```sql
-- Dashboard showing doctrine compliance by subhive and process
CREATE VIEW shq.doctrine_compliance_metrics AS
SELECT 
    d.subhive_code,
    d.process_code,
    d.doctrine_title,
    d.reference_count,
    d.last_referenced,
    COUNT(di.id) as consultations_24h,
    COUNT(CASE WHEN di.doctrine_compliance = 'COMPLIANT' THEN 1 END) as compliant_decisions,
    COUNT(CASE WHEN di.doctrine_compliance = 'EXCEPTION' THEN 1 END) as violations,
    COUNT(CASE WHEN di.human_review_required THEN 1 END) as requiring_review,
    AVG(di.confidence_score) as avg_confidence
FROM shq.orbt_doctrine_hierarchy d
LEFT JOIN shq.orbt_doctrine_integration di ON di.doctrine_section = d.doctrine_id
    AND di.consulted_at > NOW() - INTERVAL '24 hours'
GROUP BY d.subhive_code, d.process_code, d.doctrine_title, d.reference_count, d.last_referenced
ORDER BY d.subhive_code, d.process_code NULLS FIRST;
```

---

## Benefits of Granular Doctrine System

### For System Operations
- **Process-specific compliance** ensures precise behavioral control
- **Hierarchical escalation** from step → process → subhive → human
- **Granular audit trail** shows exactly which doctrine was consulted
- **Automated compliance checking** at every decision point

### For Business Governance  
- **Precise policy enforcement** down to individual process steps
- **Clear accountability** for doctrine violations
- **Systematic compliance reporting** by subhive and process
- **Controlled exception handling** with documented approvals

### For Agent Intelligence
- **Context-aware behavior** based on specific operation being performed
- **Intelligent escalation** only when doctrine requires it
- **Learning from violations** to improve future compliance
- **Consistent decision-making** across all agents in same subhive/process

---

*This granular system ensures every agent decision is doctrine-compliant at the appropriate level of specificity, from high-level subhive policies down to individual process step requirements.*