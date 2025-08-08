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

console.log('🚀 Setting up HEIR Agent System...');

// Create directory structure
const dirs = [
  '.claude',
  '.claude/agents',
  '.claude/agents/orchestrators',
  '.claude/agents/managers', 
  '.claude/agents/specialists'
];

dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`✅ Created ${dir}/`);
  }
});

// Create project config template
const configTemplate = {
  "// PROJECT OVERVIEW": "=== FILL THIS OUT FIRST ===",
  "project_name": path.basename(process.cwd()),
  "project_description": "What you want to build in 1-2 sentences",
  "project_type": "simple/medium/complex - See examples",
  
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
    "schema_enforcement": "STAMPED/SPVPET/STACKED",
    "doctrine_enforcement_level": "strict"
  },

  "// WHICH AGENTS TO USE": "=== AGENT ACTIVATION (set to true for needed agents) ===",
  "agents_needed": {
    "// System Orchestrator": "DPR doctrine enforcement and ID management", 
    "system_orchestrator": {
      "use_this_agent": true,
      "why": "Always needed - enforces your DPR doctrine system"
    },

    "// HEIR Claude Code Specialist": "Automates all Claude Code operations",
    "heir_claude_code_specialist": {
      "use_this_agent": true, 
      "why": "Always needed - handles all Claude Code syntax and HEIR system setup automatically"
    },

    "// CEO Orchestrator": "Project coordination", 
    "ceo_orchestrator": {
      "use_this_agent": true,
      "why": "Always needed - master coordinator"
    },
    
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

console.log('\n🎉 HEIR Agent System setup complete!');
console.log('\n📋 Configuration Template Created:');
console.log('✅ DPR doctrine system integration');
console.log('✅ ORBT monitoring enabled by default');
console.log('✅ System + HEIR Claude Code specialists always active');
console.log('✅ Complete technical specification templates');
console.log('\n🚀 Next steps:');
console.log('1. Fill out heir-project-config.json with your project requirements');
console.log('2. Activate needed agents (backend, integration, deployment, etc.)');
console.log('3. Specify technical details for active agents only'); 
console.log('4. Bring completed config to Claude Code with HEIR Claude Code Specialist');
console.log('5. Say "Set up my HEIR project" - everything will be automated!');
console.log('\n🎯 Project:', path.basename(process.cwd()));
console.log('🎯 HEIR Version: 1.0.0 with complete monitoring & automation');