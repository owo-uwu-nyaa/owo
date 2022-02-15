import csv
import os
import re
from langdetect import detect
from aitextgen.tokenizers import train_tokenizer
from aitextgen import aitextgen

stripped_path = "stripped_msgs.txt"
msgs = []
with open('msgs.csv', 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            if row["author_id"] != "815239326811947038" and not row["msg"].startswith("!") and not row["msg"].startswith(
                    "$") and len(row['msg']) > 5 and detect(row['msg']) == 'en':
                msg = re.sub(r'<.*?>', '', row['msg'])
                msgs.append(f"{msg}")
        except:
            pass
with open(stripped_path, 'w', newline='') as smsgs:
    writer = csv.writer(smsgs)
    for msg in msgs:
        writer.writerow([msg])



train_tokenizer(stripped_path)
tokenizer_file = "aitextgen.tokenizer.json"

model_name = "355M"
model_name = "124M"
ai = aitextgen(tf_gpt2=model_name)

ai.train(stripped_path,
         model_name=model_name,
         only_train_transformer_layers=True,
         accumulate_gradients=1,
         batch_size=1,
         num_steps=50, generate_every=25,
         save_every=50
         )  # steps is max number of training steps
ai.generate()
