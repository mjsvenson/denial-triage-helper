"""Find the payer policy snippets that best match a denial note, using TF-IDF keyword search."""

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

POLICIES_PATH = Path(__file__).parent / "data" / "payer_policies.json"
PAYERS = ["Copperleaf Health Plan", "Bramblecrest Insurance", "Quillfield Health"]

# How many candidate snippets to pass on. The next step decides which one, if any, applies,
# because keyword search cannot read negation or context (see README, retrieval first version).
TOP_K = 2

# Common words that carry no meaning for matching.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "is", "it",
    "no", "not", "of", "on", "or", "our", "that", "the", "this", "to", "was", "we", "with",
}
# The payer filter already uses the payer's name, so the name should not also count toward the score.
PAYER_WORDS = {word for payer in PAYERS for word in payer.lower().split()}


def tokenize(text):
    """Lowercase words, without stopwords, payer-name words, or numbers such as dates and claim IDs."""
    return [
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOPWORDS and word not in PAYER_WORDS and not word.isdigit()
    ]


def find_payer(note_text):
    """Return the one payer named in the note, or None if no payer or several payers are named."""
    named = [payer for payer in PAYERS if payer.split()[0].lower() in note_text.lower()]
    return named[0] if len(named) == 1 else None


def cosine(a, b):
    """Similarity of two weighted word lists, from 0 (nothing shared) to 1 (same mix of words)."""
    dot = sum(weight * b.get(word, 0.0) for word, weight in a.items())
    norms = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norms if norms else 0.0


class PolicyIndex:
    """TF-IDF vectors for every policy snippet, built once and reused for each search."""

    def __init__(self, policies):
        self.policies = policies
        counts = {p["id"]: Counter(tokenize(p["text"])) for p in policies}
        doc_freq = Counter(word for c in counts.values() for word in c)
        # Words in few snippets get high weight; a word in every snippet gets zero.
        self.idf = {word: math.log(len(policies) / df) for word, df in doc_freq.items()}
        self.vectors = {pid: self.weigh(c) for pid, c in counts.items()}

    def weigh(self, counts):
        """Turn word counts into TF-IDF weights. Words that no snippet contains get zero."""
        return {word: count * self.idf.get(word, 0.0) for word, count in counts.items()}

    def rank(self, note_text, payer=None):
        """Return (score, policy) pairs for the candidate policies, best first."""
        note_vector = self.weigh(Counter(tokenize(note_text)))
        candidates = [p for p in self.policies if payer is None or p["payer"] == payer]
        scored = [(cosine(note_vector, self.vectors[p["id"]]), p) for p in candidates]
        return sorted(scored, key=lambda pair: pair[0], reverse=True)


def load_index(path=POLICIES_PATH):
    return PolicyIndex(json.loads(Path(path).read_text(encoding="utf-8")))


def retrieve(index, note_text, payer, k=TOP_K):
    """Return up to k (score, policy) candidates from the payer's snippets, best first.

    The payer comes from the claim record rather than the note text, because many notes only give
    a claim number. Snippets that share no weighted words with the note are left out.
    """
    ranked = index.rank(note_text, payer)
    return [(score, policy) for score, policy in ranked if score > 0][:k]


def main():
    parser = argparse.ArgumentParser(description="Find the policy snippets that best match one denial note.")
    parser.add_argument("text", help="the denial note text, in quotes")
    parser.add_argument("--payer", choices=PAYERS, help="payer from the claim record (default: look for a payer name in the text)")
    parser.add_argument("--k", type=int, default=TOP_K, help=f"how many candidates to return (default: {TOP_K})")
    args = parser.parse_args()

    payer = args.payer or find_payer(args.text)
    candidates = retrieve(load_index(), args.text, payer, args.k)
    print(f"payer: {payer or 'unknown, so all payers were searched'}")
    if not candidates:
        print("no candidates: no snippet shares any weighted words with the note")
    for score, policy in candidates:
        print(f"\n{score:.3f}  {policy['id']}  {policy['topic']}\n  {policy['text']}")


if __name__ == "__main__":
    main()
