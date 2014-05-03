from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError


with open("EnglishAW.test.key") as answer_file:
    answers = answer_file.read().split('\n')[:-1]
for answer in answers:
    answer = answer.split()
    word_id = answer[1]
    lemmas = answer[2:]
    for lemma in lemmas:
        try:
            if lemma != "U":
                synset = wn.lemma_from_key(lemma).synset
        except WordNetError:
            print("word id: {}      lemma: {}".format(word_id, lemma))