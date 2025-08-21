"""
API Test Example for easeCHAOS Backend

This script demonstrates how to interact with the easeCHAOS API endpoints.
"""



import requests

import json

# Base URL for the API
BASE_URL = "http://localhost:3000/api/v1"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/healthcheck")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def get_lecture_timetable():
    """Get lecture timetable for a specific class"""
    print("Getting lecture timetable...")
    payload = {
        "filename": "Draft_1.xlsx",
        "class_pattern": "EL 3",
        "is_exam": False
    }
    
    response = requests.post(
        f"{BASE_URL}/get_time_table",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Version: {data.get('version')}")
        print("Timetable Data:")
        for day_data in data.get('data', []):
            print(f"  {day_data.get('day')}:")
            for slot in day_data.get('data', []):
                print(f"    {slot.get('start')}-{slot.get('end')}: {slot.get('value')}")
    else:
        print(f"Error: {response.text}")
    print()

def get_exam_timetable():
    """Get exam timetable for a specific class"""
    print("Getting exam timetable...")
    payload = {
        "filename": "Draft_1_ex.xlsx",
        "class_pattern": "EL 3",
        "is_exam": True
    }
    
    response = requests.post(
        f"{BASE_URL}/get_time_table",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Version: {data.get('version')}")
        print("Exam Schedule:")
        for day_data in data.get('data', []):
            print(f"  {day_data.get('day')}:")
            for slot in day_data.get('data', []):
                print(f"    {slot.get('start')}-{slot.get('end')}: {slot.get('value')}")
                print(f"      Location: {slot.get('location')}")
                print(f"      Invigilator: {slot.get('invigilator')}")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("easeCHAOS API Test Examples")
    print("=" * 30)
    
    # Test health check
    test_health_check()
    
    # Test lecture timetable
    get_lecture_timetable()
    
    # Test exam timetable
    get_exam_timetable()
    
    print("API tests completed!")