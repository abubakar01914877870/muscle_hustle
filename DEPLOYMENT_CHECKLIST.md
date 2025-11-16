# Production Deployment Checklist

## Pre-Deployment

### Environment Setup
- [ ] Set `MONGO_URI` environment variable
- [ ] Set `MONGO_DBNAME` environment variable  
- [ ] Set `SECRET_KEY` environment variable (generate new one!)
- [ ] Set `FLASK_ENV=production`
- [ ] Install all dependencies: `pip install -r requirements.txt`

### MongoDB Configuration
- [ ] Create MongoDB Atlas account
- [ ] Create production cluster
- [ ] Configure network access (whitelist server IP)
- [ ] Create database user with strong password
- [ ] Get connection string
- [ ] Test connection

### Security
- [ ] Generate new SECRET_KEY (don't use default!)
- [ ] Change default admin password
- [ ] Enable HTTPS/SSL
- [ ] Restrict MongoDB network access
- [ ] Review firewall rules

## Deployment

### Application Deployment
- [ ] Upload code to server
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure WSGI/Gunicorn
- [ ] Set up web server (Nginx/Apache)
- [ ] Configure static files

### Database Initialization
- [ ] Run `python init_db.py`
- [ ] Verify indexes created
- [ ] Verify admin user created
- [ ] Test database connection

## Post-Deployment

### Testing
- [ ] Test login/logout
- [ ] Test user registration
- [ ] Test profile picture upload
- [ ] Test exercise creation with image
- [ ] Test exercise creation with YouTube video
- [ ] Test progress tracker with photo
- [ ] Test admin features
- [ ] Test on mobile devices

### Security Tasks
- [ ] Login as admin (super@admin.com / 1234qa)
- [ ] Change admin password immediately
- [ ] Create additional admin users if needed
- [ ] Review user permissions

### Monitoring Setup
- [ ] Set up error logging
- [ ] Configure uptime monitoring
- [ ] Set up MongoDB Atlas alerts
- [ ] Configure backup schedule
- [ ] Test backup/restore process

### Documentation
- [ ] Document deployment process
- [ ] Document environment variables
- [ ] Document admin procedures
- [ ] Create runbook for common issues

## Verification

### Functionality Check
- [ ] All pages load correctly
- [ ] Images display properly
- [ ] Forms submit successfully
- [ ] Authentication works
- [ ] Admin features accessible
- [ ] Progress chart displays data

### Performance Check
- [ ] Page load times acceptable
- [ ] Image upload works smoothly
- [ ] Database queries fast
- [ ] No memory leaks
- [ ] No error messages in logs

### Security Check
- [ ] HTTPS enabled
- [ ] Admin password changed
- [ ] MongoDB access restricted
- [ ] No sensitive data in logs
- [ ] Error pages don't expose info

## Maintenance

### Regular Tasks
- [ ] Monitor database size
- [ ] Review error logs weekly
- [ ] Check backup success
- [ ] Update dependencies monthly
- [ ] Review user activity

### Emergency Contacts
- MongoDB Atlas Support: https://support.mongodb.com/
- Hosting Provider Support: [Your provider]
- Application Developer: [Your contact]

## Rollback Plan

If something goes wrong:
- [ ] Keep old version accessible
- [ ] Have database backup ready
- [ ] Document rollback steps
- [ ] Test rollback procedure

## Notes

**Important URLs:**
- Production URL: _______________
- MongoDB Atlas: https://cloud.mongodb.com/
- Admin Panel: _______________/admin/users

**Credentials Location:**
- Environment variables: _______________
- MongoDB credentials: _______________
- Admin credentials: _______________

**Deployment Date:** _______________
**Deployed By:** _______________
**Version:** _______________

---

## Quick Reference

### Start Application
```bash
# PythonAnywhere: Click "Reload" button
# Heroku: git push heroku main
# VPS: sudo systemctl start muscle-hustle
```

### View Logs
```bash
# PythonAnywhere: Check error log in Files tab
# Heroku: heroku logs --tail
# VPS: sudo journalctl -u muscle-hustle -f
```

### Restart Application
```bash
# PythonAnywhere: Click "Reload" button
# Heroku: heroku restart
# VPS: sudo systemctl restart muscle-hustle
```

### Database Backup
```bash
mongodump --uri="$MONGO_URI" --out=backup
```

### Check Application Status
```bash
# Visit: https://your-domain.com
# Should see login page
```

---

**✅ Deployment Complete!**

Remember to:
1. Change default admin password
2. Set up monitoring
3. Configure backups
4. Test all features
5. Monitor for first 24 hours
