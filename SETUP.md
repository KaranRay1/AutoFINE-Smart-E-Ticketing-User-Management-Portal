# AutoFINE Setup Guide

## Quick Start Guide

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users**: If `mysqlclient` installation fails, the project is configured to use `pymysql` instead. No changes needed.

### Step 2: Database Setup

#### Option A: Using MySQL

1. Install MySQL Server (if not already installed)
2. Create database:
```sql
CREATE DATABASE autofine_db;
```

3. Update database credentials in `app.py` (line 19):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost/autofine_db'
```

#### Option B: Using SQLite (Quick Testing)

For quick testing without MySQL, you can modify `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autofine.db'
```

### Step 3: Initialize Database

```bash
python init_database.py
```

This will:
- Create all tables
- Create admin user (username: `admin`, password: `admin123`)
- Load sample data from CSV if available
- Create sample vehicle owners

### Step 4: Run Application

```bash
python app.py
```

Open browser: `http://localhost:5000`

## Default Login Credentials

- **Admin**: username=`admin`, password=`admin123`
- **Owner**: username=`john_doe`, password=`password123`

## Troubleshooting

### Issue: EasyOCR installation takes long time
**Solution**: EasyOCR downloads models on first run. This is normal and happens only once.

### Issue: Port 5000 already in use
**Solution**: Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Issue: Database connection error
**Solution**: 
- Verify MySQL is running
- Check database credentials in `app.py`
- Ensure database `autofine_db` exists

### Issue: Module not found errors
**Solution**: Ensure you're in the `autofine_app` directory and virtual environment is activated.

## Testing the ALPR Module

1. Prepare test images with visible license plates
2. Use the admin dashboard to upload images
3. Select violation type and location
4. Click "Process Violation"
5. System will detect license plate and create challan

## Project Structure

```
autofine_app/
├── app.py              # Main Flask application
├── models.py           # Database models
├── init_database.py    # Database initialization
├── requirements.txt    # Python dependencies
├── alpr_module/       # License Plate Recognition
├── templates/         # HTML templates
└── uploads/          # Uploaded images
```
