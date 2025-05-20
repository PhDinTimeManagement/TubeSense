import random
import nltk
from nltk.corpus import brown, wordnet
from nltk import pos_tag, word_tokenize
from nltk import download


# Ensure you have downloaded the necessary corpora. If not, uncomment these lines:
# download('brown')
# download('punkt')
# download('averaged_perceptron_tagger')
# download('wordnet')

############################################################
# 1. Utility: Load Words from the Brown Corpus by POS Tag
############################################################

def load_brown_words_by_pos(pos_prefix, max_samples=2000):
    """
    Returns a list of unique words from the Brown corpus
    that match a certain part-of-speech prefix (e.g. 'NN' for nouns).
    We limit to `max_samples` for efficiency.
    """
    all_words = []
    # We'll read from a few categories for variety
    categories = brown.categories()
    for cat in categories:
        sents = brown.sents(categories=cat)
        for sent in sents:
            tagged = pos_tag(sent)
            for (word, pos) in tagged:
                # Filter out punctuation, short words, etc.
                word_clean = word.lower()
                if pos.startswith(pos_prefix) and word_clean.isalpha():
                    all_words.append(word_clean)

    # De-duplicate and limit size
    unique_words = list(set(all_words))
    random.shuffle(unique_words)
    return unique_words[:max_samples]


# Load various POS lists once
NOUNS = load_brown_words_by_pos('NN')
VERBS = load_brown_words_by_pos('VB')
ADJS = load_brown_words_by_pos('JJ')
ADVS = load_brown_words_by_pos('RB')

# Filler words to help link phrases
FILLERS = ["quite", "really", "somewhat", "definitely", "obviously", "truly"]


############################################################
# 2. Synonym Fetching from WordNet
############################################################

def get_wordnet_synonyms(word):
    """
    Return a list of synonyms (lemmas) from WordNet for the given word.
    We'll focus on the first sense for each synset to keep it simple.
    """
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            synonyms.add(lemma.name().replace("_", " ").lower())
    return list(synonyms)


############################################################
# 3. Grammar-Based Template Selection
############################################################

TEMPLATES = {
    "positive": [
        "I {adv} enjoy the {topic} because it helps me {verb} {rep_word} things!",
        "Honestly, the {topic} feels {adj} and I {adv} love its {rep_word} effect.",
        "The {topic} is {adj}, and I'm {adv} thrilled to see it {verb} {rep_word}."
    ],
    "neutral": [
        "The {topic} is {adj}, but it's neither good nor bad in terms of {rep_word}.",
        "It's {adv} true that the {topic} can {verb} {rep_word}, though I'm indifferent about it.",
        "I can't decide if the {topic} is {adj} or not, but it does {verb} {rep_word}."
    ],
    "negative": [
        "I really dislike how the {topic} seems {adj}, making {rep_word} quite difficult to {verb}.",
        "The {topic} is so {adj} that it fails to {verb} {rep_word} properly.",
        "Frankly, the {topic} is {adj}, and I hate dealing with {rep_word} in this situation."
    ]
}


def pick_template(tune):
    """
    Pick a random template string based on tune: 'positive', 'negative', or 'neutral'.
    """
    if tune not in TEMPLATES:
        tune = "neutral"  # fallback
    return random.choice(TEMPLATES[tune])


############################################################
# 4. Sentence Generation Core
############################################################

def generate_sentence(sentence_length, representative_word, topic_word, tune):
    """
    Generates a single sentence that tries to incorporate:
    - a single 'representative_word' (with optional synonyms),
    - a single 'topic_word',
    - a sentiment tune ('positive', 'neutral', or 'negative'),
    - approximate length in words (we'll pad or trim a bit),
    - grammar-based template from TEMPLATES,
    - random words from Brown corpus for variety.
    """

    # 4.1 Possibly fetch a synonym for the rep_word to create some variation
    rep_syns = get_wordnet_synonyms(representative_word)
    if rep_syns:
        # 50% chance to replace the original with a random synonym
        if random.random() < 0.5:
            representative_word = random.choice(rep_syns)

    # 4.2 Build the basic template
    template = pick_template(tune)

    # 4.3 Fill placeholders with random picks from our corpus
    adv_choice = random.choice(ADVS) if ADVS else "truly"
    adj_choice = random.choice(ADJS) if ADJS else "interesting"
    verb_choice = random.choice(VERBS) if VERBS else "handle"

    # Fill in
    sentence = template.format(
        adv=adv_choice,
        adj=adj_choice,
        verb=verb_choice,
        rep_word=representative_word,
        topic=topic_word
    )

    # 4.4 Adjust length (in a simplistic way)
    tokens = word_tokenize(sentence)
    current_length = len(tokens)

    # If it's shorter than desired length, we can insert some "filler" words or synonyms
    while current_length < sentence_length:
        insert_index = random.randint(1, len(tokens) - 2)
        filler = random.choice(FILLERS + [adj_choice, adv_choice])
        tokens.insert(insert_index, filler)
        current_length += 1

    # If it's longer, we can remove random tokens (avoid removing placeholders though)
    while current_length > sentence_length and current_length > 5:
        remove_index = random.randint(1, len(tokens) - 2)
        tokens.pop(remove_index)
        current_length -= 1

    # Rebuild final sentence
    final_sentence = " ".join(tokens)
    # Capitalize first letter, ensure it ends with a period (if it doesn't already).
    if not final_sentence.endswith((".", "!", "?")):
        final_sentence += "."

    return final_sentence


























































if __name__ == "__main__":
    # Example usage
    examples = [
        (15, "focus", "presentation", "positive")
    ]

    for (length, rep_word, topic_word, tune) in examples:
        sentence = generate_sentence(length,
                                     rep_word,
                                     topic_word, tune)
        print(f"\n--- Example (len={length}, tune='{tune}') ---")
        print(sentence)
