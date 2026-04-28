# import os
# import torch
# from dotenv import load_dotenv
# from huggingface_hub import login
# from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
# from peft import PeftModel

# # ================== ENV SETUP ==================
# load_dotenv()

# # HF cache (portable)
# hf_home = os.getenv("HF_HOME", "./hf_cache")
# os.makedirs(hf_home, exist_ok=True)
# os.environ["HF_HOME"] = hf_home

# # HuggingFace login
# token = os.getenv("HF_TOKEN")
# if token:
#     login(token)


# # ================== MODEL LOADER ==================
# class ModelLoader:
#     def __init__(self):
#         self.model = None
#         self.processor = None

#         # 🔥 device control via ENV
#         self.device = os.getenv("DEVICE", "cpu")

#     def load(
#         self,
#         base_model="Qwen/Qwen2.5-VL-3B-Instruct",
#         lora_path="imbee510/qwen2-5-vl-landmark-lora"
#     ):
#         print(f"--- Running on: {self.device.upper()} ---")

#         # 1. Load Processor
#         print("Loading processor...")
#         self.processor = AutoProcessor.from_pretrained(
#             base_model,
#             trust_remote_code=True
#         )

#         # 2. Setup dtype
#         dtype = torch.float16 if self.device in ["cuda", "auto"] else torch.float32

#         # 3. Setup device_map
#         if self.device == "auto":
#             device_map = "auto"
#         else:
#             device_map = {"": self.device}

#         # 4. Load Base Model 
#         print("Loading base model...")
#         self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
#             base_model,
#             torch_dtype=dtype,
#             device_map=device_map,
#             trust_remote_code=True,
#             low_cpu_mem_usage=True
#         )

#         # 5. Load LoRA
#         if lora_path:
#             print(f"Loading LoRA adapter: {lora_path}...")
#             self.model = PeftModel.from_pretrained(
#                 self.model,
#                 lora_path
#             )

#         self.model.eval()

#         print("✅ Model + LoRA loaded successfully!")
#         return self.model, self.processor


# # ================== RUN ==================
# if __name__ == "__main__":
#     loader = ModelLoader()
#     model, processor = loader.load()

import os
import torch
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
# from transformers import AutoProcessor, AutoModel 
from peft import PeftModel

load_dotenv()

hf_home = os.getenv("HF_HOME", "./hf_cache")
os.makedirs(hf_home, exist_ok=True)
os.environ["HF_HOME"] = hf_home

token = os.getenv("HF_TOKEN")
if token:
    login(token)

_model = None
_processor = None


class ModelLoader:
    def __init__(self):
        self.device = os.getenv("DEVICE", "cpu")

    def load(self,
             base_model="Qwen/Qwen2.5-VL-3B-Instruct",
             lora_path="imbee510/qwen2-5-vl-landmark-lora"):

        print(f"--- Running on: {self.device.upper()} ---")

        processor = AutoProcessor.from_pretrained(
            base_model,
            trust_remote_code=True
        )

        dtype = torch.float16 if self.device in ["cuda", "auto"] else torch.float32
        device_map = "auto" if self.device == "auto" else {"": self.device}
        # model = AutoModel.from_pretrained(
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            base_model,
            torch_dtype=dtype,
            device_map=device_map,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        if lora_path:
            model = PeftModel.from_pretrained(model, lora_path)

        model.eval()

        print("✅ Model loaded!")
        return model, processor


def get_model():
    global _model, _processor

    if _model is not None:
        print("⚡ Using cached model")
        return _model, _processor

    print("🔥 First time loading model...")
    loader = ModelLoader()
    _model, _processor = loader.load()

    return _model, _processor