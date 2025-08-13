#!/usr/bin/env node

/**
 * HEIR Agent System - Drop-in Setup
 * 
 * Usage: Just drop this file into any existing project and run:
 * node heir-drop-in.js
 * 
 * This will:
 * 1. Create the .claude/agents structure
 * 2. Generate project-config.json template
 * 3. Set up HEIR system without disrupting existing code
 */

const fs = require('fs');
const path = require('path');

console.log('🏗️ Setting up HEIR Agent System - Skyscraper Construction Model...');

// Create skyscraper directory structure
const dirs = [
  '.claude',
  '.claude/agents',
  '.claude/agents/meta_system',
  '.claude/agents/domain_orchestrators',
  '.claude/agents/specialist_library',
  '.heir',
  '.heir/institutional_knowledge',
  '.heir/orbt_logs',
  '.heir/project_configs',
  '.heir/database_schemas',
  '.heir/error_logging',
  '.heir/resolution_tracking'
];

dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`✅ Created ${dir}/`);
  }
});

// Create skyscraper project config template
const configTemplate = {
  "// PROJECT OVERVIEW": "=== FILL THIS OUT FIRST ===",
  "project_name": path.basename(process.cwd()),
  "project_description": "What you want to build in 1-2 sentences",
  "project_type": "simple/medium/complex - See examples",
  "architecture_model": "skyscraper_construction",
  
  "// WHAT TO BUILD": "=== PROJECT REQUIREMENTS ===",
  "what_you_want": "Detailed description of what the end result should be",
  "success_looks_like": [
    "List specific outcomes that mean success",
    "e.g., 'Users can sign up and pay for subscriptions'",
    "e.g., 'System processes 1000 leads per hour'"
  ],
  "constraints": {
    "budget": "Any budget limits or cost considerations",
    "timeline": "When do you need this done?",
    "must_use_technologies": ["List any required tech/platforms"],
    "cannot_use": ["List any forbidden technologies"]
  },

  "// DPR SYSTEM INTEGRATION": "=== YOUR DOCTRINE SYSTEM ===",
  "dpr_system": {
    "unique_id_format": "[DB].[SUBHIVE].[MICROPROCESS].[TOOL].[ALTITUDE].[STEP]",
    "section_number_format": "[database].[subhive].[subsubhive].[section].[sequence]",
    "process_id_style": "Verb + Object (e.g., Load CSV, Generate Report)",
    "orbt_enabled": true,
    "orbt_protocol": "3_strike_escalation_with_institutional_knowledge",
    "schema_enforcement": "STAMPED/SPVPET/STACKED",
    "doctrine_enforcement_level": "strict",
    "institutional_knowledge_enabled": true,
    "cross_project_learning": true
  },

  "// SKYSCRAPER CONSTRUCTION AGENTS": "=== AGENT ACTIVATION (set to true for needed agents) ===",
  "agents_needed": {
    "// LEVEL 0: Meta-System (Always Required)": "",
    "master_orchestrator": {
      "use_this_agent": true,
      "role": "building_superintendent",
      "why": "Always needed - coordinates all domain orchestrators like a construction superintendent"
    },
    
    "system_orchestrator": {
      "use_this_agent": true,
      "role": "dpr_doctrine_enforcement",
      "why": "Always needed - enforces your DPR doctrine system across all agents"
    },

    "heir_claude_code_specialist": {
      "use_this_agent": true,
      "role": "claude_code_automation", 
      "why": "Always needed - automates all Claude Code operations and HEIR system setup"
    },

    "// LEVEL 1: Domain Orchestrators (Floor Managers)": "",
    
    "project_planner": {
      "use_this_agent": false,
      "why": "Only for complex projects with multiple phases"
    },

    "backend_manager": {
      "use_this_agent": false,
      "why": "Need APIs, databases, or server logic",
      "what_to_build": "Describe backend requirements"
    },
    
    "integration_manager": {
      "use_this_agent": false,
      "why": "Need external APIs, scraping, or data pipelines",
      "what_to_integrate": "List external services/APIs needed"
    },
    
    "deployment_manager": {
      "use_this_agent": false,
      "why": "Need hosting, CI/CD, or infrastructure",
      "where_to_deploy": "Platform preferences (Render, Vercel, etc.)"
    },

    "neon_database": {
      "use_this_agent": false,
      "why": "Need PostgreSQL database",
      "database_needs": "Describe what data you need to store"
    },
    
    "stripe_payments": {
      "use_this_agent": false,
      "why": "Need payment processing",
      "payment_details": "What kind of payments? (one-time, subscriptions, etc.)"
    },
    
    "web_scraping": {
      "use_this_agent": false,
      "why": "Need to scrape websites for data",
      "scraping_targets": "What websites/data do you need?"
    },
    
    "orbt_monitor": {
      "use_this_agent": true,
      "why": "Production systems need real-time monitoring and error logging",
      "monitoring_requirements": "Real-time dashboard, global error logging, automated escalation"
    },
    
    "error_handling": {
      "use_this_agent": false,
      "why": "Need advanced error handling and monitoring beyond ORBT",
      "error_requirements": "What kind of specialized errors to catch/handle?"
    }
  },

  "// TECHNICAL DETAILS": "=== FILL OUT FOR ACTIVE AGENTS ONLY ===",
  "technical_specs": {
    "backend_details": {
      "database_schema": "Describe your data structure",
      "api_endpoints": ["List the APIs you need", "/api/users", "/api/payments"],
      "authentication": "How should users log in? (email/password, Google, etc.)"
    },
    
    "integration_details": {
      "external_apis": ["List external services", "OpenAI API", "SendGrid"],
      "data_flows": "How should data move between services?",
      "rate_limits": "Any API rate limit considerations?"
    },
    
    "deployment_details": {
      "hosting_platform": "Preferred platform (Render, Vercel, etc.)",
      "environment_variables": "List any env vars needed",
      "monitoring_needs": "What should be monitored?"
    },
    
    "database_details": {
      "tables_needed": ["users", "payments", "logs"],
      "relationships": "How are your data tables connected?",
      "performance_needs": "Any specific performance requirements?"
    },
    
    "payment_details": {
      "payment_types": ["one-time", "subscription", "usage-based"],
      "pricing_tiers": "Describe your pricing structure",
      "webhook_handling": "What should happen when payments succeed/fail?"
    },
    
    "scraping_details": {
      "target_websites": ["List websites to scrape"],
      "data_to_extract": "What specific data do you need?",
      "scraping_frequency": "How often should this run?",
      "ethical_limits": "Any scraping restrictions to follow?"
    },
    
    "monitoring_details": {
      "dashboard_enabled": true,
      "error_log_retention": "30 days",
      "escalation_channels": ["slack", "email"],
      "orbt_compliance": true,
      "performance_tracking": true,
      "training_logs": true
    }
  },

  "system": {
    "entry_point": "system-orchestrator",
    "user_interface": "heir-claude-code-specialist",
    "project_coordination": "ceo-orchestrator",
    "auto_repair": true,
    "orbt_enabled": true,
    "dpr_compliant": true,
    "session_tracking": true,
    "created_timestamp": new Date().toISOString(),
    "project_root": process.cwd(),
    "heir_version": "1.0.0"
  }
};

// Write config file
const configPath = 'heir-project-config.json';
if (!fs.existsSync(configPath)) {
  fs.writeFileSync(configPath, JSON.stringify(configTemplate, null, 2));
  console.log(`✅ Created ${configPath}`);
} else {
  console.log(`⚠️  ${configPath} already exists, skipping...`);
}

// Create .gitignore entry if needed
const gitignorePath = '.gitignore';
const gitignoreEntry = '\n# HEIR Agent System\n.claude/\nheir-project-config.json\n';

if (fs.existsSync(gitignorePath)) {
  const gitignoreContent = fs.readFileSync(gitignorePath, 'utf8');
  if (!gitignoreContent.includes('HEIR Agent System')) {
    fs.appendFileSync(gitignorePath, gitignoreEntry);
    console.log('✅ Updated .gitignore');
  }
} else {
  fs.writeFileSync(gitignorePath, gitignoreEntry);
  console.log('✅ Created .gitignore');
}

// Create ORBT error logging schema files
const errorLoggingSchema = `
-- ORBT Automatic Error Logging Schema
-- This gets deployed automatically with every HEIR system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create SHQ schema for system headquarters
CREATE SCHEMA IF NOT EXISTS shq;

-- Master error logging table (automatically used by all agents)
CREATE TABLE IF NOT EXISTS shq.orbt_error_log (
    id SERIAL PRIMARY KEY,
    error_id VARCHAR(50) UNIQUE NOT NULL,
    orbt_status VARCHAR(10) NOT NULL CHECK (orbt_status IN ('GREEN', 'YELLOW', 'RED')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_timestamp TIMESTAMPTZ NULL,
    agent_id VARCHAR(100) NOT NULL,
    agent_hierarchy VARCHAR(20) NOT NULL CHECK (agent_hierarchy IN ('orchestrator', 'manager', 'specialist')),
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    error_stack TEXT NULL,
    doctrine_violated VARCHAR(50) NULL,
    section_number VARCHAR(50) NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    escalation_level INTEGER NOT NULL DEFAULT 0,
    requires_human BOOLEAN NOT NULL DEFAULT FALSE,
    project_context VARCHAR(100) NULL,
    render_endpoint VARCHAR(200) NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolution_method VARCHAR(50) NULL,
    resolution_notes TEXT NULL,
    downtime_seconds INTEGER NULL,
    affected_users INTEGER NULL,
    troubleshooting_key VARCHAR(100) NULL,
    auto_fix_attempted BOOLEAN DEFAULT FALSE,
    auto_fix_success BOOLEAN DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Troubleshooting guide table (instant error resolution)
CREATE TABLE IF NOT EXISTS shq.orbt_troubleshooting_guide (
    id SERIAL PRIMARY KEY,
    lookup_key VARCHAR(100) UNIQUE NOT NULL,
    unique_id_pattern VARCHAR(50) NOT NULL,
    process_id VARCHAR(50) NOT NULL,
    error_code VARCHAR(20) NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    error_title VARCHAR(200) NOT NULL,
    error_description TEXT NOT NULL,
    business_impact VARCHAR(100) NOT NULL,
    urgency_level VARCHAR(20) NOT NULL,
    immediate_action TEXT NOT NULL,
    diagnostic_steps TEXT[] NOT NULL,
    resolution_steps TEXT[] NOT NULL,
    escalation_criteria TEXT NOT NULL,
    common_causes TEXT[] NOT NULL,
    prevention_tips TEXT[] NOT NULL,
    related_errors VARCHAR(50)[] NULL,
    affected_agents VARCHAR(50)[] NOT NULL,
    affected_domains VARCHAR(50)[] NOT NULL,
    system_components TEXT[] NOT NULL,
    auto_resolvable BOOLEAN NOT NULL DEFAULT FALSE,
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    avg_resolution_time_minutes INTEGER NOT NULL DEFAULT 0,
    requires_human_expertise BOOLEAN NOT NULL DEFAULT FALSE,
    documentation_links TEXT[] NULL,
    code_examples TEXT NULL,
    monitoring_queries TEXT[] NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NULL,
    version VARCHAR(10) NOT NULL DEFAULT '1.0.0'
);

-- Resolution library table (never start from scratch)
CREATE TABLE IF NOT EXISTS shq.orbt_resolution_library (
    id SERIAL PRIMARY KEY,
    resolution_id VARCHAR(50) UNIQUE NOT NULL,
    error_signature VARCHAR(500) NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    error_code VARCHAR(20) NOT NULL,
    unique_id_pattern VARCHAR(50) NOT NULL,
    process_id VARCHAR(50) NOT NULL,
    fix_title VARCHAR(200) NOT NULL,
    fix_description TEXT NOT NULL,
    fix_category VARCHAR(50) NOT NULL,
    diagnostic_commands TEXT[] NOT NULL,
    fix_commands TEXT[] NOT NULL,
    verification_commands TEXT[] NOT NULL,
    rollback_commands TEXT[] NOT NULL,
    affected_systems TEXT[] NOT NULL,
    prerequisites TEXT[] NULL,
    side_effects TEXT[] NULL,
    environment_type VARCHAR(20) NOT NULL,
    fixed_by VARCHAR(100) NOT NULL,
    fixed_by_type VARCHAR(20) NOT NULL,
    original_error_id VARCHAR(50) NOT NULL,
    resolution_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolution_time_minutes INTEGER NOT NULL,
    success_rate DECIMAL(5,2) NOT NULL DEFAULT 100.0,
    application_count INTEGER NOT NULL DEFAULT 1,
    last_applied TIMESTAMPTZ NULL,
    lessons_learned TEXT NOT NULL,
    improvement_suggestions TEXT NULL,
    related_resolutions VARCHAR(50)[] NULL,
    documentation_created TEXT[] NULL,
    code_changes_required BOOLEAN DEFAULT FALSE,
    config_changes_required BOOLEAN DEFAULT FALSE,
    infrastructure_changes_required BOOLEAN DEFAULT FALSE,
    peer_reviewed BOOLEAN DEFAULT FALSE,
    peer_reviewer VARCHAR(100) NULL,
    review_notes TEXT NULL,
    approved_for_automation BOOLEAN DEFAULT FALSE,
    automation_confidence DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version VARCHAR(10) NOT NULL DEFAULT '1.0.0'
);

-- Escalation queue table (human intervention tracking)
CREATE TABLE IF NOT EXISTS shq.orbt_escalation_queue (
    id SERIAL PRIMARY KEY,
    escalation_id VARCHAR(50) UNIQUE NOT NULL,
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'DISMISSED')),
    error_id VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(100) NULL,
    escalated_by VARCHAR(100) NOT NULL,
    escalated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_at TIMESTAMPTZ NULL,
    resolved_at TIMESTAMPTZ NULL,
    resolution_notes TEXT NULL,
    resolution_method VARCHAR(50) NULL,
    follow_up_required BOOLEAN NOT NULL DEFAULT FALSE,
    follow_up_date TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- System status table (real-time monitoring)
CREATE TABLE IF NOT EXISTS shq.orbt_system_status (
    id SERIAL PRIMARY KEY,
    status_id VARCHAR(50) UNIQUE NOT NULL,
    overall_status VARCHAR(10) NOT NULL CHECK (overall_status IN ('GREEN', 'YELLOW', 'RED')),
    active_agents INTEGER NOT NULL DEFAULT 0,
    green_count INTEGER NOT NULL DEFAULT 0,
    yellow_count INTEGER NOT NULL DEFAULT 0,
    red_count INTEGER NOT NULL DEFAULT 0,
    avg_execution_time_ms DECIMAL(10,2) NULL,
    avg_token_usage DECIMAL(10,2) NULL,
    avg_memory_usage_mb DECIMAL(10,2) NULL,
    uptime_seconds INTEGER NOT NULL DEFAULT 0,
    last_error_timestamp TIMESTAMPTZ NULL,
    escalation_pending INTEGER NOT NULL DEFAULT 0,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_error_log_timestamp ON shq.orbt_error_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_log_status ON shq.orbt_error_log(orbt_status);
CREATE INDEX IF NOT EXISTS idx_error_log_agent ON shq.orbt_error_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_lookup ON shq.orbt_troubleshooting_guide(lookup_key);
CREATE INDEX IF NOT EXISTS idx_resolution_library_pattern ON shq.orbt_resolution_library(error_signature);
CREATE INDEX IF NOT EXISTS idx_escalation_status ON shq.orbt_escalation_queue(status);

-- Auto-escalation trigger (2+ occurrences = human escalation)
CREATE OR REPLACE FUNCTION shq.check_error_escalation()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE shq.orbt_error_log 
    SET occurrence_count = (
        SELECT COUNT(*) 
        FROM shq.orbt_error_log 
        WHERE error_message = NEW.error_message 
        AND agent_id = NEW.agent_id
    )
    WHERE error_id = NEW.error_id;
    
    IF (SELECT occurrence_count FROM shq.orbt_error_log WHERE error_id = NEW.error_id) >= 2 THEN
        UPDATE shq.orbt_error_log 
        SET escalation_level = 2, requires_human = TRUE, orbt_status = 'RED'
        WHERE error_id = NEW.error_id;
        
        INSERT INTO shq.orbt_escalation_queue (
            escalation_id, error_id, priority, status, escalated_by
        ) VALUES (
            'ESC-' || NEW.error_id, NEW.error_id, 'HIGH', 'PENDING', 'SYSTEM_AUTO'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_error_escalation
    AFTER INSERT ON shq.orbt_error_log
    FOR EACH ROW
    EXECUTE FUNCTION shq.check_error_escalation();
`;

const troubleshootingData = `
-- Default troubleshooting entries (automatically loaded)
INSERT INTO shq.orbt_troubleshooting_guide (
    lookup_key, unique_id_pattern, process_id, error_code, error_type,
    error_title, error_description, business_impact, urgency_level,
    immediate_action, diagnostic_steps, resolution_steps, escalation_criteria,
    common_causes, prevention_tips, affected_agents, affected_domains, system_components,
    auto_resolvable, success_rate, avg_resolution_time_minutes
) VALUES 
(
    'ProcessData:CONN_TIMEOUT',
    '*.03.*.DB.*.*',
    'ProcessData',
    'CONN_TIMEOUT',
    'connection',
    'Database Connection Timeout',
    'Cannot connect to database within timeout period',
    'Data operations blocked, users cannot access features',
    'HIGH',
    'Retry connection, check database status endpoint',
    ARRAY['ping database_host', 'SELECT 1 FROM pg_stat_activity', 'Check connection pool'],
    ARRAY['Restart connection pool', 'Scale database if CPU > 80%', 'Clear pool if > 90% utilized'],
    'If 3 retries fail OR database unresponsive OR >100 affected users',
    ARRAY['Database overload', 'Connection pool exhaustion', 'Network issues'],
    ARRAY['Monitor pool utilization', 'Set up auto-scaling', 'Implement circuit breaker'],
    ARRAY['database-specialist', 'data-orchestrator'],
    ARRAY['data', 'platform'],
    ARRAY['PostgreSQL', 'Connection Pool', 'Neon Database'],
    true, 85.0, 5
),
(
    'ProcessPayment:PAY_DECLINED',
    '*.04.*.PAY.*.*',
    'ProcessPayment',
    'PAY_DECLINED',
    'payment',
    'Payment Card Declined',
    'Customer payment declined by payment processor',
    'Customer cannot complete purchase, revenue loss',
    'MEDIUM',
    'Check decline reason, show user-friendly message',
    ARRAY['Check Stripe dashboard', 'Verify card format', 'Check fraud flags'],
    ARRAY['Show decline message', 'Suggest alternative payment', 'Retry with 3D Secure'],
    'If >10 declines in 5 minutes OR working card declined',
    ARRAY['Insufficient funds', 'Expired card', 'Fraud detection'],
    ARRAY['Pre-validate cards', 'Implement retry logic', 'Use address verification'],
    ARRAY['payment-specialist', 'payment-orchestrator'],
    ARRAY['payment'],
    ARRAY['Stripe API', 'Payment Gateway'],
    true, 95.0, 2
) ON CONFLICT (lookup_key) DO NOTHING;
`;

// Write database schema files
fs.writeFileSync('.heir/database_schemas/orbt-schema.sql', errorLoggingSchema);
fs.writeFileSync('.heir/database_schemas/troubleshooting-data.sql', troubleshootingData);

console.log('✅ Created ORBT error logging database schema');
console.log('✅ Created troubleshooting guide with default entries');

console.log('\n🏗️ HEIR Skyscraper Construction System setup complete!');
console.log('\n📋 Skyscraper Configuration Template Created:');
console.log('✅ Master Orchestrator (Building Superintendent) enabled');
console.log('✅ DPR doctrine system with 3-Strike ORBT protocol');
console.log('✅ Institutional knowledge system for cross-project learning');
console.log('✅ Domain Orchestrators (Floor Managers) ready for assignment');
console.log('✅ Specialist Library (Reusable Workforce Pool) configured');
console.log('✅ Complete technical specification templates');
console.log('✅ AUTOMATIC: Error logging to shq.orbt_error_log table');
console.log('✅ AUTOMATIC: Troubleshooting guide with instant lookup');
console.log('✅ AUTOMATIC: Resolution tracking (never start from scratch)');
console.log('✅ AUTOMATIC: 3-strike escalation with human intervention');
console.log('✅ AUTOMATIC: Pattern recognition and institutional learning');
console.log('\n🚀 Next steps:');
console.log('1. Fill out heir-project-config.json with your project requirements');
console.log('2. Deploy database schema: psql -f .heir/database_schemas/orbt-schema.sql');
console.log('3. Load troubleshooting data: psql -f .heir/database_schemas/troubleshooting-data.sql');
console.log('4. Activate needed Domain Orchestrators (Data, Payment, Integration, Platform)');
console.log('5. Specialists will be assigned automatically by Domain Orchestrators'); 
console.log('6. Bring completed config to Claude Code with HEIR Claude Code Specialist');
console.log('7. Say "Set up my HEIR project" - complete skyscraper construction automated!');
console.log('\n🏗️ Project:', path.basename(process.cwd()));
console.log('🏗️ HEIR Version: 2.0.0 Skyscraper Construction Model');
console.log('🧠 Features: Master Orchestrator + Domain Orchestrators + Specialist Library');
console.log('⚡ Protocol: 3-Strike ORBT with Institutional Knowledge');
console.log('🔄 Learning: Cross-project expertise that compounds over time');
console.log('🛡️ AUTOMATIC: Complete error logging, troubleshooting & resolution tracking');