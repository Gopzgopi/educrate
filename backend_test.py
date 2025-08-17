import requests
import sys
import json
from datetime import datetime

class EduCrateAPITester:
    def __init__(self, base_url="https://smart-educrate.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.kit_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_create_user(self):
        """Test user creation"""
        user_data = {
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "learning_styles": [],
            "preferred_language": "en",
            "timezone": "UTC"
        }
        
        success, response = self.run_test(
            "Create User",
            "POST",
            "api/users",
            200,
            data=user_data
        )
        
        if success and 'user_id' in response:
            self.user_id = response['user_id']
            print(f"   Created user with ID: {self.user_id}")
            return True
        return False

    def test_get_user(self):
        """Test getting user by ID"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        return self.run_test(
            "Get User",
            "GET",
            f"api/users/{self.user_id}",
            200
        )[0]

    def test_assessment_questions(self):
        """Test getting assessment questions"""
        return self.run_test(
            "Get Assessment Questions",
            "GET",
            "api/learning-assessment-questions",
            200
        )[0]

    def test_save_assessment(self):
        """Test saving learning assessment"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False

        assessment_data = {
            "user_id": self.user_id,
            "visual_score": 8,
            "auditory_score": 6,
            "textual_score": 9,
            "kinesthetic_score": 5,
            "answers": {
                "1": "textual",
                "2": "visual", 
                "3": "textual",
                "4": "textual",
                "5": "visual"
            }
        }
        
        return self.run_test(
            "Save Assessment",
            "POST",
            f"api/users/{self.user_id}/assessment",
            200,
            data=assessment_data
        )[0]

    def test_create_learning_kit(self):
        """Test creating a learning kit"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False

        params = {
            "user_id": self.user_id,
            "topic": "Machine Learning Basics",
            "source_content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It includes supervised learning, unsupervised learning, and reinforcement learning approaches."
        }
        
        success, response = self.run_test(
            "Create Learning Kit",
            "POST",
            "api/learning-kits",
            200,
            params=params
        )
        
        if success and 'kit' in response:
            self.kit_id = response['kit']['id']
            print(f"   Created kit with ID: {self.kit_id}")
            return True
        return False

    def test_get_user_kits(self):
        """Test getting user's learning kits"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        return self.run_test(
            "Get User Learning Kits",
            "GET",
            f"api/users/{self.user_id}/learning-kits",
            200
        )[0]

    def test_get_learning_kit(self):
        """Test getting specific learning kit"""
        if not self.kit_id:
            print("❌ No kit ID available for testing")
            return False
            
        return self.run_test(
            "Get Learning Kit",
            "GET",
            f"api/learning-kits/{self.kit_id}",
            200
        )[0]

    def test_start_study_session(self):
        """Test starting a study session"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False

        session_data = {
            "user_id": self.user_id,
            "mood": "focused",
            "available_time": 30,
            "energy_level": 7,
            "focus_level": 8,
            "preferred_content_types": ["summary", "flashcards"]
        }
        
        return self.run_test(
            "Start Study Session",
            "POST",
            f"api/users/{self.user_id}/study-session",
            200,
            data=session_data
        )[0]

    def test_qa_session(self):
        """Test QA session"""
        if not self.user_id or not self.kit_id:
            print("❌ No user ID or kit ID available for testing")
            return False

        params = {
            "user_id": self.user_id,
            "kit_id": self.kit_id,
            "question": "What is supervised learning?"
        }
        
        return self.run_test(
            "QA Session",
            "POST",
            "api/qa-sessions",
            200,
            params=params
        )[0]

    def test_user_analytics(self):
        """Test user analytics"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
            
        return self.run_test(
            "Get User Analytics",
            "GET",
            f"api/users/{self.user_id}/analytics",
            200
        )[0]

def main():
    print("🚀 Starting EduCrate API Testing...")
    print("=" * 50)
    
    tester = EduCrateAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Create User", tester.test_create_user),
        ("Get User", tester.test_get_user),
        ("Assessment Questions", tester.test_assessment_questions),
        ("Save Assessment", tester.test_save_assessment),
        ("Create Learning Kit", tester.test_create_learning_kit),
        ("Get User Kits", tester.test_get_user_kits),
        ("Get Learning Kit", tester.test_get_learning_kit),
        ("Start Study Session", tester.test_start_study_session),
        ("QA Session", tester.test_qa_session),
        ("User Analytics", tester.test_user_analytics)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())