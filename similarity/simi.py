import textdistance
from difflib import SequenceMatcher  # 导入库


def ratio_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def levenshtein(a, b):
    return 1 - textdistance.levenshtein.distance(a.lower(), b.lower()) / max(len(a), len(b))
