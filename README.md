# Claude Code Hierarchical Agent System Architecture

## System Overview: Hive-to-Sub-Hive Orchestration Model

This system uses a hierarchical approach where AI builds automation systems rather than running them constantly. Each level has specific responsibilities and clear delegation patterns.

## Core Philosophy
- **AI builds automation that runs independently**
- **Specialists create systems that don't need AI after deployment**
- **Token usage: Heavy during build phase, minimal during production**
- **ORBP (Operation, Repair, Build, Troubleshoot) self-healing integration**

## Architecture Levels

### Level 1: CEO Orchestrators (30,000ft - Strategic Level)
- **ceo-orchestrator**: Master coordinator, vision setting, division management, final QA
- **project-planner**: Complex projects, multi-hive coordination, dependencies, resource management

### Level 2: Division Managers (20,000ft - Tactical Level)
- **backend-manager**: API design, database work, auth systems, server logic
- **integration-manager**: External APIs, scraping coordination, data pipelines, rate limiting
- **deployment-manager**: Platform operations, infrastructure, monitoring, CI/CD setup

### Level 3: Tool Specialists (10,000ft - Execution Level)
- **neon-integrator**: Database connections, query optimization, pool configuration
- **apify-integrator**: Actor setup, data extraction, rate limits, data transformation
- **render-deployer**: Platform configuration, environment setup, health checks
- **stripe-handler**: Payment flows, webhook setup, subscription management
- **firecrawl-scraper**: Web scraping, data cleaning, ethical scraping
- **error-analyst**: 3-strike rule, pattern recognition, auto-repair, FAQ updates

## Quick Start

1. **Setup the system**:
   ```bash
   # Create global agents directory
   mkdir -p ~/.claude/agents/{orchestrators,managers,specialists}
   
   # Copy global agents
   cp -r agents/global/* ~/.claude/agents/
   ```

2. **Create a new project**:
   ```bash
   # Initialize project-specific agents
   mkdir -p .claude/agents/{orchestrators,managers,specialists}
   cp -r agents/project-templates/* .claude/agents/
   ```

3. **Start with CEO Orchestrator**:
   ```bash
   # The CEO orchestrator will coordinate the entire project
   # Just describe your requirements and watch the system build itself
   ```

## Usage Examples

### Simple Project
```
User: "Build a landing page with contact form"
└── ceo-orchestrator
    └── frontend-specialist (direct delegation)
```

### Medium Project  
```
User: "Build SaaS app with Stripe + Neon"
└── ceo-orchestrator
    ├── backend-manager
    │   ├── neon-integrator
    │   └── stripe-handler
    └── deployment-manager
        └── vercel-deployer
```

### Complex Project
```
User: "Build buyer intent system with 6 tools"
└── ceo-orchestrator
    ├── data-collection-manager
    │   ├── apollo-processor
    │   └── apify-coordinator
    ├── processing-manager
    │   ├── validation-specialist
    │   └── bigquery-processor
    ├── intelligence-manager
    │   ├── intent-scorer
    │   └── pattern-detector
    └── deployment-manager
        ├── render-deployer
        └── monitoring-specialist
```

## ORBP Integration

The system includes self-healing capabilities:
- **3-strike rule**: Automatic retry → Alternative method → Human intervention
- **Pattern recognition**: Learn from errors and update FAQ
- **Auto-repair**: Fix common issues without human intervention
- **Monitoring**: Continuous health checks and alerting

## Directory Structure

```
~/.claude/agents/                    # Global agents (all projects)
├── orchestrators/
│   ├── ceo-orchestrator.md         # Master coordinator
│   └── project-planner.md          # Complex project manager
├── managers/
│   ├── backend-manager.md          # Backend coordination
│   ├── integration-manager.md      # External services
│   └── deployment-manager.md       # Platform operations
└── specialists/
    ├── neon-integrator.md          # Database specialist
    ├── apify-integrator.md         # Scraping specialist
    ├── stripe-handler.md           # Payment specialist
    ├── render-deployer.md          # Platform specialist
    └── error-analyst.md            # ORBP specialist

.claude/agents/                      # Project-specific agents
├── orchestrators/
│   └── buyer-intent-orchestrator.md # Domain-specific coordinator
├── managers/
│   └── insurance-pipeline-manager.md# Industry-specific manager
└── specialists/
    ├── apollo-processor.md         # Project-specific tool
    └── insurance-validator.md      # Domain-specific logic
```

## Key Principles

1. **Clear Hierarchy**: Each agent knows who they report to and delegate to
2. **Focused Responsibility**: Each agent has a single, well-defined purpose  
3. **Clean Handoffs**: Agents complete their work and pass results up/down
4. **Automation Focus**: Agents build systems that run without ongoing AI
5. **ORBP Integration**: Self-healing capabilities at all levels
6. **Scalable Architecture**: Easy to add new divisions or specialists
7. **Token Efficiency**: Heavy usage during build, minimal during operation

This architecture transforms Claude Code from a single assistant into a coordinated development organization that builds autonomous, self-healing business systems.
