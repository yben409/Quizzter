from quizzApp.utils.dependecies import *
from quizzApp.utils.common_functions import *
from string import punctuation
punctuation = punctuation + '\n'

def fill_in_blanks(text):
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
    str_sentence_scores = {}
    for key in sentence_scores:
        new_key = str(key)
        str_sentence_scores[new_key] = sentence_scores[key]
    alpha_words = {word: freq for word, freq in word_frequencies.items() if word.isalpha()}
    top_words = random.sample(heapq.nlargest(20, alpha_words, key=alpha_words.get),15)
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
    iterator = 1
    i = 0
    sentences_fill_in = []
    unsuccessful_attempts = 0
    max_questions = len(set(mappedSents.keys()).intersection(set(mappedDists.keys())))
    return_text =""
    while i < max_questions and unsuccessful_attempts < 10*max_questions:
        # Randomly choose a word from mappedDists
        each = random.choice(list(mappedDists.keys()))
        
        # Check if the chosen word is in mappedSents and has a sentence associated with it
        if each in mappedSents and mappedSents[each]:
            sent = mappedSents[each][0]
            
            # Check if the sentence has already been used for a fill-in-the-blank question
            if sent not in sentences_fill_in:
                
                # Replace the chosen word with a blank in the sentence
                p = re.compile(each,re.IGNORECASE)
                op = p.sub("________",sent)
                ##print("Question %s-> %s"%(iterator, op))
                return_text = return_text + "Question %s-> %s"%(iterator, op) + "\n"
                # Create a list of answer choices including the correct answer and three distractors
                options = [each.capitalize()]+random.sample(mappedDists[each], 3)
                options = options[:4]
                random.shuffle(options)
                
                # Find the index of the correct answer in the options list
                for i,ch in enumerate(options):
                    if ch.lower() == each.lower():
                        answer = ch.capitalize()
                
                # Display the answer choices and the correct answer
                 ##print()
                 ##print("\tAnswer: %s\n"%(answer))
                return_text = return_text + "\tAnswer: %s\n"%(answer) + "\n"
                iterator += 1
                sentences_fill_in.append(sent)
                i += 1
                unsuccessful_attempts = 0
            else:
                # If the sentence has already been used, increment the unsuccessful_attempts counter
                unsuccessful_attempts += 1
        else:
            # If the chosen word is not in mappedSents or does not have a sentence associated with it, increment the unsuccessful_attempts counter
            unsuccessful_attempts += 1
    return return_text 