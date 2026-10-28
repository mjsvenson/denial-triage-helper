"""Find the payer policy snippet that best matches a denial note, using TF-IDF keyword search."""

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

POLICIES_PATH = Path(__file__).parent / "data" / "payer_policies.json"
PAYERS = ["Copperleaf Health Plan", "Bramblecrest Insurance", "Quillfield Health"]

# Below this similarity, no policy is returned. Set before the held-out run, halfway between the
# lowest correct-match score (0.241) and the highest no-policy score (0.086) on the development notes.
MIN_SCORE = 0.16

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


def retrieve(index, note_text, min_score=MIN_SCORE):
    """Return (best policy or None, full ranking). None means no candidate reached min_score."""
    ranked = index.rank(note_text, find_payer(note_text))
    if ranked and ranked[0][0] >= min_score:
        return ranked[0][1], ranked
    return None, ranked


def main():
    parser = argparse.ArgumentParser(description="Find the policy snippet that best matches one denial note.")
    parser.add_argument("text", help="the denial note text, in quotes")
    parser.add_argument("--min-score", type=float, default=MIN_SCORE, help=f"minimum similarity (default: {MIN_SCORE})")
    args = parser.parse_args()

    index = load_index()
    payer = find_payer(args.text)
    policy, ranked = retrieve(index, args.text, args.min_score)
    print(f"payer filter: {payer or 'none (searched all payers)'}")
    for score, candidate in ranked[:3]:
        print(f"  {score:.3f}  {candidate['id']}  {candidate['payer']}, {candidate['topic']}")
    if policy:
        print(f"\nmatched {policy['id']}: {policy['text']}")
    else:
        print(f"\nno policy matched (best score below {args.min_score})")


if __name__ == "__main__":
    main()
