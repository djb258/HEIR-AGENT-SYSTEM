# HEIR Platform Quick Start
**Get HEIR platform running in 5 minutes**

## 1. Prerequisites Check
```bash
# Check you have required tools
node --version    # Need 16+
psql --version   # Need PostgreSQL client
git --version    # Need Git
```

## 2. Clone & Set Environment
```bash
git clone https://github.com/djb258/HEIR-AGENT-SYSTEM.git
cd HEIR-AGENT-SYSTEM

# Set your database URL (REQUIRED)
export DATABASE_URL="postgresql://username:password@host:port/database"
```

## 3. Deploy Platform
```bash
# Deploy database schema
bash scripts/deploy-database.sh

# Initialize platform
node heir-drop-in.js
```

## 4. Verify Success
You should see:
```
✅ Schema version 1.0.0 deployed successfully
✅ All critical tables verified
✅ ORBT system functional
🎉 HEIR System Database Deployment Complete!
```

## 5. Quick Test
```bash
# Test doctrine header enforcement
curl -X POST http://localhost:3000/test-endpoint \
  -H "unique_id: TEST.01.PROC.API.10000.001" \
  -H "process_id: TestOperation" \
  -H "blueprint_id: quick-start-test" \
  -H "agent_signature: test:$(date +%Y%m%d%H%M%S):abc123"
```

## Next Steps
- Read [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) for detailed integration
- Configure your application to use doctrine headers
- Set up monitoring and alerts

## Need Help?
- Check logs: All scripts provide detailed error messages
- Validate config: Use provided .env.example template
- Test database: `psql $DATABASE_URL -c "SELECT version();"`

**That's it! Your HEIR platform is ready for application integration.** 🚀