from quizzApp.utils.dependecies import *

model_name = 'tuner007/pegasus_paraphrase'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
if torch.cuda.is_available() :
    torch_device = 'cuda' 
    #model = torch.from_pretrained("quizzApp/utils/torch_model/pytorch_model.bin")
    
else : 
    torch_device = 'cpu'
    #model = PegasusTokenizer.from_pretrained("quizzApp/utils/torch_model/pytorch_model.bin")

model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)


def get_response(input_text,num_return_sequences):
    batch = tokenizer.prepare_seq2seq_batch([input_text],truncation=True,padding='longest', return_tensors="pt").to(torch_device)
    translated = model.generate(**batch,num_beams=10, num_return_sequences=num_return_sequences, temperature=1.5)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    return tgt_text

def mapSents(impWords,sents):
    processor=KeywordProcessor() #Using keyword processor as our processor for this task
    keySents={}
    for word in impWords:
        keySents[word]=[]
        processor.add_keyword(word) #Adds key word to the processor
    for sent in sents:
        found=processor.extract_keywords(sent) #Extract the keywords in the sentence
        for each in found:
            keySents[each].append(sent) #For each keyword found, map the sentence to the keyword
    for key in keySents.keys():
        temp=keySents[key]
        temp=sorted(temp,key=len,reverse=True) #Sort the sentences according to their decreasing length in order to ensure the quality of question for the MCQ 
        keySents[key]=temp
    return keySents

def getWordSense(sent, word):
    # Initialize a WordNetLemmatizer instance
    lem = WordNetLemmatizer()
    # Lemmatize the word to reduce its form to its base or dictionary form
    # 'n' specifies the part of speech tag as a noun
    word = lem.lemmatize(word, 'n')
    # Retrieve all synsets for the given word and part-of-speech
    synsets = wn.synsets(word, pos='n')
    # If no synsets are found, return None
    if len(synsets) > 0:
        # Compute the Wu-Palmer Similarity (WUP) between the word in the sentence and all the synsets
        wup = max_similarity(sent, word, 'wup', pos='n')
        # Compute the adapted Lesk score between the word in the sentence and all the synsets
        adapted_lesk_output = adapted_lesk(sent, word, pos='n')
        try:
            # Find the index of the synset with the lowest index from the two similarity scores
            lowest_index = min(synsets.index(wup), synsets.index(adapted_lesk_output))
            # Return the synset with the lowest index
            return synsets[lowest_index]
        except ValueError:
            # If the index is not found, return None
            return None
    else:
        # If no synsets are found, return None
        return None


def getDistractors(syn,word):
    dists=[]
    word=word.lower() 
    actword=word
    if len(word.split())>0: #If the word has multiple words, replace the spaces with underscores
        word.replace(" ","_")
    hypernym = syn.hypernyms() #Get the hypernyms of the input word
    if len(hypernym)==0: #If there are no hypernyms, return an empty list
        return dists
    for each in hypernym[0].hyponyms(): #For each hyponym of the hypernym,
        name=each.lemmas()[0].name() #get the name of the first lemma
        if(name==actword): #If the name is the same as the input word, continue to the next hyponym
            continue
        name=name.replace("_"," ") #Replace underscores with spaces
        name=" ".join(w.capitalize() for w in name.split()) #Capitalize the first letter of each word
        if name is not None and name not in dists: #If the name is not None and is not already in the list,
            dists.append(name) #add it to the list of distractors
    return dists #Return the list of distractors


def getDistractors2(word):
    word=word.lower()
    
    # Save original input word to compare later
    actword=word
    # Check if there are multiple words in the input and split them with underscores if true
    if len(word.split())>0: 
        word=word.replace(" ","_")
    # Create an empty list to hold the distractors
    dists=[]
    # Build the URL to retrieve distractors from ConceptNet's API and retrieve the results as a JSON object
    url= "http://api.conceptnet.io/query?node=/c/en/%s/n&rel=/r/PartOf&start=/c/en/%s&limit=5"%(word,word) 
    obj=requests.get(url).json()
    # Loop through each 'edge' object in the JSON object and retrieve the 'link' object associated with it
    for edge in obj['edges']:
        link=edge['end']['term']
        # Build a new URL using the 'link' object as the new 'node' parameter and retrieve the results as a JSON object
        url2="http://api.conceptnet.io/query?node=%s&rel=/r/PartOf&end=%s&limit=10"%(link,link)
        obj2=requests.get(url2).json()
        # Loop through each 'edge' object in the new JSON object and retrieve the 'word2' object associated with it
        for edge in obj2['edges']:
            word2=edge['start']['label'] 
            # Check if the 'word2' object is not already in the distractors list and is different from the original input word, then add it to the list
            if word2 not in dists and actword.lower() not in word2.lower():
                dists.append(word2)
    # Return the list of distractors
    return dists


def get_distractors(word, context, nlp):
    # Create a set of all words in the context
    context_words = set()
    for sent in context:
        for token in nlp(sent):
            context_words.add(token.text)

    # Get the most similar words from a larger vocabulary
    #Create a list of all vocabulary words that have a word vector, are in lower case,
    #and only contain alphabetic characters, and are not in the context words
    vocab_words = [w for w in nlp.vocab if w.has_vector and w.is_lower and w.is_alpha and w.text not in context_words]
    similar_words = [w.text for w in sorted(vocab_words, key=lambda w: w.similarity(nlp(word)), reverse=True)[:3]]
    #Sort the list of vocabulary words based on their similarity to the given word, in descending order
    #(most similar first) and select the top 3 most similar words
    return similar_words
    
def map_distractors(mapped_sents, nlp):
    mapped_dists = {}
    for word, context in mapped_sents.items():
      # Get the distractors for each word in the mapped sentences
        distractors = get_distractors(word, context, nlp)
        if distractors:
          # If distractors are found, add them to the mapped distractors dictionary
            mapped_dists[word] = distractors
    return mapped_dists


def is_valid_url(url):
    try:
        # Parse the URL using 'urlparse'
        result = urlparse(url)
        # Check if both the 'scheme' and 'netloc' attributes are present in the 'result' object
        return all([result.scheme, result.netloc])
    except:
        # If an exception occurs during parsing, return 0
        return 0
    
def translate_tamil_to_english(text):
    detected_language = translate(text[:500], 'en', 'ta')

    if detected_language != 'ta':
        return text

    translation = translate(text, 'en', 'ta')
    return translation

def translate_english_to_tamil(text):
    detected_language = translate(text[:500], 'ta', 'en')

    if detected_language != 'en':
        return text

    translation = translate(text, 'ta', 'en')
    return translation