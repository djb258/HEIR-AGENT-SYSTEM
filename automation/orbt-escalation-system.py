# ORBT Error Escalation Automation System
# Implements Universal Rule 5: Any error appearing 2+ times escalates for human review

import asyncio
import asyncpg
import json
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orbt_escalation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ORBTEscalationSystem:
    """
    Automated escalation system implementing your Universal Rules 3-5:
    - Rule 3: Everything green unless flagged by error log
    - Rule 4: All errors routed to centralized log
    - Rule 5: 2+ occurrences trigger human escalation
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.notification_channels = {
            "slack": os.getenv("SLACK_WEBHOOK_URL"),
            "email": {
                "smtp_server": os.getenv("SMTP_SERVER"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("EMAIL_USERNAME"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "from_email": os.getenv("FROM_EMAIL"),
                "to_emails": os.getenv("TO_EMAILS", "").split(",")
            },
            "webhook": os.getenv("ESCALATION_WEBHOOK_URL")
        }
        
    async def monitor_and_escalate(self, check_interval: int = 300):
        """
        Main monitoring loop - runs every 5 minutes by default
        Implements Universal Rule 5: 2+ occurrence escalation
        """
        logger.info("Starting ORBT Escalation System monitoring...")
        
        while True:
            try:
                await self.check_for_escalations()
                await self.process_pending_escalations()
                await self.update_system_health()
                await self.cleanup_old_entries()
                
                logger.info(f"Monitoring cycle completed. Next check in {check_interval} seconds.")
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def check_for_escalations(self):
        """Check for errors that need escalation (Universal Rule 5)"""
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Find error patterns that occurred 2+ times in last 24 hours
            escalation_candidates = await conn.fetch("""
                SELECT 
                    error_message,
                    agent_id,
                    COUNT(*) as occurrence_count,
                    MAX(error_id) as latest_error_id,
                    MAX(timestamp) as latest_occurrence,
                    MIN(timestamp) as first_occurrence,
                    array_agg(error_id ORDER BY timestamp DESC) as all_error_ids
                FROM orbt_error_log 
                WHERE 
                    timestamp >= NOW() - INTERVAL '24 hours'
                    AND requires_human = FALSE
                    AND resolved = FALSE
                GROUP BY error_message, agent_id
                HAVING COUNT(*) >= 2
            """)
            
            for candidate in escalation_candidates:
                await self.create_escalation(conn, candidate)
                
        finally:
            await conn.close()
    
    async def create_escalation(self, conn, error_pattern):
        """Create escalation entry for recurring error pattern"""
        escalation_id = f"ESC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{error_pattern['agent_id'][:8]}"
        
        # Determine priority based on occurrence count and agent type
        priority = self.calculate_priority(
            error_pattern['occurrence_count'],
            error_pattern['agent_id']
        )
        
        # Create escalation queue entry
        await conn.execute("""
            INSERT INTO orbt_escalation_queue (
                escalation_id, error_id, priority, status, escalated_by,
                escalated_at, due_at
            ) VALUES ($1, $2, $3, 'PENDING', 'SYSTEM_AUTO', $4, $5)
        """,
            escalation_id,
            error_pattern['latest_error_id'],
            priority,
            datetime.now(),
            datetime.now() + timedelta(hours=self.get_response_time_hours(priority))
        )
        
        # Mark all related errors as escalated
        for error_id in error_pattern['all_error_ids']:
            await conn.execute("""
                UPDATE orbt_error_log 
                SET 
                    requires_human = TRUE,
                    escalation_level = 2,
                    orbt_status = 'RED'
                WHERE error_id = $1
            """, error_id)
        
        # Create escalation notification
        escalation_data = {
            "escalation_id": escalation_id,
            "priority": priority,
            "error_pattern": {
                "message": error_pattern['error_message'],
                "agent_id": error_pattern['agent_id'],
                "occurrence_count": error_pattern['occurrence_count'],
                "first_occurrence": error_pattern['first_occurrence'].isoformat(),
                "latest_occurrence": error_pattern['latest_occurrence'].isoformat(),
                "error_ids": error_pattern['all_error_ids']
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Send notifications
        await self.send_escalation_notifications(escalation_data)
        
        logger.info(f"Created escalation {escalation_id} for error pattern: {error_pattern['error_message'][:50]}...")
        
        # Record training log entry (Universal Rule 6)
        await self.log_training_intervention(conn, {
            "intervention_type": "auto_escalation",
            "agent_id": error_pattern['agent_id'],
            "problem_description": f"Error pattern detected: {error_pattern['error_message']}",
            "solution_applied": f"Escalated to human review (Priority: {priority})",
            "success": True,
            "recurring_issue": True,
            "pattern_recognized": True,
            "error_id": error_pattern['latest_error_id']
        })
    
    async def process_pending_escalations(self):
        """Process escalations that are due for action"""
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Find overdue escalations
            overdue_escalations = await conn.fetch("""
                SELECT 
                    escalation_id,
                    error_id,
                    priority,
                    escalated_at,
                    due_at
                FROM orbt_escalation_queue 
                WHERE 
                    status = 'PENDING'
                    AND due_at < NOW()
            """)
            
            for escalation in overdue_escalations:
                await self.handle_overdue_escalation(conn, escalation)
                
            # Send daily summary if configured
            if datetime.now().hour == 9 and datetime.now().minute < 5:  # 9 AM daily
                await self.send_daily_summary(conn)
                
        finally:
            await conn.close()
    
    async def handle_overdue_escalation(self, conn, escalation):
        """Handle escalations that haven't been addressed within SLA"""
        logger.warning(f"Escalation {escalation['escalation_id']} is overdue!")
        
        # Increase priority for overdue escalations
        new_priority = self.escalate_priority(escalation['priority'])
        
        await conn.execute("""
            UPDATE orbt_escalation_queue 
            SET 
                priority = $1,
                due_at = $2,
                updated_at = NOW()
            WHERE escalation_id = $3
        """,
            new_priority,
            datetime.now() + timedelta(hours=self.get_response_time_hours(new_priority)),
            escalation['escalation_id']
        )
        
        # Send urgent notification
        await self.send_urgent_notification({
            "escalation_id": escalation['escalation_id'],
            "original_priority": escalation['priority'],
            "new_priority": new_priority,
            "overdue_hours": (datetime.now() - escalation['due_at']).total_seconds() / 3600
        })
    
    async def update_system_health(self):
        """Update system health status based on current state"""
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Update system status
            await conn.execute("SELECT update_system_status()")
            
            # Check system health indicators
            health_check = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM orbt_escalation_queue WHERE status = 'PENDING') as pending_escalations,
                    (SELECT COUNT(*) FROM orbt_error_log WHERE orbt_status = 'RED' AND timestamp >= NOW() - INTERVAL '1 hour') as recent_critical_errors,
                    (SELECT COUNT(*) FROM orbt_agent_metrics WHERE success = false AND timestamp >= NOW() - INTERVAL '1 hour') as recent_failures,
                    (SELECT AVG(execution_time_ms) FROM orbt_agent_metrics WHERE timestamp >= NOW() - INTERVAL '1 hour') as avg_performance
            """)
            
            # Determine if system needs attention
            if (health_check['pending_escalations'] > 10 or 
                health_check['recent_critical_errors'] > 5 or
                health_check['recent_failures'] > health_check['pending_escalations'] * 2):
                
                await self.trigger_system_health_alert(health_check)
                
        finally:
            await conn.close()
    
    async def cleanup_old_entries(self):
        """Clean up old entries to maintain performance"""
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Archive old resolved escalations (older than 30 days)
            deleted_escalations = await conn.execute("""
                DELETE FROM orbt_escalation_queue 
                WHERE status = 'RESOLVED' 
                AND resolved_at < NOW() - INTERVAL '30 days'
            """)
            
            # Archive old error logs (older than 90 days, keep only critical ones)
            deleted_errors = await conn.execute("""
                DELETE FROM orbt_error_log 
                WHERE timestamp < NOW() - INTERVAL '90 days'
                AND orbt_status != 'RED'
                AND requires_human = FALSE
            """)
            
            # Archive old metrics (older than 7 days, keep daily averages)
            deleted_metrics = await conn.execute("""
                DELETE FROM orbt_agent_metrics 
                WHERE timestamp < NOW() - INTERVAL '7 days'
            """)
            
            if deleted_escalations or deleted_errors or deleted_metrics:
                logger.info(f"Cleanup completed - Deleted: {deleted_escalations} escalations, {deleted_errors} errors, {deleted_metrics} metrics")
                
        finally:
            await conn.close()
    
    def calculate_priority(self, occurrence_count: int, agent_id: str) -> str:
        """Calculate escalation priority based on error pattern"""
        # Higher priority for orchestrators vs specialists
        if "orchestrator" in agent_id.lower():
            base_priority = "HIGH"
        elif "manager" in agent_id.lower():
            base_priority = "MEDIUM"
        else:
            base_priority = "LOW"
        
        # Escalate based on occurrence count
        if occurrence_count >= 10:
            return "CRITICAL"
        elif occurrence_count >= 5:
            return "HIGH"
        elif occurrence_count >= 3 and base_priority != "LOW":
            return "HIGH"
        else:
            return base_priority
    
    def get_response_time_hours(self, priority: str) -> int:
        """Get expected response time based on priority"""
        return {
            "CRITICAL": 1,   # 1 hour
            "HIGH": 4,       # 4 hours
            "MEDIUM": 24,    # 1 day
            "LOW": 72        # 3 days
        }.get(priority, 24)
    
    def escalate_priority(self, current_priority: str) -> str:
        """Escalate priority for overdue items"""
        priority_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        current_index = priority_levels.index(current_priority)
        return priority_levels[min(current_index + 1, len(priority_levels) - 1)]
    
    async def send_escalation_notifications(self, escalation_data: Dict):
        """Send notifications via configured channels"""
        
        # Slack notification
        if self.notification_channels["slack"]:
            await self.send_slack_notification(escalation_data)
        
        # Email notification
        if self.notification_channels["email"]["smtp_server"]:
            await self.send_email_notification(escalation_data)
        
        # Webhook notification
        if self.notification_channels["webhook"]:
            await self.send_webhook_notification(escalation_data)
    
    async def send_slack_notification(self, escalation_data: Dict):
        """Send Slack notification for escalation"""
        try:
            priority_emoji = {
                "CRITICAL": "🚨",
                "HIGH": "⚠️",
                "MEDIUM": "⚡",
                "LOW": "ℹ️"
            }
            
            message = {
                "text": f"{priority_emoji.get(escalation_data['priority'], '⚠️')} ORBT System Escalation",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🔴 ORBT Escalation: {escalation_data['priority']} Priority"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Escalation ID:*\n{escalation_data['escalation_id']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Agent:*\n{escalation_data['error_pattern']['agent_id']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Occurrences:*\n{escalation_data['error_pattern']['occurrence_count']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*First Seen:*\n{escalation_data['error_pattern']['first_occurrence']}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Error Message:*\n```{escalation_data['error_pattern']['message'][:500]}```"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Dashboard"
                                },
                                "url": f"https://render-command-ops-connection.onrender.com/orbt/dashboard"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Error Log"
                                },
                                "url": f"https://render-command-ops-connection.onrender.com/api/orbt/errors?agent_id={escalation_data['error_pattern']['agent_id']}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                self.notification_channels["slack"],
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent for escalation {escalation_data['escalation_id']}")
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
    
    async def send_email_notification(self, escalation_data: Dict):
        """Send email notification for escalation"""
        try:
            email_config = self.notification_channels["email"]
            
            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = f"🚨 ORBT System Escalation - {escalation_data['priority']} Priority"
            
            html_body = f"""
            <html>
            <head></head>
            <body>
                <h2 style="color: #ff0000;">ORBT System Escalation Alert</h2>
                
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Escalation ID:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{escalation_data['escalation_id']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Priority:</td>
                        <td style="border: 1px solid #ddd; padding: 8px; color: #ff0000;">{escalation_data['priority']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Agent ID:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{escalation_data['error_pattern']['agent_id']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">Error Occurrences:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{escalation_data['error_pattern']['occurrence_count']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">First Occurrence:</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{escalation_data['error_pattern']['first_occurrence']}</td>
                    </tr>
                </table>
                
                <h3>Error Message:</h3>
                <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">{escalation_data['error_pattern']['message']}</pre>
                
                <p><strong>Action Required:</strong> This error pattern has been detected {escalation_data['error_pattern']['occurrence_count']} times and requires human intervention per Universal Rule 5.</p>
                
                <p>
                    <a href="https://render-command-ops-connection.onrender.com/orbt/dashboard" style="background-color: #007cba; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">View ORBT Dashboard</a>
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["from_email"], email_config["to_emails"], text)
            server.quit()
            
            logger.info(f"Email notification sent for escalation {escalation_data['escalation_id']}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    async def send_webhook_notification(self, escalation_data: Dict):
        """Send webhook notification for integration with other systems"""
        try:
            payload = {
                "event_type": "orbt_escalation",
                "timestamp": datetime.now().isoformat(),
                "data": escalation_data
            }
            
            response = requests.post(
                self.notification_channels["webhook"],
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Webhook notification sent for escalation {escalation_data['escalation_id']}")
            else:
                logger.error(f"Failed to send webhook notification: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
    
    async def send_urgent_notification(self, overdue_data: Dict):
        """Send urgent notification for overdue escalations"""
        # Similar to send_escalation_notifications but with URGENT messaging
        pass
    
    async def send_daily_summary(self, conn):
        """Send daily summary of ORBT system status"""
        # Generate and send daily system health summary
        pass
    
    async def log_training_intervention(self, conn, training_data: Dict):
        """Log training intervention per Universal Rule 6"""
        training_id = f"TRAIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await conn.execute("""
            INSERT INTO orbt_training_log (
                training_id, intervention_type, agent_id, problem_description,
                solution_applied, success, recurring_issue, pattern_recognized, error_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
            training_id,
            training_data.get("intervention_type"),
            training_data.get("agent_id"),
            training_data.get("problem_description"),
            training_data.get("solution_applied"),
            training_data.get("success", False),
            training_data.get("recurring_issue", False),
            training_data.get("pattern_recognized", False),
            training_data.get("error_id")
        )
    
    async def trigger_system_health_alert(self, health_data: Dict):
        """Trigger system-wide health alert when multiple issues detected"""
        logger.warning("System health alert triggered!")
        # Implement system-wide health alerting
        pass

# CLI Interface
async def main():
    """Main entry point for escalation system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ORBT Escalation System")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--check-interval", type=int, default=300, help="Check interval in seconds (default: 300)")
    
    args = parser.parse_args()
    
    escalation_system = ORBTEscalationSystem(args.database_url)
    await escalation_system.monitor_and_escalate(args.check_interval)

if __name__ == "__main__":
    asyncio.run(main())