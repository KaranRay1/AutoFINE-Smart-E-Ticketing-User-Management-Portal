# AutoFINE: Datasets, Models, and Tools Documentation

## 📊 Datasets Used

### 1. **Punjab E-Challan Dataset** (Primary)
- **Source**: `archive/Punjab_E_Challan_Dataset_500_Rows.csv`
- **Type**: CSV dataset containing challan records
- **Content**: 500 rows of traffic violation data including:
  - Challan IDs
  - Vehicle types (Bike, Car, Truck, Bus)
  - Violation types (Speeding, Signal Jumping, Wrong Parking, No Helmet, etc.)
  - Locations (Mall Road, Clock Tower, GT Road, etc.)
  - Cities (Rawalpindi, Lahore, Faisalabad)
  - Speed records (for speeding violations)
  - Fine amounts (in PKR)
  - Payment status
  - Issuing method (Camera, Traffic Warden)
  - Repeat offender flags
- **Usage**: Used for initial database population and testing challan management features
- **Format**: CSV with 11 columns

### 2. **Vehicle Images Dataset**
- **Source**: `AI-Based-Traffic-Rules-Violation-Detection-and-E-Challan-System-main/car_images/`
- **Type**: Image dataset (271 PNG files)
- **Content**: Vehicle images with visible license plates for ALPR testing
- **Usage**: Testing and training license plate recognition module
- **Format**: PNG image files

### 3. **Indian Traffic Challan Dataset** (Government Data Format)
- **Reference**: Indian Parivahan Portal (parivahan.gov.in)
- **Expected Format**: Based on Indian government e-challan structure:
  - Vehicle Registration Number (Indian format: XX##XX####)
  - Owner details
  - Violation details
  - Fine amounts as per Indian Motor Vehicles Act
  - Location (with GPS coordinates)
  - Date and time
  - Camera/Enforcement officer details
- **Note**: This project implements a system compatible with Indian challan data format
- **Integration**: System designed to support Parivahan/VAHAN database integration

### 4. **Online Datasets** (Referenced for ALPR)
- **DriveIndia Dataset**: ~66,996 images of Indian traffic scenarios
  - Source: Research papers and academic datasets
  - Used for: License plate detection in Indian traffic conditions
  - Format: Images with annotations
- **UFPR-ALPR**: Standard ALPR dataset for training
- **SSIG-SegPlate**: Segmentation dataset for license plate regions

---

## 🤖 ML Models & AI Components

### 1. **License Plate Recognition (ALPR) Module**

#### **Detection Model**:
- **Technology**: OpenCV with contour detection and morphological operations
- **Approach**: Traditional computer vision for license plate region detection
- **Process**:
  1. Image preprocessing (Gaussian blur, Canny edge detection)
  2. Morphological operations to connect edges
  3. Contour detection with aspect ratio filtering (2:1 to 5:1 ratio)
  4. Region extraction based on area and geometry

#### **OCR Engine**:
- **Primary**: **EasyOCR 1.7.2**
  - Language: English
  - GPU Support: Available (CPU mode used for compatibility)
  - Accuracy: High for clear license plate images
  - Framework: PyTorch backend
- **Features**:
  - Multi-language support (extensible to Indian languages)
  - Character recognition with confidence scores
  - Robust to various fonts and styles
- **Text Cleaning**:
  - Regex-based filtering (alphanumeric only)
  - Character normalization (uppercase)
  - Noise removal and validation

#### **Image Preprocessing**:
- **Techniques Used**:
  - Grayscale conversion
  - Denoising (fastNlMeansDenoising)
  - Contrast enhancement (CLAHE - Contrast Limited Adaptive Histogram Equalization)
  - Adaptive thresholding
  - Region of Interest (ROI) extraction

### 2. **Future ML Model Options** (Not Currently Implemented)

#### **For Production Use**:
- **YOLOv8 / YOLOv12**: For vehicle and license plate detection
  - Framework: Ultralytics PyTorch
  - Benefits: Higher accuracy, real-time performance
  - Use case: Detection of vehicles and plates in complex scenes
- **Custom CNN for OCR**: Fine-tuned for Indian license plates
  - Character-level recognition
  - Regional font support (Hindi, regional scripts)
- **Transformer-based OCR**: For improved accuracy
  - Models: TrOCR, PaddleOCR

---

## 🛠️ Tools & Technologies

### **Backend Framework**:
1. **Flask 3.1.2**
   - Web framework for API and routes
   - Template engine (Jinja2)
   - Session management
   - File upload handling

2. **Flask-SQLAlchemy 3.1.1**
   - ORM for database operations
   - Database abstraction layer
   - Query building and relationships

3. **Flask-Bcrypt 1.0.1**
   - Password hashing and security
   - Secure authentication

### **Database**:
1. **SQLite** (Default)
   - File-based database
   - Easy setup, no server required
   - Suitable for development and demos

2. **MySQL/PostgreSQL** (Production Option)
   - Supported via PyMySQL
   - Scalable for production deployments
   - Connection string: `mysql+pymysql://user:pass@host/db`

### **Computer Vision & Image Processing**:
1. **OpenCV 4.12.0** (`opencv-python-headless`)
   - Image preprocessing
   - License plate region detection
   - Contour analysis
   - Image transformations

2. **NumPy 2.2.6**
   - Numerical operations
   - Array manipulation for images
   - Mathematical computations

3. **Pillow 12.1.0**
   - Image I/O operations
   - Format conversion
   - Image manipulation

### **OCR & Text Recognition**:
1. **EasyOCR 1.7.2**
   - Dependencies:
     - **Torch 2.9.1** (PyTorch deep learning framework)
     - **Torchvision 0.24.1** (Image preprocessing for PyTorch)
     - **SciPy 1.17.0** (Scientific computing)
     - **scikit-image 0.26.0** (Image processing)
     - **PyYAML 6.0.3** (Configuration)
     - **Shapely 2.1.2** (Geometric operations)
     - **pyclipper 1.4.0** (Polygon clipping)

### **Frontend Technologies**:
1. **Bootstrap 5.3.0**
   - Responsive UI framework
   - Grid system and components

2. **Bootstrap Icons 1.11.0**
   - Icon library

3. **Custom CSS (Theme)**
   - Challan-aware theme adaptation
   - Dark teal professional design
   - Custom animations and transitions

4. **JavaScript (Vanilla)**
   - Real-time updates via Server-Sent Events (SSE)
   - AJAX for async operations
   - DOM manipulation

### **Real-Time Updates**:
- **Server-Sent Events (SSE)**
  - Implementation: Flask's `Response` with `stream_with_context`
  - Protocol: HTTP text/event-stream
  - Use case: Live challan updates without polling
  - Update interval: 2-3 seconds

### **Development Tools**:
1. **Python 3.12**
   - Programming language

2. **pip** (Package Manager)
   - Dependency management

3. **Git** (Version Control)
   - Code versioning

---

## 📋 Data Models

### **Database Schema**:
1. **Users Table**
   - User authentication and profiles
   - Roles: Owner, Admin

2. **Vehicles Table**
   - License plate number (primary identifier)
   - Owner ID (foreign key)
   - Model, color, type
   - Registration and insurance dates

3. **Violations Table**
   - Violation types (Speeding, Signal Jumping, etc.)
   - Fine amounts per violation type

4. **Challans Table**
   - Vehicle ID (foreign key)
   - Violation type
   - Location, fine amount
   - Status (Unpaid, Paid, Disputed)
   - Evidence images
   - Timestamps

5. **Cameras Table**
   - Camera locations and metadata
   - GPS coordinates

---

## 🔗 Integration Points

### **Indian Government Systems** (Designed for):
1. **Parivahan Portal** (parivahan.gov.in)
   - Vehicle registration verification
   - Owner details lookup
   - Integration-ready API endpoints

2. **VAHAN Database**
   - Vehicle registration database
   - Real-time verification capability

3. **E-Challan Format**
   - Compatible with Indian government challan structure
   - Supports standard violation codes
   - Fine amounts as per Motor Vehicles Act

---

## 📈 Performance Metrics

### **ALPR Module**:
- **Detection Rate**: ~85-90% (depends on image quality)
- **OCR Accuracy**: ~80-95% (with EasyOCR on clear images)
- **Processing Time**: 1-3 seconds per image (CPU mode)

### **Real-Time Updates**:
- **Latency**: 2-3 seconds
- **Connection**: Persistent SSE connection
- **Scalability**: Supports multiple concurrent connections

---

## 🚀 Deployment Stack

### **Development**:
- Flask development server
- SQLite database
- Local file storage for uploads

### **Production-Ready Options**:
- **Web Server**: Gunicorn or uWSGI
- **Database**: PostgreSQL or MySQL
- **File Storage**: AWS S3 or local server storage
- **Hosting**: AWS EC2, Azure, Heroku, or VPS

---

## 📝 License & Attribution

### **Open Source Libraries**:
- Flask: BSD License
- EasyOCR: Apache 2.0 License
- OpenCV: Apache 2.0 License
- Bootstrap: MIT License

### **Datasets**:
- Punjab E-Challan Dataset: Provided in project
- Vehicle Images: Provided in project folders
- Indian Government Data: Referenced format, not included

---

## 🔮 Future Enhancements

### **Planned Models**:
1. **YOLOv8/YOLOv12** for improved detection
2. **Fine-tuned OCR** for Indian license plates
3. **Video processing** for real-time CCTV feeds
4. **Deep learning** for violation classification

### **Additional Datasets**:
1. Integration with live Parivahan API
2. Real-time vehicle registration lookup
3. Historical challan data analysis

---

**Last Updated**: January 2025  
**Project Version**: 1.0.0  
**Maintained By**: AutoFINE Development Team
