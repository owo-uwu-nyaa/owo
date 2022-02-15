import csv

from aitextgen import aitextgen

ai = aitextgen(model_folder="trained_model")
ai.to_gpu()
#ai.generate_samples(repetition_penalty=5.0)
ai.generate_to_file(500, temperature=1.4, batch_size=20, repetition_penalty=5.0, num_beams=2)