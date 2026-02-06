"""
Gemini API Service for Real-time Traffic Updates and News Generation
"""

import google.generativeai as genai
import os
from datetime import datetime
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Gemini configure error: {e}")

def get_gemini_model():
    """Get Gemini model instance"""
    try:
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return None

def generate_traffic_news():
    """Generate daily traffic news and updates using Gemini"""
    model = get_gemini_model()
    if not model:
        return {
            "title": "Traffic Update",
            "content": "System updates available. Check your challans regularly.",
            "type": "info",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        prompt = f"""Generate a brief traffic news update for India (max 100 words) covering:
- Current traffic rules updates
- Important notices from state/central government
- Safety reminders
- Any recent changes in challan fines

Format as JSON with: title, content, type (info/warning/alert), timestamp
Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Try to parse JSON from response
        if '{' in text:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            json_str = text[json_start:json_end]
            news_data = json.loads(json_str)
            news_data['timestamp'] = datetime.now().isoformat()
            return news_data
        else:
            return {
                "title": "Traffic Update",
                "content": text[:200],
                "type": "info",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error generating news: {e}")
        return {
            "title": "Traffic Update",
            "content": "Stay updated with latest traffic rules. Drive safely.",
            "type": "info",
            "timestamp": datetime.now().isoformat()
        }

def generate_notice_summary(notice_text):
    """Generate a summary of a traffic notice using Gemini"""
    model = get_gemini_model()
    if not model:
        return notice_text[:100] + "..."
    
    try:
        prompt = f"""Summarize this traffic notice in 2-3 sentences:
{notice_text}

Provide only the summary, no additional text."""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error summarizing notice: {e}")
        return notice_text[:100] + "..."

def get_traffic_rules_explanation(violation_type):
    """Get explanation of traffic rules for a violation type"""
    model = get_gemini_model()
    if not model:
        return f"Violation: {violation_type}. Please follow traffic rules."
    
    try:
        prompt = f"""Explain the traffic rule violation for: {violation_type}
Include:
- What the violation means
- Fine amount (as per Indian Motor Vehicles Act)
- Safety implications
- How to avoid it

Keep it brief (3-4 sentences)."""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error explaining rule: {e}")
        return f"Violation: {violation_type}. Follow traffic rules for safety."

def generate_appeal_guidance(challan_details):
    """Generate guidance for appealing a challan"""
    model = get_gemini_model()
    if not model:
        return "You can appeal this challan through the virtual court system."
    
    try:
        prompt = f"""Provide guidance for appealing a traffic challan with these details:
Violation: {challan_details.get('violation_type', 'Unknown')}
Amount: ₹{challan_details.get('fine_amount', 0)}
Location: {challan_details.get('location', 'Unknown')}

Explain:
- Steps to file an appeal
- Required documents
- Timeline for appeal
- Grounds for appeal

Keep it concise and actionable."""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating appeal guidance: {e}")
        return "You can appeal this challan through the virtual court system."

def get_predictive_insights(location=None):
    """Get predictive insights about traffic violations"""
    model = get_gemini_model()
    if not model:
        return {
            "hotspot": "High traffic areas",
            "peak_time": "Morning rush hour",
            "common_violation": "Signal jumping"
        }
    
    try:
        prompt = f"""Based on traffic violation patterns in India, provide insights:
- Common violation hotspots
- Peak violation times
- Most frequent violation types
- Safety recommendations

Location context: {location or 'All India'}
Format as JSON with: hotspot, peak_time, common_violation, recommendation"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if '{' in text:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            json_str = text[json_start:json_end]
            return json.loads(json_str)
        else:
            return {
                "hotspot": "Urban intersections",
                "peak_time": "8-10 AM, 5-7 PM",
                "common_violation": "Signal jumping",
                "recommendation": "Follow traffic signals and speed limits"
            }
    except Exception as e:
        print(f"Error getting insights: {e}")
        return {
            "hotspot": "High traffic areas",
            "peak_time": "Rush hours",
            "common_violation": "Traffic violations",
            "recommendation": "Drive safely and follow rules"
        }
