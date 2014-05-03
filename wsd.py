import sensevalapi
import leskanswers
import danteanswers


class Answers(object):
    def __init__(self, answers, version):
        self.answers = answers
        self.version = version
        self.correct_answers = 0
        self.total_answers = 0
        self.precision = 0
        self.recall = 0
        self.correct_keys = []
        self.phrase_perc = 0  # last three attributes only applicable for dante answers
        self.colloc_perc = 0
        self.one_meaning_perc = 0

    def __str__(self):
        return "{} algorithm had precision of {}%, and recall of {}%".format(self.version, str(self.precision),
                                                                             str(self.recall))

    def set_precision_recall(self, total_senseval_answers):
        try:
            self.precision = (float(self.correct_answers) / self.total_answers) * 100
            self.recall = (float(self.total_answers) / total_senseval_answers) * 100
            if self.version == "dante":
                found_by_phrase = 0
                found_by_colloc = 0
                found_by_one_meaning = 0
                for word_id, answer in self.answers.iteritems():
                    if answer is not None:
                        if answer["found_by"] == "phrase":
                            found_by_phrase += 1
                        elif answer["found_by"] == "collocation":
                            found_by_colloc += 1
                        elif answer["found_by"] == "only one meaning":
                            found_by_one_meaning += 1
                self.phrase_perc = (float(found_by_phrase) / self.total_answers) * 100
                self.colloc_perc = (float(found_by_colloc) / self.total_answers) * 100
                self.one_meaning_perc = (float(found_by_one_meaning) / self.total_answers) * 100
        except ZeroDivisionError:
            raise ZeroDivisionError("total_answers is {} and total_senseval_answers is {}  in {}_answers".format(
                str(self.total_answers), str(total_senseval_answers), self.version))


def dante_override(dante_answers, lesk_answers, senseval_answers):
    dante_override_answers = Answers(None, "dante_overriding_" + lesk_answers.version)
    for answer in senseval_answers:
        word_id = answer["id"]
        if dante_answers.answers[word_id] is not None and lesk_answers.answers[word_id] is not None:
            if word_id in dante_answers.correct_keys:
                dante_override_answers.correct_answers += 1
            dante_override_answers.total_answers += 1
        elif dante_answers.answers[word_id] is not None:
            if word_id in dante_answers.correct_keys:
                dante_override_answers.correct_answers += 1
            dante_override_answers.total_answers += 1
        elif lesk_answers.answers[word_id] is not None:
            if word_id in lesk_answers.correct_keys:
                dante_override_answers.correct_answers += 1
            dante_override_answers.total_answers += 1
    return dante_override_answers


def run_experiment():
    senseval_data = sensevalapi.senseval_data()
    senseval_answers, total_senseval_answers = sensevalapi.senseval_answers()
    print "Senseval parsing completed"
    #-----------------------------------------
    dante_answers = Answers(danteanswers.get_dante_answers(senseval_data), "dante")
    danteanswers.check_dante_answers(senseval_answers, dante_answers)
    dante_answers.set_precision_recall(total_senseval_answers)
    print "\nDANTE answering and checking completed"
    #------------------------------------------
    lesk_tuples_list = leskanswers.get_lesk_answers(senseval_data)
    lesk_answers_list = []
    for lesk_tuple in lesk_tuples_list:
        lesk_answers_list.append(Answers(lesk_tuple[0], lesk_tuple[1]))
    leskanswers.check_lesk_answers(senseval_answers, lesk_answers_list)
    for lesk_answers in lesk_answers_list:
        lesk_answers.set_precision_recall(total_senseval_answers)
    print "\nLesk answering and checking completed"
    #-------------------------------------------
    dante_override_answers_list = []
    for lesk_answers in lesk_answers_list:
        dante_override_answers_list.append(dante_override(dante_answers, lesk_answers, senseval_answers))
    for override_answers in dante_override_answers_list:
        override_answers.set_precision_recall(total_senseval_answers)
    print "Done creating override answer lists"
    #-------------------------------------------
    print dante_answers
    print "dante found {}% of answers by phrase, {}% answers by colloc, and {}% answers because DANTE only included " \
          "one possible meaning".format(dante_answers.phrase_perc, dante_answers.colloc_perc,
                                        dante_answers.one_meaning_perc)
    for answers in lesk_answers_list + dante_override_answers_list:
        print answers


run_experiment()