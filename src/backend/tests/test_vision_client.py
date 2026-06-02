from PIL import Image

from src.backend.app.vision.vision_client import (
    vision_client
)


image = Image.open(
    "test1.jpg"
)


result = vision_client.analyze_landmark(

    image=image,

    user_query=
    "Identify this landmark and explain it."
)

print(result)