import pandas as pd
import urllib.parse
import random
import os
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("EMAIL")

# Directory configuration
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'

CSV_TRAIN = DATA_DIR / 'raw' / 'train.csv'
CSV_CATEGORY = DATA_DIR / 'raw' / 'train_label_to_hierarchical.csv'
DATASET_DIR = DATA_DIR / 'landmark_dataset'
JSONL_OUTPUT = DATA_DIR / 'train.jsonl'

NUM_LABELS = 300
NUM_IMG = 20
MAX_SIZE = (512, 512)
         
NUM_THREADS = 3

PROMPT_TEMPLATES = [
    "Can you identify the landmark shown in this image?",
    "What is the name of the place in this photo?",
    "Where was this picture taken?",
    "Identify the structural marvel or natural feature in this image.",
    "Could you tell me the specific name of this landmark?"
]

random.seed(33)

def extract_data():
    """Extract and filter landmark data, selecting landmarks with balanced image counts."""
    
    df = pd.read_csv(str(CSV_TRAIN))
    df_category = pd.read_csv(str(CSV_CATEGORY))
    
    df_merged = pd.merge(df, df_category, on='landmark_id', how='inner')
    
    counts = df_merged['landmark_id'].value_counts()
    valid_landmarks = counts[(counts >= 25) & (counts <= 35)].index.tolist()
    
    if (len(valid_landmarks) > NUM_LABELS):
        selected_ids = random.sample(valid_landmarks, NUM_LABELS)
    else:
        selected_ids = valid_landmarks
    
    df_final = df_merged[df_merged['landmark_id'].isin(selected_ids)]
    df_final = df_final.groupby('landmark_id').head(NUM_IMG)
    
    df_final['landmark_name'] = df_final['category'].apply(extract_landmark_name)
    
    return df_final


def extract_landmark_name(url: str) -> str | None:
    """Extract landmark name from URL by decoding the last segment."""
    if pd.isna(url):
        return None
    
    name = url.split(':')[-1]
    name = urllib.parse.unquote(name.replace('_', ' '))
    
    return name

def download_image(row: dict) -> dict | None:
    """Download an image from URL and save to local directory."""
    img_id = row['id']
    url = row['url']
    landmark_id = row['landmark_id']
    landmark_name = row['landmark_name']
    
    class_dir = os.path.join(str(DATASET_DIR), str(landmark_id))
    os.makedirs(class_dir, exist_ok=True)
    
    file_path = os.path.join(class_dir, f"{img_id}.jpg")
    
    data_dict = {
        "local_path": file_path,
        "landmark_name": landmark_name
    }
    
    if os.path.exists(file_path):
        return data_dict
    
    headers = {
        'User-Agent': f'LandmarkMultimodalQA/1.0 ({EMAIL}) - Academic Project/Student Research',
        'Accept': 'image/jpeg,image/png,*/*;q=0.8',
    }

    MAX_RETRIES = 3 
    
    for attempt in range(MAX_RETRIES):
        time.sleep(random.uniform(5.0, 10.0))

        try:
            response = requests.get(url, headers=headers, timeout=(5, 10))
            
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                #print(f"Done: {img_id}.jpg")
                return data_dict
                
            elif response.status_code == 429:
                print(f"\n[Code 429] (Attempt: {attempt + 1}/{MAX_RETRIES})")
                time.sleep(30)
                continue
                
            else:
                print(f"\n Error {response.status_code} - ID: {img_id}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"\n Time out (Attempt: {attempt + 1}/{MAX_RETRIES})")
            time.sleep(10)
            continue
            
        except Exception as e:
            return None
            
    print(f"\n Can not download {img_id}")
    return None

def get_all_path_img(dataset_path):
    all_images = []
    for folder_name in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder_name)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    all_images.append(os.path.join(folder_path, filename))
                    
    return all_images

def resize_image(file_path):
    try:
        with Image.open(file_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            
            base_path = os.path.splitext(file_path)[0]
            new_file_path = base_path + ".jpg"
            
            img.save(new_file_path, "JPEG", quality=95)
            
            if file_path.lower() != new_file_path.lower():
                os.remove(file_path)
                
        return True
    except Exception as e:
        print(f"\nError {file_path}: {e}")
        return False
    
def parallel_resize_dataset(dataset_dir, max_workers=8):
    all_images = get_all_path_img(dataset_dir)
    total_images = len(all_images)
    successful = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(resize_image, path): path for path in all_images}
        
        # Hiển thị thanh tiến trình
        for future in tqdm(
            as_completed(futures), 
            total=total_images, 
            desc="Resizing Images"
        ):
            try:
                if future.result(): 
                    successful += 1
            except Exception as e:
                img_path = futures[future]
                print(f"\nError {img_path}: {e}")

    print(f"\nSuccessfully resize {successful}/{len(all_images)} images")
    
def create_qa_pair(image_path, landmark_name):
    question = random.choice(PROMPT_TEMPLATES)

    answer = f"Based on the visual features, this is {landmark_name}."
    
    format_qa = {
        "image": image_path, 
        
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": "You are a highly capable AI assistant specialized in identifying global landmarks."}]},
            {"role": "user", "content": [
                {"type": "image"}, 
                {"type": "text", "text": question}
            ]},
            {"role": "assistant", "content": [
                {"type": "text", "text": answer}
            ]}
        ]
    }
    return format_qa
    
def create_model_dataset(df, file_output, dataset_dir):
    id_to_name = dict(zip(df['landmark_id'].astype(str), df['landmark_name']))
    
    base_dataset_folder = os.path.basename(os.path.normpath(dataset_dir))

    qa_pairs_count = 0

    with open(file_output, 'w', encoding='utf-8') as f:
        
        for folder_name in os.listdir(dataset_dir):
            folder_path = os.path.join(dataset_dir, folder_name)
            
            if os.path.isdir(folder_path):
                
                true_landmark_name = id_to_name.get(folder_name, "Unknown Landmark")
                
                for filename in os.listdir(folder_path):
                    #img_path = os.path.join(folder_path, filename)
                    hf_relative_path = f"{folder_name}/{filename}"
                    
                    format_qa = create_qa_pair(hf_relative_path, true_landmark_name)
                    
                    f.write(json.dumps(format_qa, ensure_ascii=False) + '\n')
                    qa_pairs_count += 1
    print(f"Successfully create {qa_pairs_count} QA pairs")
    
def main():
    print("EXTRACTING DATA")
    
    df_final = extract_data()
    df_final.to_csv(str(DATA_DIR / "processed" / "extracted_train_1.csv"), index=False)
    
    df_final = pd.read_csv(str(DATA_DIR / "processed" / "extracted_train.csv"))
    
    print("DOWNLOADING IMAGES\n")
    
    tasks = df_final.to_dict('records')
    successful_downloads = []

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(download_image, task) for task in tasks]
        
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Downloading images"
        ):
            res = future.result()
            if res is not None:
                successful_downloads.append(res)
                
    print(
        f"Successfully downloaded {len(successful_downloads)}/{len(df_final)} images."
    )
    
    # RESIZE IMAGE
    print("RESIZE IMAGE")
    all_images = get_all_path_img(DATASET_DIR)
    
    successful = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(resize_image, path) for path in all_images]
        for future in tqdm(
            as_completed(futures), 
            total=len(futures), 
            desc="Resizing"
        ):
            if future.result():
                successful += 1

    print(f"\nSuccessfully resize {successful}/{len(all_images)} images")
    
    # CREATE QA DATASET
    create_model_dataset(df=df_final, file_output=JSONL_OUTPUT, dataset_dir=DATASET_DIR)