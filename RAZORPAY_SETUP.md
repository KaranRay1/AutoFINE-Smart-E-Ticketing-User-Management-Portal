# Razorpay Payment Gateway – Setup Guide

AutoFINE uses **Razorpay** for online challan payments. Follow these steps to get your API keys and enable real payments.

---

## Step 1: Create a Razorpay Account

1. Go to **https://razorpay.com**
2. Click **Sign Up** (top right).
3. Enter your **Email** and **Password** and complete registration.
4. Verify your email if prompted.

---

## Step 2: Complete Business / KYC (for Live Mode)

- For **test mode**: You can use **Test Mode** keys without KYC.
- For **live payments**: Complete **Business Verification** and **Bank Account** details in the Razorpay Dashboard under **Settings → Configuration**.

---

## Step 3: Get Your API Keys

1. Log in to **Razorpay Dashboard**: https://dashboard.razorpay.com  
2. Switch to **Test Mode** (toggle at top) for development, or **Live Mode** for real money.
3. Go to **Settings** (gear icon) → **API Keys**.
4. Click **Generate Key** if you don’t have keys yet.
5. You will see:
   - **Key ID** (e.g. `rzp_test_xxxxxxxxxxxx`) – **public**, used in frontend.
   - **Key Secret** – shown **once**; copy and store it securely. It’s used only on the server.

---

## Step 4: Add Keys to Your Project

### Option A: Environment variables (recommended)

Create or edit a `.env` file in the **AutoFINE** folder:

```env
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_key_secret_here
```

Replace with your actual **Key ID** and **Key Secret**.

### Option B: System environment (Windows)

```cmd
set RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx
set RAZORPAY_KEY_SECRET=your_key_secret_here
```

### Option C: Deployment (Render / Heroku / Railway)

In your hosting dashboard, add **Environment Variables**:

- `RAZORPAY_KEY_ID` = your Key ID  
- `RAZORPAY_KEY_SECRET` = your Key Secret  

---

## Step 5: Restart the Application

After setting the variables:

- **Local:** Stop the app (Ctrl+C) and run `python app.py` again.
- **Deployed:** Redeploy or restart the service so it picks up the new env vars.

---

## Step 6: Test Payment Flow

1. Log in as a **vehicle owner** (or register and add a vehicle with challans).
2. Open **My Dashboard** (owner dashboard).
3. Find an **Unpaid** challan and click **Pay**.
4. **If Razorpay is configured:** Razorpay checkout will open; use [test cards](https://razorpay.com/docs/payments/payments/test-card-details/) (e.g. `4111 1111 1111 1111`).
5. **If keys are not set:** The app will fall back to **mock payment** and show a message to configure Razorpay.

---

## Test Card Details (Test Mode Only)

| Card Number       | Result   |
|-------------------|----------|
| 4111 1111 1111 1111 | Success |
| 4000 0000 0000 0002 | Failure |

- Use any future **Expiry** and any **CVV** (e.g. 12/30, 123).
- More options: https://razorpay.com/docs/payments/payments/test-card-details/

---

## Summary Checklist

- [ ] Razorpay account created  
- [ ] Key ID and Key Secret copied from Dashboard → Settings → API Keys  
- [ ] `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` set in `.env` or hosting env  
- [ ] App restarted / redeployed  
- [ ] Pay button on owner dashboard opens Razorpay (or mock payment if keys missing)  

---

## Security Notes

- **Never** commit `.env` or put **Key Secret** in frontend or in Git.
- Use **Test Mode** and test keys during development.
- Switch to **Live Mode** and live keys only when you are ready to accept real payments.

---

## Need Help?

- Razorpay docs: https://razorpay.com/docs/  
- API Keys: https://razorpay.com/docs/api/keys/
