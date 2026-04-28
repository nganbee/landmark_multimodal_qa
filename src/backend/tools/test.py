import os
from dotenv import load_dotenv
# Import cái tool của bạn (giả sử file chứa tool tên là weather_tool.py)
from weather_tool import get_current_weather 

# 1. Load biến môi trường từ file .env
load_dotenv()

def test_tool():
    print("--- BẮT ĐẦU KIỂM TRA WEATHER TOOL ---")
    
    # Kiểm tra xem API Key có load được không
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("❌ LỖI: Không tìm thấy WEATHER_API_KEY trong file .env")
        return

    # 2. Test với các trường hợp khác nhau
    test_cities = ["Hanoi", "Ho Chi Minh City", "InvalidCity123"]

    for city in test_cities:
        print(f"\nĐang gọi API cho: {city}...")
        try:
            # SỬA Ở ĐÂY: Dùng .invoke() với input là dict
            result = get_current_weather.invoke({"location_name": city})
            
            print(f"Kết quả trả về: {result}")
            
            # Kiểm tra logic trả về
            if "error" in result:
                print(f"⚠️ API báo lỗi: {result['error']}")
            else:
                print(f"✅ THÀNH CÔNG: Nhiệt độ tại {city} là {result.get('temp')}°C")
                
        except Exception as e:
            print(f"❌ LỖI HỆ THỐNG: {str(e)}")

if __name__ == "__main__":
    test_tool()