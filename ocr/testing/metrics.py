from rapidfuzz import fuzz
import matplotlib.pyplot as plt
import json

# ====================== OCR TEXT EXTRACTION ACCURACY ==========================
def evaluate_ocr_accuracy(
    ocr_result_dict: dict[str, list[str]], 
    ground_truth_dict: dict[str, list[str]]
) -> float:
    
    total_score = 0
    for img_id in ground_truth_dict:
        gt_text = " ".join(ground_truth_dict[img_id])
        pred_text = " ".join(ocr_result_dict.get(img_id, []))
        similarity_score = fuzz.partial_ratio(gt_text, pred_text)
        total_score += similarity_score
    return total_score / len(ground_truth_dict)

# ========================== SINGLE QUERY ACCURACY =============================
def build_phrase_to_images_dict(image_to_phrases_dict):
    phrase_to_images = {}

    for image_id, phrases in image_to_phrases_dict.items():
        for phrase in phrases:
            if phrase not in phrase_to_images:
                phrase_to_images[phrase] = set()
            phrase_to_images[phrase].add(image_id)

    # Convert sets to lists for easier downstream processing
    return {query: list(images) for query, images in phrase_to_images.items()}


def evaluate_single_query(gt_phrase_to_images, query, matched_paths):
    gt_paths = gt_phrase_to_images[query]

    tp = len(gt_paths & matched_paths)
    fp = len(matched_paths - gt_paths)
    fn = len(gt_paths - matched_paths)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    accuracy = tp / len(gt_paths) if gt_paths else 0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy
    }


def save_query_metrics_to_txt(metrics, query_name, runtime=None, filename="query_eval.txt"):
    """
    Usage:
    metrics = evaluate_single_query(gt_images, predicted_image_paths)
    save_query_metrics_to_txt(metrics, query_name="stephen olney")
    """
    with open(filename, "w") as f:
        f.write(f"Evaluation for Query: '{query_name}'\n")
        f.write(f"{'-'*40}\n")
        f.write(f"True Positives : {metrics['true_positives']}\n")
        f.write(f"False Positives: {metrics['false_positives']}\n")
        f.write(f"False Negatives: {metrics['false_negatives']}\n")
        f.write(f"Precision       : {metrics['precision']:.2f}\n")
        f.write(f"Recall          : {metrics['recall']:.2f}\n")
        f.write(f"Accuracy        : {metrics['accuracy']:.2f}\n")
        if runtime is not None:
            f.write(f"Runtime         : {runtime:.4f} seconds\n")


def plot_single_query_metrics(metrics, query_name="Query"):
    """
    plot_single_query_metrics(metrics, query_name="stephen olney")
    """
    keys = ["precision", "recall", "accuracy"]
    values = [metrics[k] for k in keys]

    plt.figure(figsize=(6, 4))
    plt.bar(keys, values)
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.title(f"Evaluation Metrics for '{query_name}'")
    plt.grid(True, axis='y')
    plt.show()


def main():
    # Evaluate OCR accuracy (against ground truth text database)
    with open("ocr_test_db_100.json", "rb") as f:
        ocr_result_dict = json.load(f)
    with open("gt_test_db.json", "rb") as f:
        gt_result_dict = json.load(f)
    accuracy = evaluate_ocr_accuracy(ocr_result_dict, gt_result_dict)
    print(accuracy)  # 56.02

    # Evaluate query accuracy
    gt_phrase_to_images = build_phrase_to_images_dict(gt_result_dict)
    evaluate_single_query(gt_phrase_to_images, "stephen olney", )


if __name__ == "__main__":
    main()