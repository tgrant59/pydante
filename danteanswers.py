from sys import stdout
from time import sleep
from danteapi import DanteAPI
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from nltk.stem.wordnet import WordNetLemmatizer


def get_dante_answers(senseval_data):
    # TODO: implement probability based inference of accuracy, i.e. POS adds prob, colloc adds prob, phrase adds prob
    #  - must find values for probs first. for colloc - adjacency affects it. for phrase - order affects it
    # Or, just test adjacency, presence of colloc and phrase words in the sentence (test both lemmatized and not)
    # Methods: Set arbitrary values and adjust manually
    #          Use a learning algorithm to find the best mix of values
    DanteAPI.initialize()
    dante = DanteAPI.get_all_word_meanings()
    print "\nDANTE parsing completed"
    dante_answers = {}
    lemmatizer = WordNetLemmatizer()
    for sentence_data in senseval_data:
        for phrase in sentence_data["test_phrases"]:
            word_id, raw_word = phrase["headword"]
            word = lemmatizer.lemmatize(raw_word)
            phrase_meaning = _answer_phrase(word, sentence_data, dante)
            if phrase_meaning is not None:
                dante_answers[word_id] = phrase_meaning
            else:
                dante_answers[word_id] = _answer_word(word, sentence_data, dante)

        for word_id, raw_word in sentence_data["test_words"].iteritems():
            word = lemmatizer.lemmatize(raw_word)
            dante_answers[word_id] = _answer_word(word, sentence_data, dante)
    return dante_answers


def _answer_phrase(word, sentence_data, dante):
    stdout.write(".")
    if word in dante:
        meanings = dante[word]
        for meaning in meanings:
            if "phrase_text" in meaning:
                if meaning["phrase_text"][0] in sentence_data["sentence"]:
                    if len(meaning["phrase_text"]) == 1:
                        meaning["found_by"] = "phrase"
                        return meaning
                    else:
                        phrase_complete = True
                        for phrase_word in meaning["phrase_text"]:
                            if phrase_word not in sentence_data["sentence"]:
                                phrase_complete = False
                                break
                        if phrase_complete:
                            meaning["found_by"] = "phrase"
                            return meaning

                        # uncomment below and comment above to make phrase selection dependent on word order
                        #---------------------------------------------------
                        # first_word_index = sentence_data["sentence"].index(meaning["phrase_text"][0])
                        # phrase_complete = True
                        # for j, phrase_word in enumerate(meaning["phrase_text"][1:]):
                        #     try:
                        #         if sentence_data["sentence"][first_word_index + 1 + j] != phrase_word:
                        #             phrase_complete = False
                        #             break
                        #     except IndexError:
                        #         phrase_complete = False
                        #         break
                        # if phrase_complete:
                        #     meaning["found_by"] = "phrase"
                        #     return meaning
    return None


def _answer_word(word, sentence_data, dante):
    stdout.write(".")
    if word in dante:
        meanings = dante[word]
        if len(meanings) == 1:
            meanings[0]["found_by"] = "only one meaning"
            return meanings[0]
        else:
            for meaning in meanings:
                if "phrase_text" not in meaning:
                    for colloc in meaning["collocations"]:
                        colloc_complete = True
                        for colloc_word in colloc:
                            if colloc_word not in sentence_data["sentence"]:
                                colloc_complete = False
                                break
                        if colloc_complete:
                            meaning["found_by"] = "collocation"
                            return meaning
    return None


def check_dante_answers(senseval_answers, dante_answers):
    for senseval_answer in senseval_answers:
        if senseval_answer["id"] not in dante_answers.answers:
            raise ValueError(str(senseval_answer) + " id not found in dante_answers")
        if dante_answers.answers[senseval_answer["id"]] is not None:
            for lemma in senseval_answer["lemmas"]:
                success = True
                if lemma not in DanteAPI.dante_answer_lookup or \
                        dante_answers.answers[senseval_answer["id"]]["meaning"] not in \
                        DanteAPI.dante_answer_lookup[lemma]:
                    success = create_lookup_entry(lemma, dante_answers.answers[senseval_answer["id"]],
                                                  senseval_answer["id"])
                if success:
                    if DanteAPI.dante_answer_lookup[lemma][dante_answers.answers[senseval_answer["id"]]["meaning"]]:
                        dante_answers.correct_answers += 1
                        dante_answers.correct_keys.append(senseval_answer["id"])
                        break
            dante_answers.total_answers += 1


def create_lookup_entry(lemma, dante_answer, answer_id):
    """
    Returns True if it failed
    """
    try:
        if lemma == "U":
            wn_definition = "NO DEFINITION FOUND - CHECK CONTEXT"
        else:
            wn_definition = wn.lemma_from_key(lemma).synset.definition
        write_string = str("For answer: " + answer_id + "\nAre these definitions of " + dante_answer["headword"] +
                           " the same?\n" + wn_definition + "\n          AND\n" + dante_answer["meaning"] + "\n")
        yes_or_no = None
        while yes_or_no != "y" and yes_or_no != "n":
            stdout.write("\r%s" % write_string)
            yes_or_no = raw_input("y or n?: ")
            stdout.flush()
            sleep(1)
        if yes_or_no == "y":
            DanteAPI.write_to_lookup(lemma, dante_answer["meaning"], True)
        elif yes_or_no == "n":
            DanteAPI.write_to_lookup(lemma, dante_answer["meaning"], False)
        else:
            raise ValueError("Wrong input squeezed through")
        stdout.write("\n")
        return True
    except WordNetError as err:
        synsets = wn.synsets(dante_answer["headword"])
        print "head word " + dante_answer["headword"] + " and lemma " + lemma + " caused error: " + err.message
        print "Synsets: " + str(synsets)
        print "FIX IT BEFORE NEXT RUN"
        return False