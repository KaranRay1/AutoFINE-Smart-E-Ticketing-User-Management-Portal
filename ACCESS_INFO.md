# AutoFINE Server Access Information

## 🚀 Server is Running!

### Local Access (Same Computer):
```
http://localhost:5000
```

### Network Access (Other Devices on Same Network):
```
http://192.168.29.75:5000
```

**Note:** Replace `192.168.29.75` with your actual local IP address if different.

## 🔐 Login Credentials

### Admin Account:
- **Username:** `admin`
- **Password:** `admin123`

### Vehicle Owner Accounts:
- **Username:** `john_doe`, `jane_smith`, or `rahul_kumar`
- **Password:** `password123`

## 📱 Access from Mobile/Other Devices

1. Make sure your device is connected to the same Wi-Fi network
2. Open a web browser on your device
3. Navigate to: `http://192.168.29.75:5000`

## 🛠️ To Start the Server Again

### Option 1: Using Batch File (Windows)
Double-click `start_server.bat`

### Option 2: Using PowerShell Script
Right-click `start_server.ps1` → Run with PowerShell

### Option 3: Using Command Line
```bash
cd "D:\Projects\E- Challan\AutoFINE"
python app.py
```

## ⚠️ Important Notes

1. **Firewall:** Windows Firewall may block incoming connections. If devices can't access:
   - Go to Windows Defender Firewall
   - Allow Python through firewall for Private networks

2. **Port:** The server runs on port 5000. If this port is in use:
   - Change port in `app.py` (line 330): `app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)`

3. **Network:** Only devices on the same local network can access. For internet access, you would need:
   - Port forwarding on your router, OR
   - Cloud hosting (AWS, Azure, Heroku, etc.)

## 🛑 To Stop the Server

Press `Ctrl+C` in the terminal window where the server is running.
