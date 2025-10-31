from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm
from src.tools.icd10_search import search_icd10_code

print("A carregar dataset...")
dataset = load_dataset("Gokul-waterlabs/ICD-10-CM", split="train")

NUM_SAMPLES = 200
dataset = dataset.select(range(NUM_SAMPLES))

y_true = []
y_pred = []

print(f"A iniciar avaliação com {NUM_SAMPLES} exemplos...\n")

for item in tqdm(dataset):
    symptoms = item["input"]
    expected_code = item["output"]

    try:
        result = search_icd10_code(symptoms)
        predicted_code = result["icd10_codes"][0]
    except Exception as e:
        print(f"Erro ao processar '{symptoms}': {e}")
        continue

    y_true.append(expected_code)
    y_pred.append(predicted_code)

correct = [1 if t == p else 0 for t, p in zip(y_true, y_pred)]

accuracy = accuracy_score(y_true, y_pred)
f1 = f1_score(correct, [1] * len(correct))

print("\nResultados da Avaliação:")
print(f"Accuracy: {accuracy:.3f}")
print(f"F1-score: {f1:.3f}")