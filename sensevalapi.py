from xml.etree import cElementTree as ElementTree

SENSEVAL3_TEST_DATA_FILE = "english-all-words.xml"
SENSEVAL3_TEST_ANSWERS_FILE = "EnglishAW.test.key"


def senseval_data():
    # TODO: Add part of speech of each word using WordNet

    all_sentences = []
    senseval_test = ElementTree.parse(SENSEVAL3_TEST_DATA_FILE)
    texts = senseval_test.getroot().findall("text")
    sentence = []
    sats = []
    test_words = {}
    test_phrases = []
    macro_sentence = []    # Macro variable are for sentences with subclauses in brackets, to process the clause in
    macro_test_words = {}  # the brackets without losing the continuity of the sentence outside the brackets
    macro_test_phrases = []
    for text in texts:
        elems = text.iter()
        for elem in elems:
            if elem.tag == "text":
                tail_words = elem.text.lower().split()
            elif elem.tag == "sat":
                sentence.append(elem.text.lower())
                tail_words = elem.tail.lower().split()
                sats.append(elem)
            elif elem.tag == "head":
                if "sats" in elem.attrib:
                    test_phrases.append({"headword": (elem.attrib["id"], elem.text.lower()), "sats": elem.attrib["sats"].split()})
                else:
                    test_words[elem.attrib["id"]] = elem.text.lower()
                sentence.append(elem.text.lower())
                tail_words = elem.tail.lower().split()
            else:
                raise ValueError("tag of unidentified kind: " + elem.tag)
            for tail_word in tail_words:
                # Ignore certain characters
                if not tail_word.isdigit() and tail_word[0] != "*" and tail_word != "," and tail_word != "&quot;":
                    # if sentence over, run sentence through Lesk
                    if tail_word == "." or tail_word == "!" or tail_word == "?" or \
                                    tail_word == "--" or tail_word == ":":
                        all_sentences.append({"sentence": sentence, "test_words": test_words, "test_phrases": test_phrases})
                        sentence = []
                        test_words = {}
                        test_phrases = []
                    # if left bracket
                    elif tail_word == "-LRB-":
                        macro_sentence = sentence
                        macro_test_words = test_words
                        macro_test_phrases = test_phrases
                        sentence = []
                        test_words = {}
                        test_phrases = []
                    # if right bracket
                    elif tail_word == "-RRB-":
                        all_sentences.append({"sentence": sentence, "test_words": test_words, "test_phrases": test_phrases})
                        sentence = macro_sentence
                        test_words = macro_test_words
                        test_phrases = macro_test_phrases
                        macro_sentence = []
                        macro_test_words = {}
                        macro_test_phrases = []
                    else:
                        sentence.append(tail_word.lower())
    if sentence or test_words:
        all_sentences.append({"sentence": sentence, "test_words": test_words, "test_phrases": test_phrases})
    return all_sentences


def senseval_answers():
    with open(SENSEVAL3_TEST_ANSWERS_FILE) as answer_file:
        answers = answer_file.read().split('\n')[:-1]
    answer_dicts = []
    total_answers = 0
    for answer in answers:
        answer = answer.split()
        answer_dicts.append({"id": answer[1], "lemmas": answer[2:]})
        if answer[2] != "U":  # catches the case where WordNet doesn't provide the proper sense.
            total_answers += 1
    return answer_dicts, total_answers