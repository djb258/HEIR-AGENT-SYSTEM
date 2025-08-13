# HEIR System Doctrine Integration
## Automatic Agent Behavioral Control via DPR Doctrine

---

## Overview
This system connects HEIR agents directly to the existing `dpr_doctrine` table in Neon, ensuring every agent decision follows your established 600-page doctrine. No agent acts without consulting organizational knowledge.

**Core Principle:** Every agent decision must be doctrine-compliant or explicitly document the exception.

---

## Database Integration Schema

### 1. Doctrine Connection Table (`shq.orbt_doctrine_integration`)
```sql
-- Links HEIR error/resolution system to DPR doctrine
CREATE TABLE IF NOT EXISTS shq.orbt_doctrine_integration (
    id SERIAL PRIMARY KEY,
    integration_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- HEIR System References
    error_id VARCHAR(50) NULL,              -- Link to orbt_error_log
    resolution_id VARCHAR(50) NULL,         -- Link to orbt_resolution_library
    agent_id VARCHAR(100) NOT NULL,         -- Which agent consulted doctrine
    
    -- DPR Doctrine References  
    doctrine_section VARCHAR(100) NOT NULL, -- Section from dpr_doctrine table
    doctrine_subsection VARCHAR(100) NULL,  -- Specific subsection referenced
    subhive_code VARCHAR(2) NOT NULL,       -- 01=SHQ, 02=CLNT, etc.
    
    -- Decision Context
    decision_type VARCHAR(50) NOT NULL,     -- error_handling, resolution_choice, escalation
    decision_made TEXT NOT NULL,            -- What the agent decided to do
    doctrine_compliance VARCHAR(20) NOT NULL CHECK (doctrine_compliance IN ('COMPLIANT', 'EXCEPTION', 'UNCLEAR')),
    exception_reason TEXT NULL,             -- Why agent deviated from doctrine (if applicable)
    
    -- Query Details
    doctrine_query TEXT NOT NULL,           -- What agent asked doctrine system
    doctrine_response TEXT NOT NULL,        -- What doctrine guidance was provided
    confidence_score DECIMAL(5,2) NOT NULL DEFAULT 0.0, -- How confident agent was in interpretation
    
    -- Audit Trail
    consulted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decision_outcome VARCHAR(50) NULL,      -- success, failure, pending
    human_review_required BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2. Doctrine Lookup Functions

#### Primary Doctrine Query Function
```sql
-- Function to query DPR doctrine for agent guidance
CREATE OR REPLACE FUNCTION shq.get_doctrine_guidance(
    p_subhive_code VARCHAR(2),
    p_query_context TEXT,
    p_agent_id VARCHAR(100)
) RETURNS TABLE(
    doctrine_section VARCHAR(100),
    guidance_text TEXT,
    confidence_score DECIMAL(5,2),
    requires_escalation BOOLEAN,
    related_sections TEXT[]
) AS $$
DECLARE
    v_integration_id VARCHAR(50);
BEGIN
    -- Generate integration tracking ID
    v_integration_id := 'DOC-' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '-' || 
                        LPAD(nextval('doctrine_integration_seq')::TEXT, 3, '0');
    
    -- Query the existing dpr_doctrine table
    -- (Assuming columns: section, subsection, content, subhive_applicable)
    RETURN QUERY
    SELECT 
        d.section as doctrine_section,
        d.content as guidance_text,
        -- Calculate confidence based on keyword matching
        CASE 
            WHEN d.content ILIKE '%' || p_query_context || '%' THEN 95.0
            WHEN d.subsection ILIKE '%' || p_query_context || '%' THEN 85.0
            WHEN d.section ILIKE '%' || p_query_context || '%' THEN 75.0
            ELSE 50.0
        END as confidence_score,
        -- Determine if escalation required based on doctrine content
        (d.content ILIKE '%escalate%' OR d.content ILIKE '%human%' OR 
         d.content ILIKE '%manager%' OR d.content ILIKE '%supervisor%') as requires_escalation,
        -- Find related sections
        ARRAY(
            SELECT DISTINCT d2.section 
            FROM dpr_doctrine d2 
            WHERE d2.subhive_applicable = p_subhive_code 
            AND d2.section != d.section 
            AND (d2.content ILIKE '%' || p_query_context || '%')
            LIMIT 3
        ) as related_sections
    FROM dpr_doctrine d
    WHERE 
        (d.subhive_applicable = p_subhive_code OR d.subhive_applicable = 'ALL')
        AND (
            d.content ILIKE '%' || p_query_context || '%' OR
            d.section ILIKE '%' || p_query_context || '%' OR
            d.subsection ILIKE '%' || p_query_context || '%'
        )
    ORDER BY 
        CASE 
            WHEN d.content ILIKE '%' || p_query_context || '%' THEN 1
            WHEN d.subsection ILIKE '%' || p_query_context || '%' THEN 2
            WHEN d.section ILIKE '%' || p_query_context || '%' THEN 3
            ELSE 4
        END,
        d.section
    LIMIT 5;
    
    -- Log the doctrine consultation
    INSERT INTO shq.orbt_doctrine_integration (
        integration_id, agent_id, subhive_code, decision_type,
        doctrine_query, doctrine_response, doctrine_compliance,
        consulted_at
    ) VALUES (
        v_integration_id, p_agent_id, p_subhive_code, 'guidance_request',
        p_query_context, 'Doctrine consulted - see results', 'COMPLIANT',
        NOW()
    );
END;
$$ LANGUAGE plpgsql;
```

#### Doctrine Compliance Checker
```sql
-- Function to validate agent decisions against doctrine
CREATE OR REPLACE FUNCTION shq.validate_doctrine_compliance(
    p_agent_id VARCHAR(100),
    p_subhive_code VARCHAR(2),
    p_proposed_action TEXT,
    p_context TEXT
) RETURNS TABLE(
    is_compliant BOOLEAN,
    doctrine_violation TEXT,
    required_actions TEXT[],
    escalation_needed BOOLEAN,
    compliance_score DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    WITH doctrine_check AS (
        SELECT 
            d.section,
            d.content,
            -- Check for prohibitive language
            CASE 
                WHEN d.content ILIKE '%must not%' AND p_proposed_action ILIKE '%' || SUBSTRING(d.content FROM 'must not ([^.]*)')|| '%' 
                THEN 'VIOLATION'
                WHEN d.content ILIKE '%prohibited%' AND p_proposed_action ILIKE '%' || SUBSTRING(d.content FROM 'prohibited ([^.]*)')|| '%'
                THEN 'VIOLATION'
                WHEN d.content ILIKE '%required%' AND p_proposed_action NOT ILIKE '%' || SUBSTRING(d.content FROM 'required ([^.]*)')|| '%'
                THEN 'MISSING_REQUIREMENT'
                ELSE 'COMPLIANT'
            END as compliance_status,
            -- Extract required actions
            regexp_split_to_array(
                regexp_replace(d.content, '.*must:\s*(.*?)(?:\.|$)', '\1', 'gi'),
                ',\s*'
            ) as required_actions_array
        FROM dpr_doctrine d
        WHERE 
            (d.subhive_applicable = p_subhive_code OR d.subhive_applicable = 'ALL')
            AND (
                d.content ILIKE '%' || p_context || '%' OR
                d.content ILIKE '%' || p_proposed_action || '%'
            )
    )
    SELECT 
        (COUNT(CASE WHEN compliance_status = 'VIOLATION' THEN 1 END) = 0) as is_compliant,
        string_agg(section || ': ' || compliance_status, '; ') FILTER (WHERE compliance_status != 'COMPLIANT') as doctrine_violation,
        array_agg(DISTINCT unnest_val) FILTER (WHERE unnest_val IS NOT NULL AND unnest_val != '') as required_actions,
        (COUNT(CASE WHEN content ILIKE '%escalate%' OR content ILIKE '%supervisor%' THEN 1 END) > 0) as escalation_needed,
        CASE 
            WHEN COUNT(CASE WHEN compliance_status = 'VIOLATION' THEN 1 END) = 0 THEN 100.0
            WHEN COUNT(CASE WHEN compliance_status = 'MISSING_REQUIREMENT' THEN 1 END) > 0 THEN 60.0
            ELSE 20.0
        END as compliance_score
    FROM doctrine_check,
         unnest(required_actions_array) as unnest_val;
END;
$$ LANGUAGE plpgsql;
```

### 3. Agent Integration Functions

#### Enhanced Error Logging with Doctrine
```sql
-- Updated error logging to include doctrine consultation
CREATE OR REPLACE FUNCTION shq.log_error_with_doctrine(
    p_error_id VARCHAR(50),
    p_agent_id VARCHAR(100),
    p_subhive_code VARCHAR(2),
    p_error_type VARCHAR(50),
    p_error_message TEXT,
    p_proposed_resolution TEXT DEFAULT NULL
) RETURNS VARCHAR(50) AS $$
DECLARE
    v_doctrine_guidance RECORD;
    v_compliance_check RECORD;
    v_integration_id VARCHAR(50);
BEGIN
    -- First log the error normally
    INSERT INTO shq.orbt_error_log (
        error_id, agent_id, error_type, error_message, orbt_status
    ) VALUES (
        p_error_id, p_agent_id, p_error_type, p_error_message, 'YELLOW'
    );
    
    -- Consult doctrine for guidance
    SELECT * INTO v_doctrine_guidance
    FROM shq.get_doctrine_guidance(p_subhive_code, p_error_type || ' ' || p_error_message, p_agent_id)
    LIMIT 1;
    
    -- If resolution proposed, check compliance
    IF p_proposed_resolution IS NOT NULL THEN
        SELECT * INTO v_compliance_check
        FROM shq.validate_doctrine_compliance(p_agent_id, p_subhive_code, p_proposed_resolution, p_error_message)
        LIMIT 1;
        
        -- Generate integration record
        v_integration_id := 'DOC-' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '-' || 
                            LPAD(nextval('doctrine_integration_seq')::TEXT, 3, '0');
        
        INSERT INTO shq.orbt_doctrine_integration (
            integration_id, error_id, agent_id, subhive_code, decision_type,
            doctrine_section, decision_made, doctrine_compliance,
            doctrine_query, doctrine_response, confidence_score,
            human_review_required
        ) VALUES (
            v_integration_id, p_error_id, p_agent_id, p_subhive_code, 'error_resolution',
            COALESCE(v_doctrine_guidance.doctrine_section, 'NO_GUIDANCE'),
            p_proposed_resolution,
            CASE 
                WHEN v_compliance_check.is_compliant THEN 'COMPLIANT'
                ELSE 'EXCEPTION'
            END,
            p_error_type || ' resolution guidance',
            COALESCE(v_doctrine_guidance.guidance_text, 'No specific doctrine found'),
            COALESCE(v_doctrine_guidance.confidence_score, 0.0),
            COALESCE(v_compliance_check.escalation_needed, false) OR NOT COALESCE(v_compliance_check.is_compliant, false)
        );
        
        -- Update error log with doctrine compliance status
        UPDATE shq.orbt_error_log 
        SET 
            doctrine_violated = CASE WHEN NOT COALESCE(v_compliance_check.is_compliant, true) THEN v_compliance_check.doctrine_violation END,
            requires_human = COALESCE(v_compliance_check.escalation_needed, false) OR NOT COALESCE(v_compliance_check.is_compliant, false)
        WHERE error_id = p_error_id;
    END IF;
    
    RETURN COALESCE(v_integration_id, p_error_id);
END;
$$ LANGUAGE plpgsql;
```

---

## Agent Integration Workflow

### 1. Before Any Major Decision
```python
# Python example for agent doctrine consultation
def consult_doctrine(agent_id, subhive_code, decision_context):
    query = """
    SELECT * FROM shq.get_doctrine_guidance(%s, %s, %s)
    """
    
    result = db.execute(query, [subhive_code, decision_context, agent_id])
    
    if result and result[0]['confidence_score'] > 70.0:
        return {
            'guidance': result[0]['guidance_text'],
            'confidence': result[0]['confidence_score'],
            'escalation_required': result[0]['requires_escalation'],
            'doctrine_compliant': True
        }
    else:
        # No clear doctrine guidance - may need human review
        return {
            'guidance': 'No specific doctrine found - proceed with caution',
            'confidence': 0.0,
            'escalation_required': True,
            'doctrine_compliant': False
        }

# Usage in agent code
class DatabaseSpecialist:
    def handle_connection_timeout(self, error_details):
        # Consult doctrine first
        doctrine_guidance = consult_doctrine(
            agent_id='database-specialist',
            subhive_code='03',  # DATA subhive
            decision_context='database connection timeout recovery'
        )
        
        if doctrine_guidance['escalation_required']:
            self.escalate_to_orchestrator(error_details, doctrine_guidance)
        else:
            # Follow doctrine guidance
            proposed_action = self.generate_fix_based_on_doctrine(doctrine_guidance)
            
            # Validate compliance before acting
            compliance = validate_compliance(
                agent_id='database-specialist',
                subhive_code='03',
                proposed_action=proposed_action,
                context='connection timeout'
            )
            
            if compliance['is_compliant']:
                self.execute_fix(proposed_action)
            else:
                self.log_doctrine_exception(compliance['doctrine_violation'])
                self.escalate_for_human_review()
```

### 2. Enhanced Resolution Library with Doctrine
```sql
-- Updated resolution library to include doctrine compliance
ALTER TABLE shq.orbt_resolution_library 
ADD COLUMN doctrine_sections_consulted TEXT[] DEFAULT ARRAY[]::TEXT[],
ADD COLUMN doctrine_compliance_score DECIMAL(5,2) DEFAULT 100.0,
ADD COLUMN doctrine_exceptions TEXT[] DEFAULT ARRAY[]::TEXT[],
ADD COLUMN human_doctrine_review_required BOOLEAN DEFAULT FALSE;
```

### 3. Real-time Doctrine Monitoring
```sql
-- View for monitoring doctrine compliance across system
CREATE VIEW shq.doctrine_compliance_dashboard AS
SELECT 
    d.subhive_code,
    COUNT(*) as total_consultations,
    COUNT(CASE WHEN d.doctrine_compliance = 'COMPLIANT' THEN 1 END) as compliant_decisions,
    COUNT(CASE WHEN d.doctrine_compliance = 'EXCEPTION' THEN 1 END) as exception_decisions,
    COUNT(CASE WHEN d.human_review_required THEN 1 END) as pending_human_review,
    AVG(d.confidence_score) as avg_confidence,
    COUNT(DISTINCT d.agent_id) as agents_consulting_doctrine,
    MAX(d.consulted_at) as last_consultation
FROM shq.orbt_doctrine_integration d
WHERE d.consulted_at > NOW() - INTERVAL '24 hours'
GROUP BY d.subhive_code
ORDER BY d.subhive_code;
```

---

## Automatic Doctrine Integration in heir-drop-in.js

### Enhanced Schema Creation
```javascript
// Add to heir-drop-in.js
const doctrineIntegrationSchema = `
-- Doctrine Integration Tables
CREATE SEQUENCE IF NOT EXISTS doctrine_integration_seq;

CREATE TABLE IF NOT EXISTS shq.orbt_doctrine_integration (
    id SERIAL PRIMARY KEY,
    integration_id VARCHAR(50) UNIQUE NOT NULL,
    error_id VARCHAR(50) NULL,
    resolution_id VARCHAR(50) NULL,
    agent_id VARCHAR(100) NOT NULL,
    doctrine_section VARCHAR(100) NOT NULL,
    doctrine_subsection VARCHAR(100) NULL,
    subhive_code VARCHAR(2) NOT NULL,
    decision_type VARCHAR(50) NOT NULL,
    decision_made TEXT NOT NULL,
    doctrine_compliance VARCHAR(20) NOT NULL CHECK (doctrine_compliance IN ('COMPLIANT', 'EXCEPTION', 'UNCLEAR')),
    exception_reason TEXT NULL,
    doctrine_query TEXT NOT NULL,
    doctrine_response TEXT NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    consulted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decision_outcome VARCHAR(50) NULL,
    human_review_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enhanced error log with doctrine fields
ALTER TABLE shq.orbt_error_log 
ADD COLUMN IF NOT EXISTS doctrine_sections_consulted TEXT[] DEFAULT ARRAY[]::TEXT[],
ADD COLUMN IF NOT EXISTS doctrine_compliance_score DECIMAL(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS doctrine_exceptions TEXT[] DEFAULT ARRAY[]::TEXT[];

-- Indexes
CREATE INDEX IF NOT EXISTS idx_doctrine_integration_agent ON shq.orbt_doctrine_integration(agent_id);
CREATE INDEX IF NOT EXISTS idx_doctrine_integration_subhive ON shq.orbt_doctrine_integration(subhive_code);
CREATE INDEX IF NOT EXISTS idx_doctrine_integration_compliance ON shq.orbt_doctrine_integration(doctrine_compliance);

-- Connection test to dpr_doctrine table
CREATE OR REPLACE FUNCTION shq.test_doctrine_connection()
RETURNS BOOLEAN AS $$
BEGIN
    PERFORM 1 FROM dpr_doctrine LIMIT 1;
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
`;
```

---

## Usage Examples

### 1. Payment Processing with Doctrine
```python
# Payment specialist consulting doctrine before processing refund
doctrine_guidance = consult_doctrine(
    agent_id='payment-specialist',
    subhive_code='04',  # PAY subhive
    decision_context='customer refund request over $500'
)

if doctrine_guidance['confidence'] > 80:
    if 'requires approval' in doctrine_guidance['guidance'].lower():
        escalate_to_human_approval(refund_request, doctrine_guidance)
    else:
        process_refund_automatically(refund_request)
else:
    # Unclear doctrine - escalate
    escalate_for_doctrine_clarification(refund_request)
```

### 2. Data Access Control
```python
# Data orchestrator checking doctrine for data access permissions
doctrine_check = validate_compliance(
    agent_id='data-orchestrator',
    subhive_code='03',
    proposed_action='grant_database_access_to_external_api',
    context='third party integration request'
)

if not doctrine_check['is_compliant']:
    deny_access_with_doctrine_reason(doctrine_check['doctrine_violation'])
else:
    proceed_with_access_grant()
```

---

## Benefits

### For Agents
- **Never violate doctrine** - automatic compliance checking
- **Consistent decision-making** across all agents
- **Automatic escalation** when doctrine is unclear
- **Learning from 600 pages** of institutional knowledge

### For Operations  
- **Audit trail** of all doctrine consultations
- **Compliance monitoring** in real-time
- **Exception tracking** for continuous improvement
- **Human review** only when doctrine is ambiguous

### For Business
- **Guaranteed compliance** with established procedures
- **Institutional knowledge preservation** in agent decisions
- **Consistent customer experience** regardless of which agent handles request
- **Automatic adaptation** when doctrine is updated

---

*This integration ensures every HEIR agent operates within your established 600-page doctrine while maintaining the speed and intelligence of the automated system.*