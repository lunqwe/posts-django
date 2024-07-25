from transformers import BertForSequenceClassification, BertTokenizer, TextClassificationPipeline

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained("JungleLee/bert-toxic-comment-classification")

pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)

def check_for_obscence(text:str) -> bool:
    is_toxic = pipeline(text)[0].get('label')
    if is_toxic == 'toxic':
        return False
    else:
        return True