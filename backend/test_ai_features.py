"""
Test script for AI features
Run after server is started: python test_ai_features.py
"""
import asyncio
import httpx
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Test credentials
TEST_USER = {
    "email": "ai_test@example.com",
    "password": "TestPassword123!",
    "full_name": "AI Test User"
}

async def main():
    async with httpx.AsyncClient() as client:
        print("🚀 Testing SkillStudio AI Features\n")
        
        # 1. Register user
        print("1️⃣  Registering test user...")
        access_token = None
        try:
            register_response = await client.post(
                f"{BASE_URL}/auth/register",
                json=TEST_USER
            )
            if register_response.status_code == 200:
                print("✅ User registered successfully")
                data = register_response.json()
                access_token = data["access_token"]
            elif register_response.status_code == 400:
                # User already exists, login instead
                print("ℹ️  User already exists, logging in...")
                login_response = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "email": TEST_USER["email"],
                        "password": TEST_USER["password"]
                    }
                )
                login_response.raise_for_status()
                access_token = login_response.json()["access_token"]
                print("✅ Logged in successfully")
            else:
                register_response.raise_for_status()
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        if not access_token:
            print("❌ Failed to get access token")
            return
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Create a learning goal
        print("\n2️⃣  Creating learning goal...")
        try:
            goal_response = await client.post(
                f"{BASE_URL}/learning/goals",
                json={
                    "goal_description": "Master Python Web Development with FastAPI, SQLAlchemy, and async programming",
                    "target_role": "Full Stack Python Developer",
                    "target_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs"],
                    "target_completion_date": (datetime.now() + timedelta(days=90)).date().isoformat()
                },
                headers=headers
            )
            goal_response.raise_for_status()
            goal_id = goal_response.json()["id"]
            print(f"✅ Learning goal created: {goal_id}")
        except Exception as e:
            print(f"❌ Error creating goal: {e}")
            # Try to get existing goals
            try:
                goals_response = await client.get(f"{BASE_URL}/learning/goals", headers=headers)
                goals = goals_response.json()
                if goals:
                    goal_id = goals[0]["id"]
                    print(f"ℹ️  Using existing goal: {goal_id}")
                else:
                    return
            except:
                return
        
        # 3. Generate AI Learning Path
        print("\n3️⃣  Generating AI-powered learning path...")
        try:
            path_response = await client.post(
                f"{BASE_URL}/ai/generate-learning-path",
                params={"goal_id": goal_id},
                headers=headers
            )
            path_response.raise_for_status()
            path_data = path_response.json()
            print("✅ Learning path generated!")
            print(f"   📚 Recommended courses: {len(path_data.get('learning_path', []))}")
            print(f"   ⏱️  Estimated hours: {path_data.get('metadata', {}).get('total_hours', 0)}")
            print(f"   🎯 Confidence: {path_data.get('confidence_score', 0):.2f}")
        except httpx.HTTPStatusError as e:
            print(f"❌ Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"❌ Error generating path: {e}")
        
        # 4. Get AI Dashboard
        print("\n4️⃣  Fetching AI Dashboard...")
        try:
            dashboard_response = await client.get(
                f"{BASE_URL}/ai/dashboard",
                headers=headers
            )
            dashboard_response.raise_for_status()
            dashboard = dashboard_response.json()
            print("✅ Dashboard loaded!")
            print(f"   📊 Performance data: {len(dashboard.get('performance', {}))} metrics")
            print(f"   💡 Active recommendations: {len(dashboard.get('recommendations', []))}")
            print(f"   🎓 Learning goals tracked: {len(dashboard.get('learning_goals', []))}")
            
            # Show AI insights
            insights = dashboard.get('ai_insights', {})
            print(f"\n   🤖 AI Insights:")
            print(f"      • Overall progress: {insights.get('overall_progress', 'N/A')}")
            print(f"      • Engagement level: {insights.get('engagement_level', 'N/A')}")
            if insights.get('next_milestone'):
                print(f"      • Next milestone: {insights['next_milestone']}")
            
        except Exception as e:
            print(f"❌ Error fetching dashboard: {e}")
        
        # 5. Get Recommendations
        print("\n5️⃣  Fetching personalized recommendations...")
        try:
            rec_response = await client.get(
                f"{BASE_URL}/ai/recommendations",
                headers=headers
            )
            rec_response.raise_for_status()
            recommendations = rec_response.json()
            print(f"✅ Found {len(recommendations)} recommendations")
            
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"\n   {i}. {rec['recommendation_type'].replace('_', ' ').title()}")
                print(f"      Reason: {rec['reason'][:80]}...")
                print(f"      Priority: {rec['priority']}/10")
                print(f"      Confidence: {rec.get('confidence_score', 0):.2f}")
                
        except Exception as e:
            print(f"❌ Error fetching recommendations: {e}")
        
        # 6. Get Performance Summary
        print("\n6️⃣  Fetching performance analytics...")
        try:
            perf_response = await client.get(
                f"{BASE_URL}/ai/performance",
                headers=headers
            )
            perf_response.raise_for_status()
            performance = perf_response.json()
            print("✅ Performance analytics loaded!")
            print(f"   📈 Lessons completed: {performance.get('lessons_completed', 0)}")
            print(f"   ⭐ Average quiz score: {performance.get('average_quiz_score', 0):.1f}%")
            print(f"   🔥 Current streak: {performance.get('streak_days', 0)} days")
            print(f"   ⏰ Study hours (30d): {performance.get('total_study_hours', 0):.1f}h")
            
        except Exception as e:
            print(f"❌ Error fetching performance: {e}")
        
        print("\n" + "="*60)
        print("🎉 AI Features Test Complete!")
        print("="*60)
        print(f"\n📖 Access full API docs: http://127.0.0.1:8000/docs")
        print(f"🤖 AI Dashboard endpoint: GET {BASE_URL}/ai/dashboard")
        print(f"💡 Your access token (valid 30min):")
        print(f"   {access_token[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())
