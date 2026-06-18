from __future__ import unicode_literals
from flask import Flask,render_template,url_for,request

from spacy_summarization import text_summarizer
# from gensim.summarization import summarize  # Deprecated in gensim 4.0+, using alternative
from nltk_summarization import nltk_summarizer

# Alternative to gensim.summarization.summarize
def gensim_summarize(text, ratio=0.2):
    """
    Simple text summarization function to replace gensim.summarization.summarize
    Uses a basic extractive summarization approach similar to gensim
    """
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        # Calculate number of sentences to extract (similar to ratio parameter)
        sentences = parser.document.sentences
        num_sentences = max(1, int(len(sentences) * ratio))
        summary = summarizer(parser.document, num_sentences)
        return ' '.join([str(sentence) for sentence in summary])
    except:
        # Fallback to simple extraction if sumy fails
        sentences = text.split('.')
        num_sentences = max(1, int(len(sentences) * ratio))
        return '. '.join(sentences[:num_sentences]) + '.'
import time
import spacy
nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)

# Web Scraping Pkg
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# Sumy Pkg
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# Sumy 
def sumy_summary(docx):
	parser = PlaintextParser.from_string(docx,Tokenizer("english"))
	lex_summarizer = LexRankSummarizer()
	summary = lex_summarizer(parser.document,3)
	summary_list = [str(sentence) for sentence in summary]
	result = ' '.join(summary_list)
	return result


# Reading Time
def readingTime(mytext):
	total_words = len([ token.text for token in nlp(mytext)])
	estimatedTime = total_words/200.0
	return estimatedTime

# Fetch Text From Url
def get_text(url):
	try:
		req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
		page = urlopen(req, timeout=10)
		soup = BeautifulSoup(page, 'html.parser')
		fetched_text = ' '.join(map(lambda p:p.text, soup.find_all('p'))).strip()
		return fetched_text
	except (URLError, HTTPError, ValueError):
		return ""

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/analyze',methods=['GET','POST'])
def analyze():
	start = time.time()
	if request.method == 'POST':
		rawtext = request.form['rawtext']
		final_reading_time = readingTime(rawtext)
		final_summary = text_summarizer(rawtext)
		summary_reading_time = readingTime(final_summary)
		end = time.time()
		final_time = end-start
	return render_template('index.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)

@app.route('/analyze_url',methods=['GET','POST'])
def analyze_url():
	start = time.time()
	rawtext = ""
	final_reading_time = 0
	final_summary = ""
	summary_reading_time = 0
	final_time = 0
	if request.method == 'POST':
		raw_url = request.form['raw_url']
		rawtext = get_text(raw_url)
		if rawtext:
			final_reading_time = readingTime(rawtext)
			final_summary = text_summarizer(rawtext)
			summary_reading_time = readingTime(final_summary)
		else:
			final_summary = "Unable to fetch text from the provided link. Please check the URL and try again."
		end = time.time()
		final_time = end-start
	return render_template('index.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)



@app.route('/compare_summary')
def compare_summary():
	return render_template('compare_summary.html')

@app.route('/comparer',methods=['GET','POST'])
def comparer():
	start = time.time()
	rawtext = ""
	final_reading_time = 0
	final_summary_spacy = ""
	summary_reading_time = 0
	final_summary_gensim = ""
	summary_reading_time_gensim = 0
	final_summary_nltk = ""
	summary_reading_time_nltk = 0
	final_summary_sumy = ""
	summary_reading_time_sumy = 0
	final_time = 0
	if request.method == 'POST':
		rawtext = request.form['rawtext']
		final_reading_time = readingTime(rawtext)
		try:
			final_summary_spacy = text_summarizer(rawtext)
		except Exception:
			final_summary_spacy = "SpaCy summarization failed for this input."
		summary_reading_time = readingTime(final_summary_spacy) if final_summary_spacy else 0
		# Gensim Summarizer (using alternative implementation)
		try:
			final_summary_gensim = gensim_summarize(rawtext)
		except Exception:
			final_summary_gensim = "Gensim-style summarization failed for this input."
		summary_reading_time_gensim = readingTime(final_summary_gensim) if final_summary_gensim else 0
		# NLTK
		try:
			final_summary_nltk = nltk_summarizer(rawtext)
		except Exception:
			final_summary_nltk = "NLTK summarization failed. Ensure required NLTK resources are installed."
		summary_reading_time_nltk = readingTime(final_summary_nltk) if final_summary_nltk else 0
		# Sumy
		try:
			final_summary_sumy = sumy_summary(rawtext)
		except Exception:
			final_summary_sumy = "Sumy summarization failed for this input."
		summary_reading_time_sumy = readingTime(final_summary_sumy) if final_summary_sumy else 0

		end = time.time()
		final_time = end-start
	return render_template('compare_summary.html',ctext=rawtext,final_summary_spacy=final_summary_spacy,final_summary_gensim=final_summary_gensim,final_summary_nltk=final_summary_nltk,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time,summary_reading_time_gensim=summary_reading_time_gensim,final_summary_sumy=final_summary_sumy,summary_reading_time_sumy=summary_reading_time_sumy,summary_reading_time_nltk=summary_reading_time_nltk)



@app.route('/about')
def about():
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)