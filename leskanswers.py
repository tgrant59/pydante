import sys
import time
from pywsd import lesk
from nltk.stem.wordnet import WordNetLemmatizer


def get_lesk_answers(senseval_data):
    time_start = time.clock()

    # Getting answers from lesk algorithms
    original_lesk_answers = {}
    simple_lesk_answers = {}
    adapted_lesk_answers = {}
    for sentence_data in senseval_data:
        for phrase in sentence_data["test_phrases"]:
            word_id, word = phrase["headword"]
            original_lesk_answers[word_id] = lesk.original_lesk(" ".join(sentence_data["sentence"]), word)
            simple_lesk_answers[word_id] = lesk.simple_lesk(" ".join(sentence_data["sentence"]), word)
            adapted_lesk_answers[word_id] = lesk.adapted_lesk(" ".join(sentence_data["sentence"]), word)
        for word_id, word in sentence_data["test_words"].iteritems():
            original_lesk_answers[word_id] = lesk.original_lesk(" ".join(sentence_data["sentence"]), word)
            simple_lesk_answers[word_id] = lesk.simple_lesk(" ".join(sentence_data["sentence"]), word)
            adapted_lesk_answers[word_id] = lesk.adapted_lesk(" ".join(sentence_data["sentence"]), word)
        sys.stdout.write(".")
    lesk_answers_list = []
    lesk_answers_list.append((original_lesk_answers, "original lesk"))
    lesk_answers_list.append((simple_lesk_answers, "simple lesk"))
    lesk_answers_list.append((adapted_lesk_answers, "adapted lesk"))

    time_end = time.clock()
    print "\nlesk took " + str(time_end - time_start) + " seconds"
    return lesk_answers_list


def check_lesk_answers(senseval_answers, lesk_answers_list):
    for senseval_answer in senseval_answers:
        for lesk_answers in lesk_answers_list:
            if senseval_answer["id"] not in lesk_answers.answers:
                raise ValueError(str(senseval_answer) + " id not found in " + lesk_answers.version + "_answers")
            if lesk_answers.answers[senseval_answer["id"]] is not None:
                correct = False
                for lemma in lesk_answers.answers[senseval_answer["id"]].lemmas:
                    for acceptable_answer in senseval_answer["lemmas"]:
                        if lemma.key == acceptable_answer:
                            lesk_answers.correct_answers += 1
                            lesk_answers.correct_keys.append(senseval_answer["id"])
                            correct = True
                            break  # These two break statements are to ensure that no answer is counted as correct twice
                    if correct:
                        break
                lesk_answers.total_answers += 1
        sys.stdout.write(".")
