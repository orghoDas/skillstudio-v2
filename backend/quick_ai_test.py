"""
Quick AI Features Test with Sample Users
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Use existing sample user
email = "sarah.developer@demo.com"
password = "demo1234"

print("="*80)
print("🤖 TESTING AI FEATURES")
print("="*80)

# Login
print(f"\n🔐 Logging in as {email}...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": email, "password": password}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

token = response.json()["access_token"]
print("✅ Login successful!")

headers = {"Authorization": f"Bearer {token}"}

# Test 1: Course Recommendations
print(f"\n{'='*80}")
print("📚 TEST 1: AI COURSE RECOMMENDATIONS")
print(f"{'='*80}")

response = requests.get(f"{BASE_URL}/ai/recommendations?limit=5", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Received {len(data['recommendations'])} personalized recommendations:\n")
    
    for i, rec in enumerate(data['recommendations'][:3], 1):
        print(f"{i}. {rec['title']}")
        print(f"   Score: {rec['recommendation_score']}/100")
        print(f"   Difficulty: {rec['difficulty_level']} | Duration: {rec['estimated_duration_hours']}hrs")
        print(f"   Why recommended:")
        for reason in rec['reasons'][:2]:
            print(f"      • {reason}")
        print()
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")

# Test 2: Learning Path
print(f"\n{'='*80}")
print("🛤️  TEST 2: PERSONALIZED LEARNING PATH")
print(f"{'='*80}")

response = requests.get(f"{BASE_URL}/ai/learning-path", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"\n🎯 Goal: {data['goal']['description']}")
    print(f"   Target Role: {data['goal']['target_role']}")
    print(f"   Progress: {data['completion_percentage']}%")
    print(f"\n📚 Recommended Learning Path ({len(data['learning_path'])} courses):\n")
    
    for course in data['learning_path'][:3]:
        print(f"   Step {course['sequence']}: {course['title']}")
        print(f"      Skills: {', '.join(course['skills_gained'])}")
        print(f"      Duration: {course['duration_hours']} hours")
        print()
    
    print(f"⏱️  Timeline: {data['timeline']['estimated_weeks']} weeks ({data['timeline']['total_hours']} hours)")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")

# Test 3: Skill Gap Analysis
print(f"\n{'='*80}")
print("📊 TEST 3: SKILL GAP ANALYSIS")
print(f"{'='*80}")

response = requests.get(f"{BASE_URL}/ai/skill-gap-analysis", headers=headers)
if response.status_code == 200:
    data = response.json()
    
    print(f"\n💪 Your Strengths:")
    if data['strengths']:
        for strength in data['strengths'][:3]:
            print(f"   • {strength['skill']} (Level {strength['level']})")
    else:
        print("   Building foundation...")
    
    print(f"\n📈 Top Skill Gaps:")
    for gap in data['skill_gaps'][:5]:
        print(f"   • {gap['skill']} - {gap['priority'].upper()} priority (Current: {gap['current_level']})")
    
    print(f"\n🎯 Overall Readiness: {data['overall_readiness']['percentage']}%")
    print(f"   Status: {data['overall_readiness']['status'].replace('_', ' ').title()}")
    
    print(f"\n💡 Recommendations:")
    for rec in data['recommendations']:
        print(f"   • {rec['message']}")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")

# Test 4: Next Best Action
print(f"\n{'='*80}")
print("🎯 TEST 4: NEXT BEST ACTION")
print(f"{'='*80}")

response = requests.get(f"{BASE_URL}/ai/next-best-action", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"\n✨ Recommended: {data['action'].replace('_', ' ').title()}")
    print(f"   💡 {data['reason']}")
else:
    print(f"❌ Failed: {response.status_code} - {response.text}")

print(f"\n{'='*80}")
print("✅ AI FEATURES TEST COMPLETE!")
print(f"{'='*80}")
print("\n📖 View full API documentation at: http://localhost:8000/docs")
