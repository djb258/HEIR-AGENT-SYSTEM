# HEIR Agent System Guide for GPT

This guide explains what each type of agent does and when to use them. Use this to select the right agents for any project.

## How HEIR Works
- **Level 1**: Strategic coordination (30,000ft view)
- **Level 2**: Tactical management (20,000ft view) 
- **Level 3**: Technical execution (10,000ft view)

Each level delegates down and reports up. Always start with CEO Orchestrator.

---

## LEVEL 1: ORCHESTRATORS (Strategic)

### CEO Orchestrator
**Always Required** - Master coordinator for all projects
- Sets project vision and success criteria
- Assigns work to managers and specialists
- Makes final decisions on architecture
- Ensures quality standards are met
- **Use for**: Every single project

### Project Planner
**For Complex Projects** - Multi-phase coordination
- Breaks down complex projects into phases
- Manages dependencies between different parts
- Allocates resources across multiple teams
- **Use for**: Projects with 5+ major components or multiple integration points

---

## LEVEL 2: MANAGERS (Tactical)

### Backend Manager
**For Server-Side Logic** - Coordinates all backend development
- Designs APIs and database architecture
- Manages authentication and security
- Coordinates between database and payment specialists
- **Use for**: Need APIs, databases, user auth, server logic
- **Delegates to**: Database specialists, auth systems, API designers

### Integration Manager  
**For External Services** - Handles all external connections
- Coordinates API integrations and web scraping
- Manages data pipelines and transformations
- Handles rate limiting and error recovery
- **Use for**: Need to connect external APIs, scrape websites, process external data
- **Delegates to**: Scraping specialists, API connectors, data processors

### Deployment Manager
**For Infrastructure** - Handles hosting and operations  
- Manages platform deployment and CI/CD
- Sets up monitoring and health checks
- Coordinates environment configuration
- **Use for**: Need hosting, deployment, monitoring, infrastructure
- **Delegates to**: Platform specialists (Render, Vercel, etc.), monitoring tools

### Frontend Manager
**For User Interfaces** - Coordinates UI/UX development
- Manages component architecture and state
- Coordinates design implementation
- Handles user experience flows
- **Use for**: Building web apps, mobile apps, user interfaces
- **Delegates to**: React specialists, UI designers, state management

---

## LEVEL 3: SPECIALISTS (Technical Execution)

### DATABASE SPECIALISTS

#### Neon Integrator
**PostgreSQL with Neon platform**
- Sets up database connections and schemas
- Optimizes queries and connection pooling
- **Use for**: Need PostgreSQL database, scalable SQL storage
- **Good for**: SaaS apps, user data, transactional systems

#### Supabase Integrator  
**Full-stack backend with Supabase**
- Database + auth + real-time + storage in one
- Sets up user authentication flows
- **Use for**: Need complete backend solution, real-time features
- **Good for**: Chat apps, collaborative tools, user-generated content

### PAYMENT SPECIALISTS

#### Stripe Handler
**Payment processing with Stripe**
- Sets up payment flows and subscriptions
- Handles webhooks and billing logic
- **Use for**: Need to accept payments, subscriptions, billing
- **Good for**: SaaS subscriptions, e-commerce, one-time payments

### SCRAPING SPECIALISTS

#### Apify Integrator
**Professional web scraping with Apify**
- Sets up actors and data extraction pipelines
- Handles large-scale scraping with proxies
- **Use for**: Need to scrape lots of data, complex websites, at scale
- **Good for**: Lead generation, market research, data collection

#### Firecrawl Scraper
**Simple web scraping with Firecrawl**
- Basic website content extraction
- Good for simple scraping tasks
- **Use for**: Need basic web scraping, content extraction
- **Good for**: Blog content, product info, simple data gathering

### DEPLOYMENT SPECIALISTS

#### Render Deployer
**Deploy to Render platform**
- Full-stack applications with databases
- Good for apps that need persistent storage
- **Use for**: Backend APIs, full-stack apps, databases
- **Good for**: SaaS apps, APIs with databases

#### Vercel Deployer  
**Deploy to Vercel platform**
- Frontend and serverless functions
- Great for static sites and Next.js
- **Use for**: Frontend apps, static sites, serverless functions
- **Good for**: Landing pages, marketing sites, JAMstack apps

### AI/ML SPECIALISTS

#### OpenAI Integrator
**AI capabilities with OpenAI**
- Integrates GPT models and embeddings
- Handles prompt engineering and optimization
- **Use for**: Need AI features, chatbots, content generation
- **Good for**: AI assistants, content tools, automation

### COMMUNICATION SPECIALISTS

#### SendGrid Handler
**Email delivery with SendGrid**
- Transactional and marketing emails
- Email templates and analytics
- **Use for**: Need to send emails, notifications, marketing
- **Good for**: User onboarding, notifications, newsletters

### MONITORING SPECIALISTS

#### Error Analyst
**Advanced error handling and monitoring**
- Implements 3-strike retry logic
- Pattern recognition and auto-repair
- **Use for**: Production systems, critical applications
- **Good for**: SaaS apps, customer-facing systems

---

## COMMON PROJECT PATTERNS

### Simple Landing Page
- **Agents**: CEO Orchestrator → Frontend Manager → Vercel Deployer
- **Use for**: Marketing sites, portfolios, simple presentations

### SaaS Application  
- **Agents**: CEO Orchestrator → Backend Manager (Neon + Stripe) → Frontend Manager → Deployment Manager
- **Use for**: Subscription businesses, user accounts, payments

### Data Collection System
- **Agents**: CEO Orchestrator → Integration Manager (Apify/Firecrawl) → Backend Manager (Neon) → Deployment Manager  
- **Use for**: Lead generation, market research, data aggregation

### AI-Powered Application
- **Agents**: CEO Orchestrator → Backend Manager (OpenAI + Neon) → Frontend Manager → Deployment Manager
- **Use for**: Chatbots, content generation, AI tools

### E-commerce Platform
- **Agents**: CEO Orchestrator → Backend Manager (Neon + Stripe) → Integration Manager (external APIs) → Frontend Manager → Deployment Manager
- **Use for**: Online stores, marketplaces, product catalogs

---

## SELECTION RULES FOR GPT

1. **Always start with CEO Orchestrator** - Required for every project
2. **Use Project Planner only for complex projects** - 5+ major components
3. **Select managers based on project domains**:
   - Need server/database/auth? → Backend Manager
   - Need external APIs/scraping? → Integration Manager  
   - Need hosting/deployment? → Deployment Manager
   - Need user interface? → Frontend Manager
4. **Let managers choose specialists** - They know technical requirements
5. **Add Error Analyst for production systems** - Critical for reliability

## QUESTIONS TO ASK YOURSELF

- **What does the user want to build?** (determines overall architecture)
- **Does it need a database?** (Backend Manager + database specialist)
- **Does it need payments?** (Stripe Handler)
- **Does it need external data?** (Integration Manager + scraping specialist)  
- **Where should it be hosted?** (Deployment Manager + platform specialist)
- **Does it need AI features?** (OpenAI Integrator)
- **Is this for production use?** (Error Analyst for monitoring)

Use this guide to select the minimum viable set of agents that can accomplish the user's goals.