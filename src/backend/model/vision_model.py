import requests
import base64
from io import BytesIO

class LandmarkModel:
    def __init__(self, pinggy_url):
        self.url = pinggy_url

    def predict(self, image, prompt="Can you tell me the name of the landmark shown in the image?"):
        
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        
        response = requests.post(
            f"{self.url}/predict_landmark",
            files={"file": buffered.getvalue()},
            data={"prompt": prompt}
        )
        
        return response.json()