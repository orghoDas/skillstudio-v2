"""Test dashboard endpoint directly"""
import asyncio
import httpx

async def test_dashboard():
    # First login
    async with httpx.AsyncClient() as client:
        # Login as demo user
        login_response = await client.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            json={
                "email": "demo@learningplatform.com",
                "password": "demo1234"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()["access_token"]
        print(f"✅ Logged in successfully")
        
        # Test dashboard
        headers = {"Authorization": f"Bearer {token}"}
        dashboard_response = await client.get(
            "http://127.0.0.1:8000/api/v1/ai/dashboard",
            headers=headers
        )
        
        print(f"\n📊 Dashboard Response ({dashboard_response.status_code}):")
        if dashboard_response.status_code == 200:
            print(dashboard_response.json())
        else:
            print(dashboard_response.text)

if __name__ == "__main__":
    asyncio.run(test_dashboard())
