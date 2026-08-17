# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 جاري تشغيل السيرفر...")
    print("📍 افتح المتصفح على: http://127.0.0.1:5000")
    print("👤 حسابات تجريبية:")
    print("   Adminerp / 1234 (مدير)")
    print("   Fahd01 / 1234 (مدير)")
    print("   employee1 / 1234 (موظف)")
    print("   viewer1 / 1234 (مراقب)")
    app.run(debug=True, host='0.0.0.0', port=5000)