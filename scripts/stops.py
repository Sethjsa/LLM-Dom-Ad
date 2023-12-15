from string import punctuation, digits
from collections import Counter
import re

results = []

trash = punctuation + digits

with open("/home/saycock/scratch/data/CCAligned/CCAligned.en-lt.lt", "r") as f:
    lines = list(f.readlines())
    l = " ".join([l1.lower() for l1 in lines]).split()
    l = [x for x in l if x not in trash]
    p = r'[A-z]'
    l = [x for x in l if re.search(p, x)]
    c = Counter(l)
    results = c.most_common(200)

results = [i[0] for i in results]

print(results)