from transformers import BertForSequenceClassification, BertTokenizer, TextClassificationPipeline
""" 
This file is about using Hugging Face models to create required project functionality
https://huggingface.co/JungleLee/bert-toxic-comment-classification

"""

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained("JungleLee/bert-toxic-comment-classification")

pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)

def check_for_obscence(text: str) -> bool:
    
    
    is_toxic = pipeline(text)[0].get('label')
    return is_toxic != 'toxic'