import re
import requests
import json
import nltk
from nltk.stem import WordNetLemmatizer
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
from nltk.corpus import wordnet as wn
from flashtext import KeywordProcessor
import heapq
import random
from sentence_splitter import SentenceSplitter, split_text_into_sentences
from heapq import nlargest
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from urllib.parse import urlparse
import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer