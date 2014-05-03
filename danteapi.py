import csv
from sys import stdout
from xml.etree import cElementTree as ElementTree

DANTE = "dante-v1.0.xml"       # Entire database
DANTE_ANSWER_LOOKUP_FILE = "dante-wordnet-lookup.csv"


class DanteAPI(object):
    corpus = None
    dante_answer_lookup = None

    @classmethod
    def initialize(cls):
        """
        Must be called before any other functions in DanteExtractor can function
        """
        try:
            with open(DANTE) as corpus_file:
                cls.corpus = list(ElementTree.parse(corpus_file).getroot())
        except IOError as err:
            err.message = "DANTE corpus not found"
            raise

        try:
            with open(DANTE_ANSWER_LOOKUP_FILE, "rU") as lookup_file:
                lookup_list = csv.reader(lookup_file)
                dante_answer_lookup = {}
                for lookup in lookup_list:
                    # dante_answer_lookup[wn_lemma_key][dante_meaning] = True/False
                    if lookup[2] == "True":
                        lookup_bool = True
                    elif lookup[2] == "False":
                        lookup_bool = False
                    else:
                        raise ValueError("3rd value in csv line should be Boolean: " + str(lookup))
                    try:
                        dante_answer_lookup[lookup[0]][lookup[1]] = lookup_bool
                    except KeyError:
                        dante_answer_lookup[lookup[0]] = {}
                        dante_answer_lookup[lookup[0]][lookup[1]] = lookup_bool
                cls.dante_answer_lookup = dante_answer_lookup
        except IOError:
            open(DANTE_ANSWER_LOOKUP_FILE, 'a').close()

    @classmethod
    def _extract_word(cls, word):
        """
        Takes a String word
        """
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        for corpus_word in cls.corpus:
            word_text = corpus_word.findtext(".//{urn:NEID}HWD")
            if word_text == word:
                return corpus_word
        raise ValueError("Word: '" + str(word) + "' not found in DANTE")
    
    @classmethod
    def _extract_batch_words(cls, words):
        """
        Takes a set of String words
        """
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        corpus_words = {}
        for corpus_word in cls.corpus:
            word_text = corpus_word.findtext(".//{urn:NEID}HWD")
            for word in words:
                if word_text == word:
                    corpus_words[word] = corpus_word
        if sorted(corpus_words.keys()) == sorted(words):  # Checks if the lists have all the same elements
            return corpus_words
        else:
            words_not_found = []
            for word in words:
                if word not in corpus_words:
                    words_not_found.append(word)
            raise ValueError("Word(s): " + str(words_not_found) + " not found in DANTE")
    
    @classmethod
    def _extract_all_words(cls):
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        corpus_dict = {}
        x_refs = []
        for corpus_word in cls.corpus:
            word_text = corpus_word.findtext(".//{urn:NEID}HWD")
            x_ref = corpus_word.findtext(".//{urn:NEID}XREF")
            # This filters out the real XREFs from the unnecessary ones
            if x_ref is not None and (corpus_word.find(".//{urn:NEID}MEANING") is None or
                                      corpus_word.find(".//{urn:NEID}EX") is None):
                x_refs.append((word_text.rstrip(), x_ref.rstrip()))
            else:
                corpus_dict[word_text.rstrip()] = corpus_word

        for original_word, x_ref_word in x_refs:
            try:
                corpus_dict[original_word] = corpus_dict[x_ref_word]
            except KeyError:
                print "orig word: " + original_word + "    x_ref word: " + x_ref_word
                raise
        return corpus_dict
    
    @classmethod
    def _extract_word_meanings(cls, head_word, elem):
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        meanings = elem.findall("*/{urn:NEID}SenseCont")
        word_meanings = []
        for meaning in meanings:
            meaning_dict = {}
            part_of_speech_elem = meaning.find(".//{urn:NEID}POS")
            part_of_speech = ""
            if part_of_speech_elem is not None:
                part_of_speech = part_of_speech_elem.get("code")
            meaning_text = meaning.findtext(".//{urn:NEID}MEANING")
            meaning_dict["headword"] = head_word
            meaning_dict["partOfSpeech"] = part_of_speech
            meaning_dict["meaning"] = meaning_text
            meaning_dict["collocations"] = []
            colloc_list = meaning.findall(".//{urn:NEID}COLLOC")
            for colloc in colloc_list:
                meaning_dict["collocations"].append(colloc.text.lower().split())
            word_meanings.append(meaning_dict)

        phrase_meanings = elem.find("*/{urn:NEID}MWEBlk")
        if phrase_meanings is not None:
            phrases = phrase_meanings.findall(".//{urn:NEID}PhrCont")
            if phrases is not None:
                for phrase in phrases:
                    try:
                        phrase_text = phrase.find(".//{urn:NEID}PHR").text.rstrip("!?.,:;").split()
                        if "sb" in phrase_text:
                            phrase_text.remove("sb")
                        if "one's" in phrase_text:
                            phrase_text.remove("one's")
                        if "sth" in phrase_text:
                            phrase_text.remove("sth")
                        if len(phrase_text) >= 1:
                            phrase_dict = {}
                            phrase_dict["headword"] = head_word
                            phrase_dict["phrase_text"] = phrase_text
                            phrase_dict["meaning"] = phrase.find(".//{urn:NEID}MEANING").text
                            word_meanings.append(phrase_dict)
                    except AttributeError:
                        continue
        return word_meanings
    
    @classmethod
    def get_word_meanings(cls, word):
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        return cls._extract_word_meanings(word, cls._extract_word(word))
    
    @classmethod
    def get_batch_word_meanings(cls, words):
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        words_elems = cls._extract_batch_words(words)
        words_meanings = {}
        for word, word_elem in words_elems.iteritems():
            meanings = cls._extract_word_meanings(word, word_elem)
            words_meanings[word] = meanings
        return words_meanings
    
    @classmethod
    def get_all_word_meanings(cls):
        if cls.corpus is None:
            raise RuntimeError("Every method in DanteExtractor can only be called after DanteExtractor.initialize()")
        words_elems = cls._extract_all_words()
        words_meanings = {}
        for word, word_elem in words_elems.iteritems():
            meanings = cls._extract_word_meanings(word, word_elem)
            words_meanings[word] = meanings
            stdout.write(".")
        return words_meanings

    @classmethod
    def write_to_lookup(cls, wn_lemma_key, dante_meaning, match):
        with open(DANTE_ANSWER_LOOKUP_FILE, "a") as lookup_file:
            writer = csv.writer(lookup_file, lineterminator='\n')
            writer.writerow([wn_lemma_key, dante_meaning, match])
            cls.dante_answer_lookup[wn_lemma_key] = {}
            cls.dante_answer_lookup[wn_lemma_key][dante_meaning] = match
