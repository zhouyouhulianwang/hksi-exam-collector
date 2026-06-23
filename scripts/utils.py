"""
HKSI LE Exam Data Collector - Utilities
Common functions for API authentication and data handling
"""

import requests
import json

BASE_URL = "https://mgr.51exampass.com/index.php/api"
APP_BASE = "https://app.51exampass.com/api/"


def login(username: str, password: str) -> str:
    """Login and return auth token"""
    resp = requests.post(
        f"{BASE_URL}/v1.login/login_e_p",
        json={"mobile_email": username, "password": password},
        timeout=15
    )
    data = resp.json()
    if data.get("code") == 1 and data.get("data"):
        return data["data"]["token"]
    raise Exception(f"Login failed: {data.get('msg', 'Unknown error')}")


def get_mgr_headers(token: str) -> dict:
    return {"user-token": token, "Content-Type": "application/x-www-form-urlencoded"}


def get_app_headers(token: str) -> dict:
    return {"user-token": token, "server": "1", "Content-Type": "application/x-www-form-urlencoded"}


def mgr_api_call(endpoint: str, params: dict = None, token: str = None) -> dict:
    headers = get_mgr_headers(token) if token else {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{BASE_URL}/{endpoint}", headers=headers, data=params or {}, timeout=15)
    return resp.json()


def app_api_call(endpoint: str, params: dict = None, token: str = None) -> dict:
    headers = get_app_headers(token) if token else {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{APP_BASE}{endpoint}", headers=headers, data=params or {}, timeout=15)
    return resp.json()


PAPERS = {
    "卷一": {
        "subject_id": 7,
        "item_id": 1252,
        "chapters": [
            {"id": 24, "name": "第1章"}, {"id": 25, "name": "第2章"},
            {"id": 26, "name": "第3章"}, {"id": 27, "name": "第4章"},
            {"id": 28, "name": "第5章"}, {"id": 29, "name": "第6章"},
            {"id": 30, "name": "第7章"}, {"id": 31, "name": "第8章"},
            {"id": 32, "name": "第9章"},
        ]
    },
    "卷二": {
        "subject_id": 4,
        "item_id": 2417,
        "chapters": [
            {"id": 13, "name": "第1章"}, {"id": 16, "name": "第2章"},
            {"id": 39, "name": "第3章"}, {"id": 40, "name": "第4章"},
            {"id": 41, "name": "第5章"}, {"id": 42, "name": "第6章"},
            {"id": 43, "name": "第7章"},
        ]
    },
    "卷六": {
        "subject_id": 3,
        "item_id": 2418,
        "chapters": [
            {"id": 6, "name": "第1章"}, {"id": 10, "name": "第2章"},
            {"id": 46, "name": "第3章"}, {"id": 47, "name": "第4章"},
        ]
    },
}
