import math
from PIL import Image

def pad_to_square(img):
    """Pads an image to make it a perfect square using black background."""
    w, h = img.size
    size = max(w, h)
    new_img = Image.new("RGB", (size, size), (0, 0, 0))
    new_img.paste(img, ((size - w) // 2, (size - h) // 2))
    return new_img

def smart_resize_by_tokens(img, target_tokens=196, patch_size=28):
    """Resizes an image intelligently based on token count and patch size."""
    w, h = img.size
    target_grid = int(math.sqrt(target_tokens))

    scale = (target_grid * patch_size) / max(w, h)
    scale = min(scale, 1.0)

    new_w = int(w * scale)
    new_h = int(h * scale)

    new_w = max(patch_size, (new_w // patch_size) * patch_size)
    new_h = max(patch_size, (new_h // patch_size) * patch_size)

    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.LANCZOS

    return img.resize((new_w, new_h), resample_filter)

def preprocess_image(image_input):
    """
    Main entry point for image preprocessing.
    Expects either a file path (str) or a PIL Image object.
    """
    if isinstance(image_input, str):
        image = Image.open(image_input).convert("RGB")
    else:
        image = image_input.convert("RGB")

    image = pad_to_square(image)
    image = smart_resize_by_tokens(image)
    return image
