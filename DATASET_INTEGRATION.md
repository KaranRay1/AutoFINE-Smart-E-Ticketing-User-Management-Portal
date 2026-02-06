# Dataset Integration Guide

## 📊 Available Datasets

### 1. **Punjab E-Challan Dataset** (Primary)
- **Location**: `archive/Punjab_E_Challan_Dataset_500_Rows.csv`
- **Format**: Individual challan records
- **Columns**:
  - `challan_id`: Unique challan identifier
  - `vehicle_type`: Bike, Car, Truck, Bus
  - `violation_type`: Speeding, No Helmet, Wrong Parking, etc.
  - `location`: Street/location name
  - `city`: City name
  - `violation_time`: Morning, Afternoon, Evening, Night
  - `speed_recorded_kmph`: Speed (for speeding violations)
  - `fine_amount_PKR`: Fine amount in PKR
  - `payment_status`: Paid/Unpaid
  - `issuing_method`: Camera/Traffic Warden
  - `repeat_offender`: Yes/No
- **Records**: 500 challan records
- **Usage**: Creates vehicles and challans in database

### 2. **State/District Statistics**
- **Location**: `dataset/RS_Session_259_AU_1689_A.csv`
- **Format**: State-wise challan statistics
- **Columns**:
  - `Year`: Year of data
  - `State`: State name
  - `District`: District name
  - `Total Challans`: Total number of challans
  - `Total Challan Amount`: Total fine amount
  - `Total Revenue Collected`: Revenue collected
- **Usage**: Statistics and analytics

### 3. **Offence Statistics**
- **Location**: `dataset/RS_Session_267_AU_2175_A_and_C.csv`
- **Format**: Offence-wise statistics
- **Columns**:
  - `Sl. No.`: Serial number
  - `State/UT`: State/Union Territory
  - `Offence`: Offence description
  - `Total Number of Challan`: Total challans for this offence
  - `Revenue Collected (In Rupees)`: Revenue collected
- **Usage**: Creates violation types and fine amounts

### 4. **Yearly Statistics**
- **Location**: `dataset/RS_Session_256_AU_93_D.csv`
- **Format**: Year-wise challan count
- **Columns**:
  - `Sl. No.`: Serial number
  - `Year`: Year
  - `Number of Challan`: Total challans
- **Usage**: Yearly trend analysis

### 5. **State Revenue Statistics**
- **Location**: `dataset/RS_Session_266_AU_1849_E_i.csv`
- **Format**: State-wise revenue statistics
- **Columns**:
  - `Sl. No.`: Serial number
  - `State/UT`: State/Union Territory
  - `Number of Challan Issued`: Total challans
  - `Revenue Collection (in Rupees)`: Total revenue
- **Usage**: Revenue analytics

## 🔧 How to Import Datasets

### Method 1: Via Admin Dashboard (Recommended)
1. Login as admin (username: `admin`, password: `admin123`)
2. Go to Admin Dashboard
3. Scroll to "Dataset Import" section
4. Click "Import All Datasets" button
5. Wait for import to complete (may take a few minutes)

### Method 2: Via API
```bash
POST /api/datasets/import
```

### Method 3: During Database Initialization
Run `init_database.py` - it automatically imports all datasets:
```bash
python init_database.py
```

## 📋 Import Process

1. **Punjab Dataset Import**:
   - Creates vehicles with Indian license plate format (UK-XX-AA-0000)
   - Creates challans with all details
   - Maps payment status
   - Handles repeat offenders

2. **Statistics Processing**:
   - Processes state/district statistics
   - Extracts violation types from offence descriptions
   - Updates violation fine amounts
   - Logs statistics for analytics

3. **Data Transformation**:
   - Converts PKR to INR (1:1 for demo)
   - Generates Indian-style license plates
   - Maps cities to RTO codes
   - Creates realistic dates and timestamps

## 🎯 Features

- **Automatic License Plate Generation**: Creates Indian format plates (UK-XX-AA-0000)
- **RTO Code Mapping**: Maps cities to appropriate RTO codes
- **Violation Type Extraction**: Intelligently extracts violation types from descriptions
- **Owner Assignment**: Randomly assigns vehicles to existing owners
- **Payment Status Mapping**: Correctly maps payment status
- **Repeat Offender Tracking**: Marks subsequent violations
- **Error Handling**: Continues import even if some rows fail

## 📊 Expected Results

After importing all datasets:
- **500+ vehicles** created
- **500+ challans** created
- **Multiple violation types** added
- **Statistics** processed and logged
- **Analytics data** available

## 🔍 Verification

Check import results:
1. Go to Admin Dashboard → Vehicles (should show 500+ vehicles)
2. Go to Admin Dashboard → Challans (should show 500+ challans)
3. Check statistics in Analytics Dashboard

## ⚠️ Notes

- Import may take 2-5 minutes depending on dataset size
- Existing data is not deleted (additive import)
- Duplicate vehicles are handled (reuses existing vehicle)
- License plates are generated to match Indian format
- All dates are randomized within realistic ranges

## 🚀 Next Steps

After importing:
1. View statistics in Analytics Dashboard
2. Test search functionality with imported data
3. Generate reports using imported data
4. Use data for testing Bhopal ITMS features
5. Analyze trends using imported statistics
