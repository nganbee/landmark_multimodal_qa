import pandas as pd
import urllib.parse
import random
import os
import time
import json
import shutil
import uuid
import requests
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import albumentations as A

load_dotenv()
EMAIL = os.getenv("EMAIL")

# Directory configuration
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

CSV_TRAIN = DATA_DIR / "raw" / "train.csv"
CSV_CATEGORY = DATA_DIR / "raw" / "train_label_to_hierarchical.csv"
DATASET_DIR = DATA_DIR / "landmark_dataset"
JSONL_OUTPUT = DATA_DIR / "train.jsonl"

NUM_LABELS = 300
NUM_IMG = 20
MAX_SIZE = (512, 512)
NUM_THREADS = 3

PROMPT_TEMPLATES = [
    "Can you identify the landmark shown in this image?",
    "What is the name of the place in this photo?",
    "Where was this picture taken?",
    "Identify the structural marvel or natural feature in this image.",
    "Could you tell me the specific name of this landmark?",
]

random.seed(33)


def extract_landmark_name(url: str) -> str | None:
    """Extract a human-readable landmark name from a Wikidata/Wikipedia category URL."""
    if pd.isna(url):
        return None
    name = url.split(":")[-1]
    name = urllib.parse.unquote(name.replace("_", " "))
    return name


def extract_data(
    csv_train: str | Path = CSV_TRAIN,
    csv_category: str | Path = CSV_CATEGORY,
    num_labels: int = NUM_LABELS,
    num_img: int = NUM_IMG,
) -> pd.DataFrame:
    """Extract and filter landmark data, selecting landmarks with balanced image counts.

    Args:
        csv_train: Path to the raw train CSV.
        csv_category: Path to the label-to-hierarchical CSV.
        num_labels: Maximum number of landmark classes to keep.
        num_img: Maximum images per landmark class.

    Returns:
        Filtered and merged DataFrame with a ``landmark_name`` column.
    """
    df = pd.read_csv(str(csv_train))
    df_category = pd.read_csv(str(csv_category))

    df_merged = pd.merge(df, df_category, on="landmark_id", how="inner")

    counts = df_merged["landmark_id"].value_counts()
    valid_landmarks = counts[(counts >= 25) & (counts <= 35)].index.tolist()

    if len(valid_landmarks) > num_labels:
        selected_ids = random.sample(valid_landmarks, num_labels)
    else:
        selected_ids = valid_landmarks

    df_final = df_merged[df_merged["landmark_id"].isin(selected_ids)]
    df_final = df_final.groupby("landmark_id").head(num_img)
    df_final["landmark_name"] = df_final["category"].apply(extract_landmark_name)

    return df_final


# ---------------------------------------------------------------------------
# Image downloading
# ---------------------------------------------------------------------------

def download_image(row: dict, dataset_dir: str | Path = DATASET_DIR) -> dict | None:
    """Download a single image from its URL and save it to *dataset_dir*.

    Args:
        row: A record dict with keys ``id``, ``url``, ``landmark_id``, ``landmark_name``.
        dataset_dir: Root directory where ``<landmark_id>/<img_id>.jpg`` will be saved.

    Returns:
        A dict ``{"local_path": ..., "landmark_name": ...}`` on success, else ``None``.
    """
    img_id = row["id"]
    url = row["url"]
    landmark_id = row["landmark_id"]
    landmark_name = row["landmark_name"]

    class_dir = os.path.join(str(dataset_dir), str(landmark_id))
    os.makedirs(class_dir, exist_ok=True)

    file_path = os.path.join(class_dir, f"{img_id}.jpg")

    data_dict = {"local_path": file_path, "landmark_name": landmark_name}

    if os.path.exists(file_path):
        return data_dict

    headers = {
        "User-Agent": f"LandmarkMultimodalQA/1.0 ({EMAIL}) - Academic Project/Student Research",
        "Accept": "image/jpeg,image/png,*/*;q=0.8",
    }

    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        time.sleep(random.uniform(5.0, 10.0))

        try:
            response = requests.get(url, headers=headers, timeout=(5, 10))

            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
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

        except Exception:
            return None

    print(f"\n Can not download {img_id}")
    return None


def parallel_download(
    df: pd.DataFrame,
    dataset_dir: str | Path = DATASET_DIR,
    num_threads: int = NUM_THREADS,
) -> list[dict]:
    """Download all images in *df* in parallel.

    Args:
        df: DataFrame with image records (must have columns used by :func:`download_image`).
        dataset_dir: Root directory for saving images.
        num_threads: Number of concurrent download threads.

    Returns:
        List of successful result dicts from :func:`download_image`.
    """
    tasks = df.to_dict("records")
    successful: list[dict] = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(download_image, task, dataset_dir) for task in tasks]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading images"):
            res = future.result()
            if res is not None:
                successful.append(res)

    return successful


# ---------------------------------------------------------------------------
# Image resizing
# ---------------------------------------------------------------------------

def get_all_path_img(dataset_path: str | Path) -> list[str]:
    """Recursively collect all image file paths under *dataset_path*."""
    all_images: list[str] = []
    for folder_name in os.listdir(dataset_path):
        folder_path = os.path.join(str(dataset_path), folder_name)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    all_images.append(os.path.join(folder_path, filename))
    return all_images


def resize_image(file_path: str, max_size: tuple[int, int] = MAX_SIZE) -> bool:
    """Resize a single image in-place to fit within *max_size*, converting to JPEG.

    Args:
        file_path: Absolute path to the image file.
        max_size: Maximum (width, height) after ``thumbnail`` resize.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    try:
        with Image.open(file_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            base_path = os.path.splitext(file_path)[0]
            new_file_path = base_path + ".jpg"

            img.save(new_file_path, "JPEG", quality=95)

            if file_path.lower() != new_file_path.lower():
                os.remove(file_path)

        return True
    except Exception as e:
        print(f"\nError {file_path}: {e}")
        return False


def parallel_resize_dataset(
    dataset_dir: str | Path,
    max_size: tuple[int, int] = MAX_SIZE,
    max_workers: int = 8,
) -> None:
    """Resize all images in *dataset_dir* in parallel.

    Args:
        dataset_dir: Root directory containing class sub-folders with images.
        max_size: Maximum (width, height) passed to :func:`resize_image`.
        max_workers: Number of concurrent worker threads.
    """
    all_images = get_all_path_img(dataset_dir)
    total_images = len(all_images)
    successful = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(resize_image, path, max_size): path for path in all_images}

        for future in tqdm(as_completed(futures), total=total_images, desc="Resizing Images"):
            try:
                if future.result():
                    successful += 1
            except Exception as e:
                img_path = futures[future]
                print(f"\nError {img_path}: {e}")

    print(f"\nSuccessfully resize {successful}/{total_images} images")


# ---------------------------------------------------------------------------
# QA dataset creation
# ---------------------------------------------------------------------------

def create_qa_pair(image_path: str, landmark_name: str) -> dict:
    """Build a single multimodal QA record for fine-tuning.

    Args:
        image_path: Relative or absolute path / HF-relative path to the image.
        landmark_name: Ground-truth landmark name used as the answer.

    Returns:
        A dict with ``image`` and ``messages`` keys following the chat format.
    """
    question = random.choice(PROMPT_TEMPLATES)
    answer = f"Based on the visual features, this is {landmark_name}."

    return {
        "image": image_path,
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a highly capable AI assistant specialized in identifying global landmarks.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": question},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": answer}],
            },
        ],
    }


def create_model_dataset(
    df: pd.DataFrame,
    file_output: str | Path,
    dataset_dir: str | Path,
) -> None:
    """Write a JSONL file of multimodal QA pairs for every image in *dataset_dir*.

    The function maps each class folder name (landmark_id) to its landmark name
    via *df*, then writes one JSON line per image using :func:`create_qa_pair`.

    Args:
        df: DataFrame containing at least ``landmark_id`` and ``landmark_name`` columns.
        file_output: Path of the output ``.jsonl`` file to write.
        dataset_dir: Root directory containing ``<landmark_id>/`` sub-folders.
    """
    id_to_name = dict(zip(df["landmark_id"].astype(str), df["landmark_name"]))
    qa_pairs_count = 0

    with open(str(file_output), "w", encoding="utf-8") as f:
        for folder_name in os.listdir(str(dataset_dir)):
            folder_path = os.path.join(str(dataset_dir), folder_name)

            if os.path.isdir(folder_path):
                true_landmark_name = id_to_name.get(folder_name, "Unknown Landmark")

                for filename in os.listdir(folder_path):
                    hf_relative_path = f"{folder_name}/{filename}"
                    format_qa = create_qa_pair(hf_relative_path, true_landmark_name)
                    f.write(json.dumps(format_qa, ensure_ascii=False) + "\n")
                    qa_pairs_count += 1

    print(f"Successfully create {qa_pairs_count} QA pairs")


# ---------------------------------------------------------------------------
# Folder syncing
# ---------------------------------------------------------------------------

def sync_folder_task(folder_name: str, source_parent: str, target_parent: str) -> bool:
    """Copy a single sub-folder from *source_parent* into *target_parent*, replacing it if it exists.

    Args:
        folder_name: Name of the sub-folder to copy.
        source_parent: Directory that contains *folder_name*.
        target_parent: Destination directory where *folder_name* will be placed.

    Returns:
        ``True`` on success, ``False`` on any exception.
    """
    path_in_target = os.path.join(target_parent, folder_name)
    path_in_source = os.path.join(source_parent, folder_name)

    try:
        if os.path.exists(path_in_target):
            shutil.rmtree(path_in_target)
        shutil.copytree(path_in_source, path_in_target)
        return True
    except Exception:
        return False


def parallel_sync_folders(
    path_target: str | Path,
    path_source: str | Path,
    max_workers: int = 4,
) -> None:
    """Sync all sub-folders from *path_source* into *path_target* in parallel.

    Args:
        path_target: Destination root directory.
        path_source: Source root directory whose sub-folders are copied.
        max_workers: Number of concurrent worker threads.
    """
    path_source = str(path_source)
    path_target = str(path_target)

    folders_to_copy = [
        f for f in os.listdir(path_source) if os.path.isdir(os.path.join(path_source, f))
    ]
    total_folders = len(folders_to_copy)
    successful = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(sync_folder_task, folder, path_source, path_target): folder
            for folder in folders_to_copy
        }

        for future in tqdm(as_completed(futures), total=total_folders, desc="Syncing"):
            try:
                if future.result():
                    successful += 1
            except Exception as e:
                print(f"\nError folder: {futures[future]}: {e}")

    print(f"\nSuccessfully synced {successful}/{total_folders} folders")


# ---------------------------------------------------------------------------
# File cleaning utilities
# ---------------------------------------------------------------------------

def clean_non_jpg_files(root_dir: str | Path, max_workers: int = 8) -> None:
    """Delete all non-JPEG files under *root_dir* in parallel.

    Args:
        root_dir: Root directory to scan recursively.
        max_workers: Number of concurrent worker threads.
    """
    all_files: list[str] = []
    for root, _, files in os.walk(str(root_dir)):
        for file in files:
            all_files.append(os.path.join(root, file))

    total_files = len(all_files)
    deleted_count = 0

    def _delete_task(file_path: str) -> bool:
        if not file_path.lower().endswith(".jpg"):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error {file_path}: {e}")
        return False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_delete_task, f): f for f in all_files}

        for future in tqdm(as_completed(futures), total=total_files, desc="Cleaning files"):
            if future.result():
                deleted_count += 1

    print(f"\nDone: deleted {deleted_count} non-.jpg files.")


def count_images_in_folder(folder_path: str | Path) -> int:
    """Recursively count image files (.jpg, .jpeg, .png, .webp) under *folder_path*.

    Args:
        folder_path: Root directory to scan.

    Returns:
        Total number of image files found.
    """
    valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
    total = 0
    for _, _, files in os.walk(str(folder_path)):
        total += sum(1 for f in files if f.lower().endswith(valid_extensions))
    return total


def check_split_length(base_path: str | Path) -> None:
    """Print a formatted summary of image counts for train / val / test splits.

    Args:
        base_path: Root directory that contains ``train``, ``val``, and ``test`` sub-folders.
    """
    print(f"{'Split':<10} | {'Total Images':<15}")
    print("-" * 30)

    for split in ["train", "val", "test"]:
        split_dir = os.path.join(str(base_path), split)
        if not os.path.exists(split_dir):
            print(f"{split:<10} | Folder not found!")
            continue

        count = sum(
            len(files)
            for _, _, files in os.walk(split_dir)
            if any(f.lower().endswith((".jpg", ".jpeg", ".png")) for f in files)
        )
        print(f"{split.upper():<10} | {count:<15}")


# ---------------------------------------------------------------------------
# Data augmentation
# ---------------------------------------------------------------------------

#: Default albumentations transform pipeline used by :func:`data_augmentation_parallel`.
DEFAULT_AUGMENTATION_TRANSFORM = A.Compose([
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),
    A.Perspective(scale=(0.05, 0.1), p=0.5),
    A.Sharpen(alpha=(0.2, 0.5), lightness=(0.5, 1.0), p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.RandomFog(fog_coef_lower=0.05, fog_coef_upper=0.2, p=0.3),
    A.CoarseDropout(max_holes=8, max_height=40, max_width=40, p=0.3),
])


def process_single_image(
    args: tuple[str, int],
    transform: A.Compose = DEFAULT_AUGMENTATION_TRANSFORM,
) -> int:
    """Apply *transform* to one image and save *num_variants* augmented copies.

    Args:
        args: A ``(img_path, num_variants)`` tuple.
        transform: An ``albumentations.Compose`` transform to apply.

    Returns:
        Number of augmented images successfully saved.
    """
    img_path, num_variants = args
    try:
        image = cv2.imread(img_path)
        if image is None:
            return 0
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        root = os.path.dirname(img_path)
        name_part, ext_part = os.path.splitext(os.path.basename(img_path))

        count = 0
        for i in range(num_variants):
            augmented = transform(image=image)["image"]
            save_path = os.path.join(root, f"{name_part}_aug_{i}{ext_part}")
            if cv2.imwrite(save_path, cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR)):
                count += 1
        return count
    except Exception:
        return 0


def data_augmentation_parallel(
    src_dir: str | Path,
    num_variants: int = 1,
    max_workers: int = 4,
    transform: A.Compose = DEFAULT_AUGMENTATION_TRANSFORM,
) -> None:
    """Augment all original images in *src_dir* in parallel.

    Files whose names already contain ``_aug_`` are skipped so that running the
    function twice does not augment the augmented copies.

    Args:
        src_dir: Directory to scan recursively for original images.
        num_variants: Number of augmented copies to produce per original image.
        max_workers: Number of concurrent worker threads.
        transform: Albumentations transform to apply.
    """
    all_image_tasks: list[tuple[str, int]] = []
    original_counts = 0

    for root, _, files in os.walk(str(src_dir)):
        image_files = [
            os.path.join(root, f)
            for f in files
            if f.lower().endswith((".png", ".jpg", ".jpeg")) and "_aug_" not in f
        ]
        if image_files:
            original_counts += len(image_files)
            for path in image_files:
                all_image_tasks.append((path, num_variants))

    print(f"Data Augmentation processing: {original_counts} images...")

    def _worker(args: tuple[str, int]) -> int:
        return process_single_image(args, transform)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(
            tqdm(executor.map(_worker, all_image_tasks), total=len(all_image_tasks))
        )

    total_aug = sum(results)
    print(f"Original images: {original_counts}")
    print(f"Created variants: {total_aug}")
    print(f"Total images: {original_counts + total_aug}")
    print("Done Data Augmentation")


# ---------------------------------------------------------------------------
# Metadata generation for split datasets
# ---------------------------------------------------------------------------

def create_metadata(
    src_dir: str | Path,
    split_name: str,
    mapping_dict: dict[str, dict],
) -> pd.DataFrame:

    results: list[dict] = []
    global_landmark_info = []
    seen_landmark_ids = set()

    for landmark_id in os.listdir(str(src_dir)):
        root = os.path.join(str(src_dir), landmark_id)
        if not os.path.isdir(root):
            continue

        if landmark_id not in mapping_dict:
            continue

        info = mapping_dict[landmark_id]
        category = info["category"]
        landmark_name = extract_landmark_name(category)

        if landmark_id not in seen_landmark_ids:
            global_landmark_info.append({
                "landmark_id": landmark_id,
                "category": category,
                "landmark_name": landmark_name,
            })
            seen_landmark_ids.add(landmark_id)

        valid_exts = (".png", ".jpg", ".jpeg", ".webp")
        image_files = sorted(
            f for f in os.listdir(root) if f.lower().endswith(valid_exts)
        )

        for idx, filename in enumerate(image_files, start=1):
            new_id = f"{split_name}_{landmark_id}_{idx}"
            old_path = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1]
            temp_path = os.path.join(root, f"temp_{uuid.uuid4().hex}{extension}")
            new_path = os.path.join(root, f"{new_id}{extension}")

            try:
                os.rename(old_path, temp_path)
                os.rename(temp_path, new_path)
                results.append({
                    "id": new_id,
                    "split": split_name,
                    "landmark_id": landmark_id,
                    "landmark_name": landmark_name,
                    "new_path": new_path,
                })
            except Exception as e:
                print(f"Error {filename}: {e}")

    return pd.DataFrame(results), global_landmark_info