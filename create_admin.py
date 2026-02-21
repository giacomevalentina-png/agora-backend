import requests

API_URL = "https://agora-backend-production-2347.up.railway.app/api"

admin_data = {
    'name': 'Admin',
    'email': 'admin@agora.com',
    'password': 'admin123'
}

response = requests.post(f'{API_URL}/auth/signup', json=admin_data)

if response.status_code == 201:
    print("✅ Admin account created!")
    print(f"Email: admin@agora.com")
    print(f"Password: admin123")
else:
    print(f"❌ Error: {response.json()}")
