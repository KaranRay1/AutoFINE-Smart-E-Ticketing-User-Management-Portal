# AutoFINE - Quick Start Guide

## ✅ Server Status

**Your AutoFINE server is currently RUNNING!**

- **Local Access**: http://localhost:5000
- **Network Access**: http://YOUR_IP:5000 (accessible from other devices on your network)

---

## 🔑 Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full admin dashboard, vehicle management, challan management

### Owner Account (Sample)
- **Username**: `john_doe`
- **Password**: `password123`
- **Access**: Owner dashboard, view vehicles, view/pay challans

---

## 🚀 How to Run the Application

### Method 1: Using Python Directly
```bash
cd AutoFINE
python app.py
```

### Method 2: Using Batch File (Windows)
Double-click `start_server.bat`

### Method 3: Using PowerShell Script
```powershell
.\start_server.ps1
```

---

## 🌐 Access from Other Devices

1. **Find Your IP Address**:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Example: `192.168.1.100`

2. **Access from Other Devices**:
   - Open browser on phone/tablet/other computer
   - Go to: `http://YOUR_IP:5000`
   - Example: `http://192.168.1.100:5000`

3. **Firewall Settings**:
   - Windows Firewall may block port 5000
   - Allow Python through firewall when prompted
   - Or manually allow port 5000 in Windows Firewall settings

---

## 📦 Deployment Options

### Quick Deploy (5 minutes)
1. **Heroku** (Free tier available)
   - See `DEPLOYMENT_GUIDE.md` for detailed steps
   - Best for: Quick demo, testing, small projects

2. **Railway** (Free tier available)
   - Connect GitHub repo
   - Auto-deploy on push
   - Best for: Continuous deployment

### Production Deploy (30 minutes)
1. **AWS EC2** or **DigitalOcean**
   - Full control
   - Best for: Production applications
   - See `DEPLOYMENT_GUIDE.md` for detailed steps

2. **AWS Elastic Beanstalk**
   - Managed service
   - Auto-scaling
   - Best for: Enterprise applications

---

## 🔧 Common Commands

### Reset Database (Development)
```bash
cd AutoFINE
rm autofine.db  # or del autofine.db on Windows
python init_database.py
```

### Install/Update Dependencies
```bash
pip install -r requirements.txt
```

### Check Server Status
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing

# Or just open browser to http://localhost:5000
```

---

## 📱 Features Available

✅ **Admin Dashboard**
- View all vehicles and challans
- Process violations
- Generate challans
- Analytics and insights

✅ **Owner Dashboard**
- View your vehicles
- Check challans
- Pay fines online
- View transaction history

✅ **Public Features**
- Challan lookup by UIN/Vehicle No/DL No
- View traffic notices
- Report incidents

✅ **Real-time Updates**
- Live challan updates
- Real-time dashboard
- Server-Sent Events (SSE)

✅ **AI Features**
- Gemini-powered news
- Traffic rules explanations
- Appeal guidance
- Predictive insights

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process or change port in app.py
# Change: app.run(debug=True, host='0.0.0.0', port=5000)
# To: app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Errors
```bash
# Reset database
rm autofine.db
python init_database.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Can't Access from Other Devices
1. Check firewall settings
2. Verify IP address is correct
3. Ensure both devices are on same network
4. Try accessing from same device first (localhost)

---

## 📚 Documentation

- **Full Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **Features**: See `FEATURES_IMPLEMENTED.md`
- **Setup Instructions**: See `SETUP.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`

---

## 🎯 Next Steps

1. ✅ **Server is Running** - Access at http://localhost:5000
2. 🔐 **Change Default Passwords** - For production use
3. 🔒 **Set Environment Variables** - SECRET_KEY, GEMINI_API_KEY
4. 🗄️ **Use Production Database** - PostgreSQL/MySQL for production
5. 🌐 **Deploy to Cloud** - Follow `DEPLOYMENT_GUIDE.md`

---

**Happy Coding! 🚀**
