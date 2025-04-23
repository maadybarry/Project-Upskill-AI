from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
import spacy
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import pipeline

# Initialize FastAPI
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load NLP models (this will happen once when the app starts)
nlp = spacy.load("en_core_web_md")
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
en_stopwords = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """Basic text preprocessing"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized)

@app.get("/")
async def read_root(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_text(request: Request, text: str = Form(...)):
    """Analyze the submitted text"""
    # Preprocess the text
    processed_text = preprocess_text(text)
    
    # Perform NER with spaCy
    doc = nlp(processed_text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    # Get POS tags
    pos_tags = [{"text": token.text, "pos": token.pos_} for token in doc]
    
    # Get sentiment
    sentiment_result = sentiment_pipeline(processed_text)[0]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "original_text": text,
        "processed_text": processed_text,
        "entities": entities,
        "pos_tags": pos_tags,
        "sentiment": sentiment_result,
        "show_results": True
    })