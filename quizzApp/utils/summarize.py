from quizzApp.utils.dependecies import *
from quizzApp.utils.common_functions import *
from string import punctuation
punctuation = punctuation + '\n'

def generate_summary(text):
    text = translate_tamil_to_english(text)
    nlp = spacy.load("en_core_web_sm")
    stopwords = list(STOP_WORDS)
    doc = nlp(text)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]
    if len(sentence_tokens) < 5:
        select_length = 2
    elif len(sentence_tokens) < 7:
        select_length = 3
    elif len(sentence_tokens) < 10:
        select_length = 4
    elif len(sentence_tokens) < 15:
        select_length = 5
    elif len(sentence_tokens) < 30:
        select_length = 7
    elif len(sentence_tokens) < 50:
        select_length = 8
    elif len(sentence_tokens) < 100:
        select_length = 10
    else:
        select_length = int(len(sentence_tokens)*0.1)
    summary_ = nlargest(select_length, sentence_scores, key = sentence_scores.get)
    final_summary = [word.text for word in summary_]
    j = 0
    for i in final_summary:
        j = j + 1
        if i == sentence_tokens[0].text:
            del final_summary[j-1]
    summary = ' '.join(final_summary) 
    summary = sentence_tokens[0].text + ' ' + summary
    summary = translate_english_to_tamil(summary)
    return summary
