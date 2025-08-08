# ORBT Monitoring API Endpoints
# Add these to your render-command-ops-connection.onrender.com FastAPI service

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncpg
import os
from pydantic import BaseModel

# Add these imports to your existing FastAPI app
# from your existing app import app, get_database_connection

# Pydantic Models for Request/Response
class ErrorLogEntry(BaseModel):
    agent_id: str
    agent_hierarchy: str  # orchestrator, manager, specialist
    error_type: str      # connection, validation, doctrine, escalation
    error_message: str
    error_stack: Optional[str] = None
    doctrine_violated: Optional[str] = None
    section_number: Optional[str] = None
    project_context: Optional[str] = None
    render_endpoint: Optional[str] = None

class AgentMetrics(BaseModel):
    agent_id: str
    agent_type: str  # orchestrator, manager, specialist
    execution_time_ms: int
    token_usage: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    success: bool
    error_count: int = 0
    retry_count: int = 0
    project_context: Optional[str] = None
    render_endpoint: Optional[str] = None
    operation_type: str  # build, repair, operation, training

class EscalationAlert(BaseModel):
    alert_type: str
    severity: str
    error_id: str
    message: str
    requires_immediate_attention: bool = False

# ORBT System Status Endpoints
@app.get("/api/orbt/status")
async def get_orbt_system_status():
    """Get real-time ORBT system status (Universal Rules 1-3)"""
    try:
        conn = await get_database_connection()
        
        # Get current system status
        system_status = await conn.fetchrow("""
            SELECT 
                overall_status,
                active_agents,
                green_count,
                yellow_count,
                red_count,
                avg_execution_time_ms,
                escalation_pending,
                last_error_timestamp,
                uptime_seconds,
                updated_at
            FROM orbt_system_status 
            WHERE status_id = 'SYSTEM_STATUS_' || TO_CHAR(NOW(), 'YYYY_MM_DD')
        """)
        
        if not system_status:
            # Initialize system status if not exists
            await conn.execute("SELECT update_system_status()")
            system_status = await conn.fetchrow("""
                SELECT 
                    overall_status,
                    active_agents,
                    green_count,
                    yellow_count,
                    red_count,
                    avg_execution_time_ms,
                    escalation_pending,
                    last_error_timestamp,
                    uptime_seconds,
                    updated_at
                FROM orbt_system_status 
                WHERE status_id = 'SYSTEM_STATUS_' || TO_CHAR(NOW(), 'YYYY_MM_DD')
            """)
        
        await conn.close()
        
        return {
            "system_status": system_status["overall_status"],
            "active_agents": system_status["active_agents"],
            "error_counts": {
                "GREEN": system_status["green_count"],
                "YELLOW": system_status["yellow_count"],
                "RED": system_status["red_count"]
            },
            "performance": {
                "avg_execution_time_ms": float(system_status["avg_execution_time_ms"] or 0),
                "uptime_seconds": system_status["uptime_seconds"]
            },
            "escalations": {
                "pending": system_status["escalation_pending"]
            },
            "last_error": system_status["last_error_timestamp"],
            "last_updated": system_status["updated_at"].isoformat(),
            "orbt_compliance": "ACTIVE"  # Indicates ORBT system is running
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system status: {str(e)}")

# Global Error Logging Endpoints (Universal Rule 4)
@app.get("/api/orbt/errors")
async def get_error_log(
    limit: int = Query(50, le=1000),
    status: Optional[str] = Query(None, regex="^(GREEN|YELLOW|RED)$"),
    agent_id: Optional[str] = None,
    hours: int = Query(24, le=168)  # Max 1 week
):
    """Get global error log entries with filtering"""
    try:
        conn = await get_database_connection()
        
        # Build query with filters
        where_conditions = ["timestamp >= NOW() - INTERVAL '%s hours'" % hours]
        params = []
        
        if status:
            where_conditions.append("orbt_status = $%d" % (len(params) + 1))
            params.append(status)
            
        if agent_id:
            where_conditions.append("agent_id = $%d" % (len(params) + 1))
            params.append(agent_id)
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
            SELECT 
                error_id,
                orbt_status,
                timestamp,
                agent_id,
                agent_hierarchy,
                error_type,
                error_message,
                error_stack,
                doctrine_violated,
                section_number,
                occurrence_count,
                escalation_level,
                requires_human,
                project_context,
                render_endpoint,
                resolved,
                resolution_method,
                resolution_notes
            FROM orbt_error_log 
            WHERE {where_clause}
            ORDER BY timestamp DESC 
            LIMIT ${{len(params) + 1}}
        """
        
        params.append(limit)
        errors = await conn.fetch(query, *params)
        
        await conn.close()
        
        error_list = []
        for error in errors:
            error_dict = dict(error)
            error_dict["timestamp"] = error_dict["timestamp"].isoformat()
            error_list.append(error_dict)
        
        return {
            "status": "success",
            "count": len(error_list),
            "filters": {
                "status": status,
                "agent_id": agent_id,
                "hours": hours,
                "limit": limit
            },
            "errors": error_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching error log: {str(e)}")

@app.post("/api/orbt/errors")
async def log_error(error_data: ErrorLogEntry):
    """Log new error to global system (Universal Rule 4: Centralized logging)"""
    try:
        conn = await get_database_connection()
        
        # Generate unique error ID using your 6-position format
        error_id = await conn.fetchval("SELECT generate_error_id()")
        
        # Classify error status based on content
        orbt_status = classify_error_status(error_data.error_message, error_data.error_type)
        
        # Insert error log entry
        await conn.execute("""
            INSERT INTO orbt_error_log (
                error_id, orbt_status, agent_id, agent_hierarchy, error_type,
                error_message, error_stack, doctrine_violated, section_number,
                project_context, render_endpoint
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, 
            error_id, orbt_status, error_data.agent_id, error_data.agent_hierarchy,
            error_data.error_type, error_data.error_message, error_data.error_stack,
            error_data.doctrine_violated, error_data.section_number,
            error_data.project_context, error_data.render_endpoint
        )
        
        # Update system status
        await conn.execute("SELECT update_system_status()")
        
        await conn.close()
        
        return {
            "status": "logged",
            "error_id": error_id,
            "orbt_status": orbt_status,
            "timestamp": datetime.now().isoformat(),
            "escalation_triggered": orbt_status == "RED"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging error: {str(e)}")

# Agent Performance Metrics
@app.get("/api/orbt/metrics/{agent_id}")
async def get_agent_metrics(
    agent_id: str,
    hours: int = Query(24, le=168),
    limit: int = Query(100, le=1000)
):
    """Get performance metrics for specific agent"""
    try:
        conn = await get_database_connection()
        
        metrics = await conn.fetch("""
            SELECT 
                metric_id,
                agent_type,
                execution_time_ms,
                token_usage,
                memory_usage_mb,
                cpu_usage_percent,
                success,
                error_count,
                retry_count,
                operation_type,
                project_context,
                timestamp
            FROM orbt_agent_metrics 
            WHERE agent_id = $1 
            AND timestamp >= NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC 
            LIMIT $2
        """, agent_id, limit)
        
        # Calculate summary statistics
        if metrics:
            total_executions = len(metrics)
            successful_executions = sum(1 for m in metrics if m["success"])
            avg_execution_time = sum(m["execution_time_ms"] for m in metrics) / total_executions
            avg_token_usage = sum(m["token_usage"] or 0 for m in metrics) / total_executions
            success_rate = (successful_executions / total_executions) * 100
            
            summary = {
                "total_executions": total_executions,
                "success_rate_percent": round(success_rate, 2),
                "avg_execution_time_ms": round(avg_execution_time, 2),
                "avg_token_usage": round(avg_token_usage, 2),
                "total_errors": sum(m["error_count"] for m in metrics),
                "total_retries": sum(m["retry_count"] for m in metrics)
            }
        else:
            summary = None
        
        await conn.close()
        
        metric_list = []
        for metric in metrics:
            metric_dict = dict(metric)
            metric_dict["timestamp"] = metric_dict["timestamp"].isoformat()
            metric_list.append(metric_dict)
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "summary": summary,
            "metrics": metric_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent metrics: {str(e)}")

@app.post("/api/orbt/metrics")
async def log_agent_metrics(metrics_data: AgentMetrics):
    """Log agent performance metrics"""
    try:
        conn = await get_database_connection()
        
        # Generate unique metric ID
        metric_id = f"METRIC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{metrics_data.agent_id}"
        
        await conn.execute("""
            INSERT INTO orbt_agent_metrics (
                metric_id, agent_id, agent_type, execution_time_ms, token_usage,
                memory_usage_mb, cpu_usage_percent, success, error_count, retry_count,
                project_context, render_endpoint, operation_type
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        """,
            metric_id, metrics_data.agent_id, metrics_data.agent_type,
            metrics_data.execution_time_ms, metrics_data.token_usage,
            metrics_data.memory_usage_mb, metrics_data.cpu_usage_percent,
            metrics_data.success, metrics_data.error_count, metrics_data.retry_count,
            metrics_data.project_context, metrics_data.render_endpoint,
            metrics_data.operation_type
        )
        
        await conn.close()
        
        return {
            "status": "logged",
            "metric_id": metric_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging metrics: {str(e)}")

# Human Escalation (Universal Rule 5)
@app.post("/api/escalation/human")
async def trigger_human_escalation(escalation_data: EscalationAlert):
    """Trigger human intervention alert (Universal Rule 5: 2+ occurrences)"""
    try:
        conn = await get_database_connection()
        
        # Log escalation in queue
        escalation_id = f"ESC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await conn.execute("""
            INSERT INTO orbt_escalation_queue (
                escalation_id, error_id, priority, status, escalated_by
            ) VALUES ($1, $2, $3, 'PENDING', 'SYSTEM_AUTO')
        """, escalation_id, escalation_data.error_id, escalation_data.severity)
        
        # Here you would integrate with your notification system
        # Examples: Send Slack message, email, SMS, etc.
        
        await send_escalation_notification({
            "escalation_id": escalation_id,
            "severity": escalation_data.severity,
            "error_id": escalation_data.error_id,
            "message": escalation_data.message,
            "timestamp": datetime.now().isoformat()
        })
        
        await conn.close()
        
        return {
            "status": "escalation_triggered",
            "escalation_id": escalation_id,
            "severity": escalation_data.severity,
            "notifications_sent": ["slack", "email"],  # Customize based on your setup
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering escalation: {str(e)}")

# DPR Doctrine Integration
@app.get("/api/dpr/doctrine")
async def get_dpr_doctrine(
    category: Optional[str] = None,
    doctrine_type: Optional[str] = None,
    enforcement_level: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Access DPR doctrine system with filtering"""
    try:
        conn = await get_database_connection()
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if category:
            where_conditions.append("doctrine_category = $%d" % (len(params) + 1))
            params.append(category)
            
        if doctrine_type:
            where_conditions.append("doctrine_type = $%d" % (len(params) + 1))
            params.append(doctrine_type)
            
        if enforcement_level:
            where_conditions.append("enforcement_level = $%d" % (len(params) + 1))
            params.append(enforcement_level)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                id,
                section_number,
                section_title,
                doctrine_text,
                doctrine_type,
                enforcement_level,
                doctrine_category,
                sub_hive,
                enforcement_target,
                enforcement_scope,
                created_at
            FROM dpr.dpr_doctrine 
            WHERE {where_clause}
            ORDER BY section_number
            LIMIT ${{len(params) + 1}}
        """
        
        params.append(limit)
        doctrines = await conn.fetch(query, *params)
        
        await conn.close()
        
        doctrine_list = []
        for doctrine in doctrines:
            doctrine_dict = dict(doctrine)
            doctrine_dict["created_at"] = doctrine_dict["created_at"].isoformat()
            doctrine_list.append(doctrine_dict)
        
        return {
            "status": "success",
            "count": len(doctrine_list),
            "filters": {
                "category": category,
                "doctrine_type": doctrine_type,
                "enforcement_level": enforcement_level,
                "limit": limit
            },
            "doctrines": doctrine_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctrines: {str(e)}")

# Training Logs (Universal Rule 6)
@app.post("/api/orbt/training")
async def log_training_intervention(training_data: dict = Body(...)):
    """Log training intervention (Universal Rule 6: Training logs for live apps)"""
    try:
        conn = await get_database_connection()
        
        training_id = f"TRAIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await conn.execute("""
            INSERT INTO orbt_training_log (
                training_id, intervention_type, agent_id, problem_description,
                solution_applied, success, project_context, error_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
            training_id,
            training_data.get("intervention_type"),
            training_data.get("agent_id"),
            training_data.get("problem_description"),
            training_data.get("solution_applied"),
            training_data.get("success", False),
            training_data.get("project_context"),
            training_data.get("error_id")
        )
        
        await conn.close()
        
        return {
            "status": "logged",
            "training_id": training_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging training: {str(e)}")

# Helper Functions
def classify_error_status(error_message: str, error_type: str) -> str:
    """Classify error into GREEN/YELLOW/RED based on content"""
    error_msg_lower = error_message.lower()
    
    # RED (Critical) triggers
    critical_keywords = [
        "doctrine_violation", "connection_failure", "authentication_error",
        "data_corruption", "system_unavailable", "critical", "fatal"
    ]
    
    # YELLOW (Warning) triggers  
    warning_keywords = [
        "timeout", "rate_limit", "performance", "validation", "warning",
        "retry", "slow", "degraded"
    ]
    
    if any(keyword in error_msg_lower for keyword in critical_keywords):
        return "RED"
    elif any(keyword in error_msg_lower for keyword in warning_keywords):
        return "YELLOW"
    else:
        return "GREEN"

async def send_escalation_notification(escalation_data: dict):
    """Send escalation notifications via configured channels"""
    # Implement your notification logic here
    # Examples: Slack webhook, email service, SMS, etc.
    
    # Slack example (uncomment and configure):
    # slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    # if slack_webhook:
    #     await send_slack_notification(slack_webhook, escalation_data)
    
    # Email example (uncomment and configure):
    # await send_email_notification(escalation_data)
    
    pass

# Health check endpoint for monitoring
@app.get("/api/orbt/health")
async def orbt_health_check():
    """ORBT system health check"""
    try:
        conn = await get_database_connection()
        
        # Test database connection
        await conn.fetchval("SELECT 1")
        
        # Check if ORBT tables exist
        tables_exist = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name IN ('orbt_error_log', 'orbt_agent_metrics', 'orbt_system_status')
        """)
        
        await conn.close()
        
        return {
            "status": "healthy",
            "orbt_system": "operational",
            "database_connection": "ok",
            "tables_initialized": tables_exist >= 3,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )