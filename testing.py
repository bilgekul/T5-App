import numpy as np
import tensorflow as tf
from transformers import TFT5ForConditionalGeneration, T5Tokenizer
import evaluate
import json

# test verisini json file olarak al
with open('test.json',"r+", encoding='utf-8') as f:
    data = json.load(f)

    input_texts = []

    target_texts = []
    
    for i in data['test_data']:
        input_texts.append(i["input"])
        target_texts.append(i["output"])

# Tokenizer ve model yükleme
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = TFT5ForConditionalGeneration.from_pretrained("t5-small-turkish-english-translator")

# Giriş metinlerini tokenleştirme
inputs = tokenizer(input_texts, return_tensors="tf", padding=True, truncation=True)
input_ids = inputs["input_ids"]

# Model tahmini yapma
outputs = model.generate(input_ids)

# BLEU metriğini hesaplamak için evaluate kütüphanesini yükleme
test_metric = evaluate.load("sacrebleu")

# Test sınıfı ile metrik hesaplama
class Test:
    def __init__(self, predict, labels, tokenizer, metric):
        self.predict = predict
        self.labels = labels
        self.tokenizer = tokenizer
        self.metric = metric

    def postprocess_text(self, predicts, labels):
        preds = [pred.strip() for pred in predicts]
        labels = [label.strip() for label in labels]
        return preds, labels

    def sacre_Bleu(self):
        try:
            # predictions and labels decode etme
            decoded_predict = self.tokenizer.batch_decode(self.predict, skip_special_tokens=True)
            decoded_labels = self.tokenizer.batch_decode(self.labels, skip_special_tokens=True)

            # metni Post-process etme
            decoded_predict, decoded_labels = self.postprocess_text(decoded_predict, decoded_labels)

            # her cümle için BLEU skorunu hesap et 
            bleu_scores = []
            for pred, label in zip(decoded_predict, decoded_labels):
                result = self.metric.compute(predictions=[pred], references=[label])
                bleu_scores.append(result["score"])

            # ortalama tahmin uzunluğu
            prediction_lens = [len(pred.split()) for pred in decoded_predict]
            avg_gen_len = np.mean(prediction_lens)
            avg_bleu_scores = np.mean(bleu_scores)

            return {
                "bleu_scores": bleu_scores,
                "avg_gen_len": avg_gen_len,
                "avg_bleu_scores": avg_bleu_scores
            }

        except UnicodeError as e:
            return {"error": str(e)}

# Test sınıfını oluşturma ve metrik hesaplama
test = Test(
    predict=outputs,
    labels=tokenizer(target_texts, return_tensors="tf", padding=True, truncation=True)["input_ids"],  
    tokenizer=tokenizer,
    metric=test_metric
)

result = test.sacre_Bleu()
print("BLEU Scores for Each Sentence:", result["bleu_scores"])
print("Average BLEU Scores for Sum of Each Sentence:", result["avg_bleu_scores"])
print("Average Generation Length:", result["avg_gen_len"])


# sonuçları al ve json dosyasına çevir 
result = json.dumps(result, indent=2)

with open("scores.json", "w") as output:
    output.write(result)

        
        
