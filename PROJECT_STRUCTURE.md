# AutoFINE Project Structure

## Root
- app.py — Flask application, routes, analytics, chatbot, payments, SSE
- models.py — SQLAlchemy models (Vehicle, Challan, User, Report, etc.)
- gemini_service.py — Gemini API integration (news, rules, insights, guidance)
- email_service.py — SMTP mail helper for notifications and reports
- sms_service.py — SMS notifications helper
- traffic_rules.py — Rule texts and helpers
- advanced_detection_services.py — Predictive policing services, detection stubs
- dataset_importer.py — CSV import utilities
- init_database.py — Database initialization/seeding
- requirements.txt — Python dependencies
- runtime.txt — Runtime/version hints
- start_server.bat/ps1 — Local server shortcuts
- deploy_heroku.bat/ps1, Procfile — Heroku deployment scripts
- bhopal_itms_integration.py — External ITMS integration placeholder

## Folders
- instance/ — SQLite database (autofine.db)
- static/
  - css/ — Themes and styles (vehicle-challan-theme.css, professional-theme.css, theme.css, transaction-theme.css)
  - js/ — Frontend logic (advanced-features.js: chatbot, map, analytics; realtime.js: SSE; gemini-news.js: homepage news)
- templates/
  - base.html — Shared layout, navbar, assets
  - index.html — Homepage, CTA buttons, Gemini news
  - admin/ — Admin pages (dashboard, vehicles, challans, new challan, detail)
  - owner/ — Owner pages (dashboard, vehicle_detail, pay_challan)
  - public/ — Public pages (lookup, notices, report)
  - login.html, register.html — Auth pages
- alpr_module/ — ALPR logic (license plate recognition)
- data/ — Sample datasets (challan_generation.csv, traffic.csv, police.csv)
- dataset/ — Additional bundled CSVs and PDF report
- uploads/ — User-imported datasets and media

## Documentation
- README.md — Overview and getting started
- QUICK_START.md, SETUP.md — Setup/run instructions
- RUN.md — Run scripts guidance
- DEPLOY*.md, HEROKU_DEPLOYMENT.md — Deployment guides
- ACCESS_INFO.md — Access details and roles
- FEATURES_IMPLEMENTED.md — Feature list
- PROJECT_REPORT.md, PROJECT_SUMMARY.md, PROJECT_DOCUMENTATION.md — Detailed project docs
- DATASET_INTEGRATION.md, DATASETS_MODELS_TOOLS.md — Dataset usage
- THEME_UPDATE.md — Theme update notes

