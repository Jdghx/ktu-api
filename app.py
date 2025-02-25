from flask import Flask, jsonify
import requests
import urllib3
from bs4 import BeautifulSoup  

# Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# API URL
API_URL = "https://api.ktu.edu.in/ktu-web-portal-api/anon/announcemnts"

# Request payload
REQUEST_DATA = {
    "number": 0,
    "searchText": "",
    "size": 50  # Fetch last 50 notifications
}

# Headers
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.ktu.edu.in/"
}

@app.route('/')
def home():
    return jsonify({"status": "success", "message": "KTU Announcements API is running!"})

@app.route('/favicon.ico')
def favicon():
    return "", 204  # Avoid 404 for favicon requests

@app.route('/ktu-announcements', methods=['GET'])
def get_ktu_announcements():
    try:
        response = requests.post(API_URL, json=REQUEST_DATA, headers=HEADERS, verify=False)

        if response.status_code == 200:
            data = response.json()

            if "content" in data and isinstance(data["content"], list):
                notifications = []

                for item in data["content"]:
                    raw_description = item.get("message", "")  
                    clean_description = BeautifulSoup(raw_description, "html.parser").get_text() if raw_description else "No description available."

                    # Check if PDF attachments exist
                    has_pdf = any(
                        attachment.get("attachmentName", "").endswith(".pdf")
                        for attachment in item.get("attachmentList", [])
                    )

                    notification = {
                        "date": item.get("announcementDate", "Unknown Date"),
                        "title": item.get("subject", "No Title"),
                        "description": clean_description.strip(),
                        "pdf_link": "https://ktu.edu.in/menu/announcements" if has_pdf else None
                    }
                    notifications.append(notification)

                return jsonify({
                    "status": "success",
                    "total": len(notifications),
                    "notifications": notifications
                }), 200

            return jsonify({"status": "error", "message": "No content found"}), 404

        return jsonify({"status": "error", "message": "Failed to fetch data", "code": response.status_code}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

