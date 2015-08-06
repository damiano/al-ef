from string import punctuation
import csv
import HTMLParser


def readStopwords(stopword_dir):
  stopwords_en_filename=stopword_dir+"/stopwords.en"
  stopwords_es_filename=stopword_dir+"/stopwords.es"
  stopwords = []
  with open(stopwords_en_filename) as f:
    lines = f.read().splitlines()
    stopwords.extend(lines)
  with open(stopwords_es_filename) as f:
    lines = f.read().splitlines()
    stopwords.extend(lines)
  return stopwords

def readFeatures(fname):
    id2features = {}
    with open(fname, 'rb') as f:
      reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_ALL)
      for l in reader:
        itemdic = {}
        label = None
        for item in l:
            if len(item)>0:
                try:
                    item = HTMLParser.HTMLParser().unescape(item)
                    key, value = item.rsplit(":",1)
                except ValueError:
                    sys.stderr.write("could not parse "+item+" in "+ fname + "\n>>"+l+"\n")
                if not key == "label":
                    if key == "author":
                        itemdic[key+"_"+value.rsplit(":",1)[0]] = float(value)
                    elif key == "id":
                        tweetid = long(value)
                    else:
                       try:
                         itemdic[key] = float(value)
                       except ValueError:
                         sys.stderr.write(key+" "+value)
                else:
                    label = value
                id2features[long(tweetid)] = (itemdic, label)
    return id2features

def readGoldstandard(fname, entity):
    id2label = {}
    with open(fname, 'rb') as f:
      reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_ALL)
      for l in reader:
          if len(l)==0: continue
          entityid,tweetid,label = l
          if (entityid == entity):
              id2label[long(tweetid)] = label
    return id2label

def readInTextFile(fname):
    id2tweet = {}
    with open(fname, 'rb') as f:
      reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_ALL)
      for l in reader:
        tweetid, author, entity, text = l
        if "tweet_id" in tweetid:
            continue
        id2tweet[long(tweetid)] = {"author":author, "entity":entity, "text":text}
    return id2tweet

def preprocess_tweets(id2tweet,stopwords):
    preprocessed = {}
    for tweetid, item in id2tweet.iteritems():
       author = item["author"]
       text = item["text"]
       label = "?"
       newtext = author +" "+text
       #lowercasing
       tweet_processed = newtext.lower()
       #remove punctuation
       for p in list(punctuation):
          tweet_processed=tweet_processed.replace(p,'')
       #tokenize
       words = tweet_processed.split(' ')
       #Add bigrams
#       bigrams = zip(words, words[1:])
#       bigrams = map(lambda (x,y): x+'_'+y,bigrams)
#       words.extend(bigrams)
       #remove repetitions
       def f(w) :  return re.sub(r'(.)\1+', r'\1\1', w)
       words = map(f, words)
       #remove stopwords
       words = filter(lambda w: w not in stopwords, words)
       words = filter(lambda w: len(w) > 2 and len(w) < 40, words)
       representation = { w: "1.0" for w in words }
       preprocessed[long(tweetid)] = (representation, label)
    return preprocessed
