# HEIR System Todo List Integration
## Automatic Task Tracking for Claude Code

---

## Overview
The HEIR system now includes automatic todo list generation and tracking, ensuring Claude Code always maintains organized task lists during complex projects and keeps everyone aligned on progress.

**Key Feature:** Claude automatically creates and updates todo lists for any multi-step HEIR project.

---

## Todo List Database Schema

### 1. Project Todo Tracking Table
```sql
-- Todo list management for HEIR projects
CREATE TABLE IF NOT EXISTS shq.orbt_project_todos (
    id SERIAL PRIMARY KEY,
    todo_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Project Context
    project_name VARCHAR(100) NOT NULL,
    project_session VARCHAR(50) NOT NULL,      -- Links todos to specific sessions
    agent_id VARCHAR(100) NOT NULL,            -- Which agent created/owns todo
    
    -- Todo Details
    todo_title VARCHAR(200) NOT NULL,
    todo_description TEXT NULL,
    todo_category VARCHAR(50) NOT NULL,        -- setup, development, testing, deployment
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, CRITICAL
    
    -- Status Tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'cancelled')),
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    
    -- Dependencies
    depends_on_todo_ids VARCHAR(50)[] NULL,    -- Array of prerequisite todo IDs
    blocks_todo_ids VARCHAR(50)[] NULL,        -- Array of todos this blocks
    
    -- Time Tracking
    estimated_minutes INTEGER NULL,
    actual_minutes INTEGER NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    due_date TIMESTAMPTZ NULL,
    
    -- Assignment & Ownership
    assigned_to VARCHAR(100) NULL,             -- Human or agent assigned
    created_by VARCHAR(100) NOT NULL,          -- Who created this todo
    
    -- HEIR Integration
    related_doctrine_sections VARCHAR(20)[] NULL, -- Doctrine sections that apply
    unique_id_pattern VARCHAR(30) NULL,        -- HEIR unique ID pattern if applicable
    orbt_stage VARCHAR(20) NULL,               -- operate, repair, build, train
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2. Todo Progress Tracking
```sql
-- Detailed progress tracking for todos
CREATE TABLE IF NOT EXISTS shq.orbt_todo_progress (
    id SERIAL PRIMARY KEY,
    progress_id VARCHAR(50) UNIQUE NOT NULL,
    
    todo_id VARCHAR(50) NOT NULL REFERENCES shq.orbt_project_todos(todo_id),
    
    -- Progress Update
    progress_update TEXT NOT NULL,
    completion_percentage_change INTEGER NOT NULL, -- How much % changed
    status_change VARCHAR(50) NULL,                -- Status change if any
    
    -- Context
    updated_by VARCHAR(100) NOT NULL,
    update_type VARCHAR(50) NOT NULL,              -- progress, status_change, completion, blocking_issue
    
    -- Time Tracking
    time_spent_minutes INTEGER NULL,
    
    -- Issues & Notes
    blocking_issues TEXT[] NULL,
    next_steps TEXT[] NULL,
    notes TEXT NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3. Auto Todo Generation Rules
```sql
-- Rules for when Claude should automatically create todos
CREATE TABLE IF NOT EXISTS shq.orbt_todo_generation_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Rule Definition
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT NOT NULL,
    
    -- Trigger Conditions
    trigger_keywords TEXT[] NOT NULL,           -- Keywords that trigger todo creation
    project_types VARCHAR(50)[] NULL,           -- Which project types this applies to
    complexity_threshold VARCHAR(20) NULL,     -- simple, medium, complex
    
    -- Auto-Generated Todo Template
    todo_template JSONB NOT NULL,              -- Template for generated todos
    
    -- Rule Settings
    enabled BOOLEAN DEFAULT TRUE,
    auto_assign BOOLEAN DEFAULT FALSE,
    priority_override VARCHAR(20) NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Claude Code Integration Functions

### 1. Automatic Todo Generation
```sql
-- Function to automatically generate todos based on project context
CREATE OR REPLACE FUNCTION shq.generate_project_todos(
    p_project_name VARCHAR(100),
    p_project_type VARCHAR(50),
    p_requirements TEXT[],
    p_session_id VARCHAR(50)
) RETURNS TABLE(
    generated_todo_ids VARCHAR(50)[],
    todo_summary TEXT
) AS $$
DECLARE
    v_todo_id VARCHAR(50);
    v_generated_ids VARCHAR(50)[] := ARRAY[]::VARCHAR(50)[];
    v_requirement TEXT;
    v_rule RECORD;
    v_todo_template JSONB;
BEGIN
    -- Generate session-specific todos based on requirements
    FOREACH v_requirement IN ARRAY p_requirements
    LOOP
        -- Check if requirement matches auto-generation rules
        FOR v_rule IN 
            SELECT * FROM shq.orbt_todo_generation_rules 
            WHERE enabled = TRUE
            AND (project_types IS NULL OR p_project_type = ANY(project_types))
            AND EXISTS (
                SELECT 1 FROM unnest(trigger_keywords) AS keyword 
                WHERE v_requirement ILIKE '%' || keyword || '%'
            )
        LOOP
            -- Generate todo ID
            v_todo_id := 'TODO-' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '-' || 
                        LPAD(nextval('todo_sequence')::TEXT, 3, '0');
            
            v_todo_template := v_rule.todo_template;
            
            -- Create todo from template
            INSERT INTO shq.orbt_project_todos (
                todo_id, project_name, project_session, agent_id,
                todo_title, todo_description, todo_category, priority,
                status, estimated_minutes, created_by, orbt_stage
            ) VALUES (
                v_todo_id,
                p_project_name,
                p_session_id,
                'claude-code-specialist',
                (v_todo_template->>'title') || ' for ' || p_project_name,
                replace((v_todo_template->>'description'), '{requirement}', v_requirement),
                COALESCE((v_todo_template->>'category'), 'development'),
                COALESCE(v_rule.priority_override, (v_todo_template->>'priority'), 'MEDIUM'),
                'pending',
                (v_todo_template->>'estimated_minutes')::INTEGER,
                'auto_generation_system',
                COALESCE((v_todo_template->>'orbt_stage'), 'build')
            );
            
            v_generated_ids := array_append(v_generated_ids, v_todo_id);
        END LOOP;
    END LOOP;
    
    -- Return generated todo summary
    RETURN QUERY
    SELECT 
        v_generated_ids,
        'Generated ' || array_length(v_generated_ids, 1) || ' todos for ' || p_project_name || ' project'::TEXT;
END;
$$ LANGUAGE plpgsql;
```

### 2. Todo Progress Update Function
```sql
-- Function for Claude to update todo progress
CREATE OR REPLACE FUNCTION shq.update_todo_progress(
    p_todo_id VARCHAR(50),
    p_progress_update TEXT,
    p_completion_percentage INTEGER DEFAULT NULL,
    p_new_status VARCHAR(20) DEFAULT NULL,
    p_time_spent_minutes INTEGER DEFAULT NULL,
    p_blocking_issues TEXT[] DEFAULT NULL,
    p_next_steps TEXT[] DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
    v_progress_id VARCHAR(50);
    v_old_percentage INTEGER;
    v_percentage_change INTEGER := 0;
BEGIN
    -- Get current completion percentage
    SELECT completion_percentage INTO v_old_percentage
    FROM shq.orbt_project_todos 
    WHERE todo_id = p_todo_id;
    
    -- Calculate percentage change
    IF p_completion_percentage IS NOT NULL THEN
        v_percentage_change := p_completion_percentage - v_old_percentage;
    END IF;
    
    -- Generate progress ID
    v_progress_id := 'PROG-' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '-' || 
                    LPAD(nextval('progress_sequence')::TEXT, 3, '0');
    
    -- Update todo
    UPDATE shq.orbt_project_todos 
    SET 
        completion_percentage = COALESCE(p_completion_percentage, completion_percentage),
        status = COALESCE(p_new_status, status),
        updated_at = NOW(),
        started_at = CASE 
            WHEN p_new_status = 'in_progress' AND started_at IS NULL THEN NOW()
            ELSE started_at
        END,
        completed_at = CASE 
            WHEN p_new_status = 'completed' THEN NOW()
            ELSE completed_at
        END
    WHERE todo_id = p_todo_id;
    
    -- Log progress
    INSERT INTO shq.orbt_todo_progress (
        progress_id, todo_id, progress_update, completion_percentage_change,
        status_change, updated_by, update_type, time_spent_minutes,
        blocking_issues, next_steps
    ) VALUES (
        v_progress_id, p_todo_id, p_progress_update, v_percentage_change,
        p_new_status, 'claude-code', 
        CASE 
            WHEN p_new_status IS NOT NULL THEN 'status_change'
            WHEN p_blocking_issues IS NOT NULL THEN 'blocking_issue'
            ELSE 'progress'
        END,
        p_time_spent_minutes, p_blocking_issues, p_next_steps
    );
    
    RETURN 'Todo ' || p_todo_id || ' updated successfully. Progress: ' || 
           COALESCE(p_completion_percentage, v_old_percentage) || '%';
END;
$$ LANGUAGE plpgsql;
```

### 3. Todo Dashboard View
```sql
-- View for displaying current project todos
CREATE VIEW shq.todo_dashboard AS
SELECT 
    t.todo_id,
    t.project_name,
    t.todo_title,
    t.todo_category,
    t.status,
    t.priority,
    t.completion_percentage,
    t.estimated_minutes,
    t.actual_minutes,
    CASE 
        WHEN t.status = 'completed' THEN '✅'
        WHEN t.status = 'in_progress' THEN '🔄'
        WHEN t.status = 'blocked' THEN '🚫'
        ELSE '⏳'
    END as status_emoji,
    CASE t.priority
        WHEN 'CRITICAL' THEN '🔥'
        WHEN 'HIGH' THEN '🔴'
        WHEN 'MEDIUM' THEN '🟡'
        WHEN 'LOW' THEN '🟢'
    END as priority_emoji,
    EXTRACT(EPOCH FROM (NOW() - t.created_at))/60 as age_minutes,
    t.related_doctrine_sections,
    -- Latest progress update
    (SELECT progress_update FROM shq.orbt_todo_progress p 
     WHERE p.todo_id = t.todo_id 
     ORDER BY p.created_at DESC LIMIT 1) as latest_update
FROM shq.orbt_project_todos t
WHERE t.status != 'cancelled'
ORDER BY 
    CASE t.priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2  
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END,
    t.created_at;
```

---

## Default Todo Generation Rules

### 1. Setup and Configuration Todos
```sql
-- Rule for HEIR system setup
INSERT INTO shq.orbt_todo_generation_rules (
    rule_id, rule_name, rule_description,
    trigger_keywords, project_types, 
    todo_template
) VALUES (
    'HEIR_SETUP', 'HEIR System Setup', 'Generates setup todos for new HEIR projects',
    ARRAY['setup', 'configure', 'initialize', 'deploy'],
    ARRAY['heir_project'],
    '{
        "title": "Setup HEIR System",
        "description": "Deploy database schema, configure agents, and initialize {requirement}",
        "category": "setup",
        "priority": "HIGH", 
        "estimated_minutes": 30,
        "orbt_stage": "build"
    }'::JSONB
);

-- Rule for database setup
INSERT INTO shq.orbt_todo_generation_rules (
    rule_id, rule_name, rule_description,
    trigger_keywords, project_types,
    todo_template
) VALUES (
    'DATABASE_SETUP', 'Database Setup', 'Generates database-related todos',
    ARRAY['database', 'schema', 'migration', 'neon'],
    NULL, -- Applies to all project types
    '{
        "title": "Setup Database Schema", 
        "description": "Deploy database schema and run migrations for {requirement}",
        "category": "setup",
        "priority": "HIGH",
        "estimated_minutes": 15,
        "orbt_stage": "build"
    }'::JSONB
);

-- Rule for doctrine migration
INSERT INTO shq.orbt_todo_generation_rules (
    rule_id, rule_name, rule_description,
    trigger_keywords, project_types,
    todo_template
) VALUES (
    'DOCTRINE_MIGRATION', 'Doctrine Migration', 'Generates doctrine migration todos',
    ARRAY['doctrine', 'dpr_doctrine', 'behavioral rules'],
    ARRAY['heir_project'],
    '{
        "title": "Migrate DPR Doctrine",
        "description": "Run shq.migrate_dpr_doctrine_exact() to import {requirement}",
        "category": "setup",
        "priority": "MEDIUM",
        "estimated_minutes": 10,
        "orbt_stage": "build"
    }'::JSONB
);
```

---

## Claude Code Integration Examples

### 1. Automatic Todo Creation
```javascript
// When Claude starts a new HEIR project
async function startHeirProject(projectConfig) {
    // Generate todos automatically
    const todos = await generateProjectTodos(
        projectConfig.project_name,
        projectConfig.project_type,
        projectConfig.requirements,
        getCurrentSessionId()
    );
    
    console.log('📝 Generated Todo List:');
    todos.forEach(todo => {
        console.log(`${todo.priority_emoji} ${todo.todo_title} (${todo.estimated_minutes} min)`);
    });
    
    return todos;
}

// Example usage
const project = {
    project_name: 'E-commerce Platform',
    project_type: 'heir_project',
    requirements: [
        'Setup HEIR system with database schema',
        'Configure payment processing with Stripe',
        'Migrate existing DPR doctrine for compliance',
        'Deploy to production with monitoring'
    ]
};

// Automatically generates:
// 🔴 Setup HEIR System (30 min)
// 🔴 Setup Database Schema (15 min) 
// 🟡 Migrate DPR Doctrine (10 min)
// 🟡 Configure Payment Processing (45 min)
// 🟡 Deploy with Monitoring (20 min)
```

### 2. Real-time Progress Updates
```javascript
// Claude updates todos as work progresses
async function updateTodoProgress(todoId, update) {
    await db.query(`
        SELECT shq.update_todo_progress($1, $2, $3, $4, $5)
    `, [
        todoId,
        update.progress_description,
        update.completion_percentage,
        update.new_status,
        update.time_spent
    ]);
    
    // Show updated dashboard
    const dashboard = await getTodoDashboard();
    console.log('📊 Updated Todo Dashboard:');
    dashboard.forEach(todo => {
        console.log(`${todo.status_emoji} ${todo.todo_title} - ${todo.completion_percentage}%`);
    });
}

// Example: Claude completes database setup
updateTodoProgress('TODO-20250113120001', {
    progress_description: 'Database schema deployed successfully to Neon',
    completion_percentage: 100,
    new_status: 'completed',
    time_spent: 12
});
```

### 3. Todo Dashboard Display
```javascript
// Function to show current todo status
async function showTodoDashboard(projectName) {
    const todos = await db.query(`
        SELECT * FROM shq.todo_dashboard 
        WHERE project_name = $1 
        ORDER BY priority_emoji, completion_percentage
    `, [projectName]);
    
    console.log(`📋 ${projectName} Todo Dashboard:`);
    console.log('═'.repeat(50));
    
    todos.forEach(todo => {
        const progress = '█'.repeat(Math.floor(todo.completion_percentage / 10)) + 
                        '░'.repeat(10 - Math.floor(todo.completion_percentage / 10));
        
        console.log(`${todo.status_emoji} ${todo.priority_emoji} ${todo.todo_title}`);
        console.log(`   Progress: [${progress}] ${todo.completion_percentage}%`);
        
        if (todo.latest_update) {
            console.log(`   Latest: ${todo.latest_update}`);
        }
        console.log('');
    });
}
```

---

## Integration with heir-drop-in.js

### Add Todo System to Automatic Setup
```javascript
// Add to heir-drop-in.js
const todoSystemSchema = `
-- Todo List Management System
CREATE SEQUENCE IF NOT EXISTS todo_sequence;
CREATE SEQUENCE IF NOT EXISTS progress_sequence;

-- Project todos table
CREATE TABLE IF NOT EXISTS shq.orbt_project_todos (
    id SERIAL PRIMARY KEY,
    todo_id VARCHAR(50) UNIQUE NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    project_session VARCHAR(50) NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    todo_title VARCHAR(200) NOT NULL,
    todo_description TEXT NULL,
    todo_category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    completion_percentage INTEGER DEFAULT 0,
    estimated_minutes INTEGER NULL,
    assigned_to VARCHAR(100) NULL,
    created_by VARCHAR(100) NOT NULL,
    related_doctrine_sections VARCHAR(20)[] NULL,
    orbt_stage VARCHAR(20) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_todos_project ON shq.orbt_project_todos(project_name);
CREATE INDEX IF NOT EXISTS idx_todos_status ON shq.orbt_project_todos(status);
CREATE INDEX IF NOT EXISTS idx_todos_priority ON shq.orbt_project_todos(priority);
`;

// Write schema to file
fs.writeFileSync('.heir/database_schemas/todo-schema.sql', todoSystemSchema);
console.log('✅ AUTOMATIC: Todo list management for Claude Code projects');
console.log('✅ AUTOMATIC: Progress tracking and task organization');
console.log('✅ AUTOMATIC: Multi-step project task generation');
```

---

## Benefits

### For Claude Code Sessions
- **Organized task management** - Never lose track of complex projects
- **Progress visibility** - Clear status on all project components
- **Dependency tracking** - Understand task relationships
- **Time estimation** - Better project planning and estimation

### For Users
- **Complete transparency** - See exactly what Claude is working on
- **Progress updates** - Real-time status on project completion
- **Task prioritization** - Understand what's critical vs optional
- **Historical tracking** - Review how projects were completed

### For HEIR System
- **Systematic execution** - Ensures all steps are completed
- **Quality assurance** - Nothing gets missed in complex projects
- **Learning improvement** - Track what tasks take longest
- **Doctrine compliance** - Link tasks to specific doctrine requirements

---

*Now Claude Code automatically generates and maintains organized todo lists for every HEIR project, ensuring systematic completion and transparent progress tracking.*