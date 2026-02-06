# How to Run AutoFINE

## Prerequisites

- **Python 3.10+** installed on your system
- **.env file** in the `AutoFINE` folder with your API keys (you have already set this up)

---

## Step 1: Open Terminal in Project Folder

- **Windows (CMD):** `cd "D:\Projects\E- Challan\AutoFINE"`
- **Windows (PowerShell):** `cd "D:\Projects\E- Challan\AutoFINE"`
- **Mac/Linux:** `cd /path/to/AutoFINE`

---

## Step 2: Create Virtual Environment (Recommended, First Time Only)

```bash
python -m venv venv
```

**Activate it:**

- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Mac/Linux:** `source venv/bin/activate`

---

## Step 3: Install Dependencies (First Time or After Pull)

```bash
pip install -r requirements.txt
```

---

## Step 4: Initialize Database (First Time Only)

If you have not run this before, or if you want a fresh database:

```bash
python init_database.py
```

This creates the SQLite database and seed data (admin user, sample vehicles/challans).

---

## Step 5: Run the Application

```bash
python app.py
```

You should see something like:

```
* Running on http://127.0.0.1:5000
* Running on http://localhost:5000
```

---

## Step 6: Open in Browser

Open your browser and go to:

**http://localhost:5000**

---

## Default Login

| Role   | Username | Password   |
|--------|----------|------------|
| Admin  | admin    | admin123   |

You can also **Register** a new account and log in as **Vehicle Owner**.

---

## .env File (Already Done by You)

Your `.env` in the `AutoFINE` folder should contain at least:

- `SECRET_KEY` – Flask secret
- `RAZORPAY_KEY_ID` – Razorpay test/live Key ID
- `RAZORPAY_KEY_SECRET` – Razorpay test/live Secret
- `GEMINI_API_KEY` – (optional) for AI news/insights
- `DATABASE_URL` – (optional) e.g. `sqlite:///autofine.db`

The app loads `.env` automatically when you run `python app.py`.

---

## To Stop the Server

Press **Ctrl + C** in the terminal where the app is running.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 already in use | Stop other app using 5000, or set `FLASK_RUN_PORT=5001` and use http://localhost:5001 |
| Module not found | Run `pip install -r requirements.txt` |
| Database error | Run `python init_database.py` again (backup/delete `autofine.db` if you want a clean start) |
| Razorpay not opening | Check `.env` has `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` and restart the app |
