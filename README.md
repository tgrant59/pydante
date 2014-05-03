pydante
=======

**A knowledge-based word disambiguation algorithm that uses the Database of ANalyzed Texts of English (DANTE)**

###How to Install

 - Request access to DANTE from www.webdante.com
 - Put the xml database in the root directory and make sure it is named "dante-v1.0.xml"
 - Install the Natural Language Toolkit (NLTK): http://www.nltk.org/ OR pip install nltk
 - Install pywsd: https://github.com/alvations/pywsd
 - Put the pywsd folder in the root directory
 - (you may have to make some slight changes to pywsd to make it function in Python 2.7)

####In the interest of transparency

The lookup file for linking the DANTE answers with WordNet is dante-wordnet-lookup.csv
It can be deleted if you want to set the definitions yourself.

The answer key has been modified to work with WordNet 3.0 as integrated in the NLTK. The file is EnglishAW.test.key
