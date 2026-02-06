# AutoFINE - Help & Support Guide

## 🆘 Quick Help Topics

### 1. **Server Not Starting?**
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed, or change port in app.py
# Change: port=5000 to port=5001
```

### 2. **Database Issues?**
```bash
# Reset database
cd AutoFINE
rm autofine.db  # or del autofine.db on Windows
python init_database.py
```

### 3. **Can't Access from Other Devices?**
- Check Windows Firewall settings
- Ensure both devices are on same WiFi network
- Verify IP address: `ipconfig` (look for IPv4 Address)
- Try accessing: `http://YOUR_IP:5000`

### 4. **Import Errors?**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### 5. **Want to Deploy Online?**

#### Quick Deploy (5 minutes):
**Heroku** (Recommended):
1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Login: `heroku login`
3. Create Procfile (in AutoFINE folder):
   ```
   web: gunicorn app:app
   ```
4. Add to requirements.txt:
   ```
   gunicorn>=21.2.0
   ```
5. Create app: `heroku create autofine-app`
6. Deploy: `git push heroku main`

**See DEPLOYMENT_GUIDE.md for detailed steps**

### 6. **Need to Change Default Passwords?**
Edit `init_database.py` and change:
- Admin password hash
- Owner password hashes
Then reset database

### 7. **API Key Issues?**
- Gemini API key is already set in code
- For production, use environment variables:
  ```python
  import os
  GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-key')
  ```

### 8. **Want to Use Production Database?**
In `app.py`, change:
```python
# From SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autofine.db'

# To PostgreSQL:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/autofine'

# To MySQL:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:pass@localhost/autofine'
```

### 9. **Feature Not Working?**
- Check browser console (F12) for JavaScript errors
- Check server terminal for Python errors
- Verify database has data: `python init_database.py`

### 10. **Need to Add More Features?**
- All code is in `app.py` (routes)
- Templates in `templates/` folder
- Static files in `static/` folder
- Models in `models.py`

---

## 📞 Common Issues & Solutions

### Issue: "Port already in use"
**Solution**: Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

### Issue: "Module not found"
**Solution**: Install missing package:
```bash
pip install package-name
```

### Issue: "Database locked"
**Solution**: Close all connections, restart server

### Issue: "Can't login"
**Solution**: Reset database and use default credentials:
```bash
rm autofine.db
python init_database.py
# Then use: admin/admin123
```

### Issue: "Gemini API error"
**Solution**: Check API key in `gemini_service.py` or set environment variable

---

## 🎯 What Do You Need Help With?

1. **Deployment** → See `DEPLOYMENT_GUIDE.md`
2. **Features** → Check `FEATURES_IMPLEMENTED.md`
3. **Setup** → See `SETUP.md`
4. **Database** → Run `python init_database.py`
5. **Errors** → Check terminal output and browser console

---

## 📚 Documentation Files

- `QUICK_START.md` - Quick reference
- `DEPLOYMENT_GUIDE.md` - Full deployment instructions
- `FEATURES_IMPLEMENTED.md` - All features list
- `SETUP.md` - Setup instructions
- `PROJECT_SUMMARY.md` - Project overview

---

**Tell me what specific help you need, and I'll guide you step by step!** 🚀
