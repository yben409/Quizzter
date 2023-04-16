from quizzApp.utils.dependecies import *
from quizzApp.utils.common_functions import *
from string import punctuation
punctuation = punctuation + '\n'

def MCQ_output(text):
    text_min_length = 100
    if len(text)< text_min_length:
        return "Text too small to generate a MCQ quiz"
    
    text_is_tamil = False 
    if detect( text[:500] if len(text) > 500  else text)=='ta':
        text = translate_tamil_to_english(text)
        text_is_tamil = True 
    nlp = spacy.load("en_core_web_sm")
    stopwords = list(STOP_WORDS)
    doc = nlp(text)

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
    str_sentence_scores = {}
    for key in sentence_scores:
        new_key = str(key)
        str_sentence_scores[new_key] = sentence_scores[key]
    alpha_words = {word: freq for word, freq in word_frequencies.items() if word.isalpha()}
    top_words = random.sample(heapq.nlargest(10, alpha_words, key=alpha_words.get),10)
    str_sentences = []
    for i in range(len(sentence_tokens)):
        sente = str(sentence_tokens[i])
        str_sentences.append(sente)
    mappedSents=mapSents(top_words,str_sentences)
    mappedDists={}
    for each in mappedSents:
        if len(mappedSents[each]) != 0:
            wordsense=getWordSense(mappedSents[each][0],each) #gets the sense of the word
            if wordsense: #if the wordsense is not null/none
                dists=getDistractors(wordsense,each) #Gets the WordNet distractors
                if len(dists)==0: #If there are no WordNet distractors available for the current word
                    dists=getDistractors2(each) #The gets the distractors from the ConceptNet API
                if len(dists)!=0: #If there are indeed distractors from WordNet available, then maps them
                    # Get the top 3 distractors based on their similarity score
                    top_dists = heapq.nlargest(3, dists, key=lambda x: x[1])
                    mappedDists[each]=top_dists
            else: #If there is no wordsense, the directly searches/uses the ConceptNet
                dists=getDistractors2(each)
                if len(dists)>0: #If it gets the Distractors then maps them
                    # Get the top 3 distractors based on their similarity score
                    top_dists = heapq.nlargest(3, dists, key=lambda x: x[1])
                    mappedDists[each]=top_dists
    nlp_2 = spacy.load("en_core_web_lg")
    mappedDists = map_distractors(mappedSents, nlp_2)
    iterator = 1 #To keep the count of the questions
    i = 0
    sentences_fill_in = []
    unsuccessful_attempts = 0 #Counter for unsuccessful attempts
    max_questions = len(set(mappedSents.keys()).intersection(set(mappedDists.keys())))
    return_text = ""

    while i < max_questions and unsuccessful_attempts < 10*max_questions: #Exit loop after 10*num_questions unsuccessful attempts
        each = random.choice(list(mappedDists.keys()))
        if each in mappedSents and mappedSents[each]: # Check if there are any sentences available for the word
            sent = mappedSents[each][0]
            if sent not in sentences_fill_in:
                p = re.compile(each,re.IGNORECASE) #Converts into regular expression for pattern matching
                op = p.sub(" *****",sent) #Replaces the keyword with underscores(blanks)
                ##print("Question %s-> %s"%(iterator, op)) #Prints the question along with a question number
                return_text = return_text +  (("Question %s-> %s"%(iterator, op)) if text_is_tamil == False else translate_english_to_tamil("Question %s-> %s"%(iterator, op))) + "\n"
                options = [each.capitalize()]+random.sample(mappedDists[each], 3) #Capitalizes the options
                options = options[:4] #Selects only 4 options
                random.shuffle(options) #Shuffle the options so that order is not always same
                for i,ch in enumerate(options):
                    if ch.lower() == each.lower():
                        answer = ch
                        answer_index = i
                    ##print("\t%s: %s"%(chr(65+i), ch.capitalize())) #Print options
                    return_text = return_text +  (("\t%s: %s"%(chr(65+i), ch.capitalize())) if text_is_tamil == False else translate_english_to_tamil("\t%s: %s"%(chr(65+i), ch.capitalize())) )+ "\n"
                ##print()
                ##print("\tAnswer: %s\n"%(chr(65+answer_index) + ". " + answer.capitalize())) #Print the correct answer
                return_text = return_text +  (("\tAnswer: %s\n"%(chr(65+answer_index) + ". " + answer.capitalize())) if text_is_tamil == False else translate_english_to_tamil("\tAnswer: %s\n"%(chr(65+answer_index) + ". " + answer.capitalize()))) + "\n"
                iterator += 1 #Increase the counter
                sentences_fill_in.append(sent)
                i += 1
                unsuccessful_attempts = 0 #Reset unsuccessful_attempts counter
            else:
                unsuccessful_attempts += 1 #Increment unsuccessful_attempts counter
        else:
            unsuccessful_attempts += 1 #Increment unsuccessful_attempts counter if no sentences available for the word
    
    return return_text
