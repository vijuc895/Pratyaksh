from __future__ import print_function
import time
import cloudmersive_ocr_api_client
from cloudmersive_ocr_api_client.rest import ApiException
from pprint import pprint
import yake
import spacy
import pytextrank
from pymongo import MongoClient 
  
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
configuration.api_key['Apikey'] = '50b09c7f-bef2-47ef-82d2-8c932917ddc0'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Apikey'] = 'Bearer'

def ocr(imagefile):
# create an instance of the API class
    api_instance = cloudmersive_ocr_api_client.ImageOcrApi(cloudmersive_ocr_api_client.ApiClient(configuration))
    image_file = imagefile# file | Image file to perform OCR on.  Common file formats such as PNG, JPEG are supported.
    #language = '' # str | Optional, language of the input document, default is English (ENG).  Possible values are ENG (English), ARA (Arabic), ZHO (Chinese - Simplified), ZHO-HANT (Chinese - Traditional), ASM (Assamese), AFR (Afrikaans), AMH (Amharic), AZE (Azerbaijani), AZE-CYRL (Azerbaijani - Cyrillic), BEL (Belarusian), BEN (Bengali), BOD (Tibetan), BOS (Bosnian), BUL (Bulgarian), CAT (Catalan; Valencian), CEB (Cebuano), CES (Czech), CHR (Cherokee), CYM (Welsh), DAN (Danish), DEU (German), DZO (Dzongkha), ELL (Greek), ENM (Archaic/Middle English), EPO (Esperanto), EST (Estonian), EUS (Basque), FAS (Persian), FIN (Finnish), FRA (French), FRK (Frankish), FRM (Middle-French), GLE (Irish), GLG (Galician), GRC (Ancient Greek), HAT (Hatian), HEB (Hebrew), HIN (Hindi), HRV (Croatian), HUN (Hungarian), IKU (Inuktitut), IND (Indonesian), ISL (Icelandic), ITA (Italian), ITA-OLD (Old - Italian), JAV (Javanese), JPN (Japanese), KAN (Kannada), KAT (Georgian), KAT-OLD (Old-Georgian), KAZ (Kazakh), KHM (Central Khmer), KIR (Kirghiz), KOR (Korean), KUR (Kurdish), LAO (Lao), LAT (Latin), LAV (Latvian), LIT (Lithuanian), MAL (Malayalam), MAR (Marathi), MKD (Macedonian), MLT (Maltese), MSA (Malay), MYA (Burmese), NEP (Nepali), NLD (Dutch), NOR (Norwegian), ORI (Oriya), PAN (Panjabi), POL (Polish), POR (Portuguese), PUS (Pushto), RON (Romanian), RUS (Russian), SAN (Sanskrit), SIN (Sinhala), SLK (Slovak), SLV (Slovenian), SPA (Spanish), SPA-OLD (Old Spanish), SQI (Albanian), SRP (Serbian), SRP-LAT (Latin Serbian), SWA (Swahili), SWE (Swedish), SYR (Syriac), TAM (Tamil), TEL (Telugu), TGK (Tajik), TGL (Tagalog), THA (Thai), TIR (Tigrinya), TUR (Turkish), UIG (Uighur), UKR (Ukrainian), URD (Urdu), UZB (Uzbek), UZB-CYR (Cyrillic Uzbek), VIE (Vietnamese), YID (Yiddish) (optional)
    #preprocessing = 'preprocessing_example' # str | Optional, preprocessing mode, default is 'Auto'.  Possible values are None (no preprocessing of the image), and Auto (automatic image enhancement of the image before OCR is applied; this is recommended). (optional)

    try:
        # Convert a scanned image into words with location
        api_response = api_instance.image_ocr_photo_to_text(image_file,language='ENG')
        text=api_response.text_result
        return text
    except ApiException as e:
        print("Exception when calling ImageOcrApi->image_ocr_image_lines_with_location: %s\n" % e)
    

'''language = "en"
max_ngram_size = 3
deduplication_thresold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 20

custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
keywords = custom_kw_extractor.extract_keywords(text)

for kw in keywords:
    print(kw)
print("**************************************************")'''

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
data=[]
import glob
files=glob.glob("image/english/*.jpg")
#print(files)
for file in files:
    rec={}
    text=ocr(file)
    rec['text']=text.replace('\n',' ')
    #print(text)
    #print("**************************************************")

    tags=auto_tagging(text)
    #print("**************************************************")
    from gensim.summarization.summarizer import summarize
    from gensim.summarization import keywords

    rec["summary"]=summarize(text).replace('\n',' ')
    #somedata.append(tags)
    
    #print("**************************************************")
    rec["tags"]=keywords(text).split('\n')
    #print("**************************************************")
    collection.insert_one(rec)


def search(key):
     for i in db.english_doc.find({"tags": key}):
            print(i)  
search("drainage")
'''# Printing the data inserted 
cursor = collection.find() 
for record in cursor: 
    print(record) '''
