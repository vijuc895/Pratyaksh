#import packages

from __future__ import print_function
from flask import Flask
import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import sys
from PIL import Image

import json

UPLOAD_FOLDER = "image/english/"

ALLOWED_EXTENSIONS = {'jpg', 'jpeg','png','JPG','JPEG','PNG'}

application = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# limit upload size upto 8mb
application.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#application = Flask(__name__)

import time
import cloudmersive_ocr_api_client
from cloudmersive_ocr_api_client.rest import ApiException
from pprint import pprint
import yake
import spacy
import pytextrank
from pymongo import MongoClient
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords 
from yandex.Translater import Translater
tr = Translater()
tr.set_key('trnsl.1.1.20200229T030530Z.d16dc45c4ba5761f.aebee0a45aab9956dae437936242065f92ab5b0b')

try: 
    conn = MongoClient() 
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 
  
# database 
db = conn.database 
collection=db.english_doc


collection.delete_many({})

# Configure API key authorization: Apikey
configuration = cloudmersive_ocr_api_client.Configuration()
configuration.api_key['Apikey'] = '0536347f-9018-4661-8bc9-87b7202b8515'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Apikey'] = 'Bearer'

def ocr(imagefile,lang):
# create an instance of the API class
    api_instance = cloudmersive_ocr_api_client.ImageOcrApi(cloudmersive_ocr_api_client.ApiClient(configuration))
    image_file = imagefile# file | Image file to perform OCR on.  Common file formats such as PNG, JPEG are supported.
    #language = '' # str | Optional, language of the input document, default is English (ENG).  Possible values are ENG (English), ARA (Arabic), ZHO (Chinese - Simplified), ZHO-HANT (Chinese - Traditional), ASM (Assamese), AFR (Afrikaans), AMH (Amharic), AZE (Azerbaijani), AZE-CYRL (Azerbaijani - Cyrillic), BEL (Belarusian), BEN (Bengali), BOD (Tibetan), BOS (Bosnian), BUL (Bulgarian), CAT (Catalan; Valencian), CEB (Cebuano), CES (Czech), CHR (Cherokee), CYM (Welsh), DAN (Danish), DEU (German), DZO (Dzongkha), ELL (Greek), ENM (Archaic/Middle English), EPO (Esperanto), EST (Estonian), EUS (Basque), FAS (Persian), FIN (Finnish), FRA (French), FRK (Frankish), FRM (Middle-French), GLE (Irish), GLG (Galician), GRC (Ancient Greek), HAT (Hatian), HEB (Hebrew), HIN (Hindi), HRV (Croatian), HUN (Hungarian), IKU (Inuktitut), IND (Indonesian), ISL (Icelandic), ITA (Italian), ITA-OLD (Old - Italian), JAV (Javanese), JPN (Japanese), KAN (Kannada), KAT (Georgian), KAT-OLD (Old-Georgian), KAZ (Kazakh), KHM (Central Khmer), KIR (Kirghiz), KOR (Korean), KUR (Kurdish), LAO (Lao), LAT (Latin), LAV (Latvian), LIT (Lithuanian), MAL (Malayalam), MAR (Marathi), MKD (Macedonian), MLT (Maltese), MSA (Malay), MYA (Burmese), NEP (Nepali), NLD (Dutch), NOR (Norwegian), ORI (Oriya), PAN (Panjabi), POL (Polish), POR (Portuguese), PUS (Pushto), RON (Romanian), RUS (Russian), SAN (Sanskrit), SIN (Sinhala), SLK (Slovak), SLV (Slovenian), SPA (Spanish), SPA-OLD (Old Spanish), SQI (Albanian), SRP (Serbian), SRP-LAT (Latin Serbian), SWA (Swahili), SWE (Swedish), SYR (Syriac), TAM (Tamil), TEL (Telugu), TGK (Tajik), TGL (Tagalog), THA (Thai), TIR (Tigrinya), TUR (Turkish), UIG (Uighur), UKR (Ukrainian), URD (Urdu), UZB (Uzbek), UZB-CYR (Cyrillic Uzbek), VIE (Vietnamese), YID (Yiddish) (optional)
    #preprocessing = 'preprocessing_example' # str | Optional, preprocessing mode, default is 'Auto'.  Possible values are None (no preprocessing of the image), and Auto (automatic image enhancement of the image before OCR is applied; this is recommended). (optional)

    try:
        # Convert a scanned image into words with location
        api_response = api_instance.image_ocr_photo_to_text(image_file,language=lang)
        text=api_response.text_result
        return text
    except ApiException as e:
        print("Exception when calling ImageOcrApi->image_ocr_image_lines_with_location: %s\n" % e)

def auto_tagging(text):
    import spacy
    import pytextrank

    # example text
    #text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types systems and systems of mixed types."
    # load a spaCy model, depending on language, scale, etc.
    nlp = spacy.load("en_core_web_sm")

    # add PyTextRank to the spaCy pipeline
    tr = pytextrank.TextRank()
    nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)


    doc = nlp(text)
    cnt=0
    # examine the top-ranked phrases in the document
    tags=[]
    for p in doc._.phrases:
        tags.append(p.text)
        cnt+=1
        if(cnt==4):
            break
    return tags 

@application.route("/",methods=['GET', 'POST'])
def home():
    return render_template('home1.html')
digi_doc =[]
summary=[]
tag=[]
@application.route("/upload",methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        lang = request.form["language"]
        print(lang)
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(application.config['UPLOAD_FOLDER'],filename))
            
	    
            path =(os.path.join(application.config['UPLOAD_FOLDER'],filename))
            print("path :",path)	   
	    
            rec={}
            if(lang=="hindi"):
                text=ocr(path,'HIN')
                tr.set_text(text)
                tr.set_from_lang('hi')
                tr.set_to_lang('en')

                text=tr.translate()

            else:
                text=ocr(path,'ENG')

            print(text)
            rec['text']=text.replace('\n',' ')
            #print(text)
            #print("**************************************************")

            tags=auto_tagging(text)
            #print("**************************************************")
            

            rec["summary"]=summarize(text).replace('\n',' ')
            #somedata.append(tags)
            
            #print("**************************************************")
            rec["tags"]=keywords(text).split('\n')
            #print("**************************************************")
            collection.insert_one(rec)
            print("******************************************************************************") 
            cursor = collection.find() 
            for record in cursor: 
                digi_doc.append(record['text'])
                summary.append(record['summary'])
                tag.append(record['tags'])
            print(tag)
            print("***************************************")          
    return render_template('index1.html',digi_response=digi_doc,summary_response=summary,tags_response=tag)

@application.route("/search",methods=['GET','POST'])
def search():
    tag_result=""
    if request.method == "POST":
        key = request.form["username"]
        for i in db.english_doc.find({"tags": key}):
            tag_result=i
    return render_template('search.html',response_text = tag_result) #["text"],response_summary=tag_result["summary"],response_tag=tag_result["tag"])


if __name__ == "__main__":
    application.debug=True
    application.run(host='0.0.0.0')



