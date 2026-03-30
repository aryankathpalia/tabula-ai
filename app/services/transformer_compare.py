import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

MODEL_PATH = "aryankathpalia/tabula-legalbert-clause-classifier"


class LegalClauseClassifierCompare:

    def __init__(self):
        print("Loading LegalBERT (COMPARE)...")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )

        self.model.to(self.device)
        self.model.eval()

        self.labels = list(self.model.config.id2label.values())

        print("LegalBERT (COMPARE) loaded successfully.")

             
    # BATCH-FIRST PREDICT
             
    def predict(self, texts):

        # ALWAYS TREAT INPUT AS BATCH
        if isinstance(texts, str):
            texts = [texts]

        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = F.softmax(outputs.logits, dim=1)

        results = []

        for prob in probs:
            confidence, predicted_class = torch.max(prob, dim=0)

            results.append({
                "label": self.labels[predicted_class.item()],
                "confidence": float(confidence.item())
            })

        return results


         
# LAZY LOAD
         
_classifier = None


def get_compare_classifier():
    global _classifier

    if _classifier is None:
        _classifier = LegalClauseClassifierCompare()

    return _classifier