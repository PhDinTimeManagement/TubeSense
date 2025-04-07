import nltk, csv, re
from nltk.corpus import stopwords
from nltk.probability import FreqDist

nltk.download('stopwords')


def processFile(file):
    comments = []
    with open('data/comments.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        
        for row in reader:
            trip = (row[0], row[1], row[2])
            comments.append(trip)
    return comments

def cleanComments(comments):
    seen = set()
    uniqueComments = [(x, y) for x, y in comments if x not in seen and not seen.add(x)]
    cleaned = []
    for comment in uniqueComments:
        regex = r"^[A-Za-z0-9.,;!?\'\"-_\s]+$"
        if re.match(comment[0], regex) :
            cleaned.append(comment)
    return cleaned

def tokenizeComments(comments):
    tokenizedComments = []
    for comment, likes, replies in comments:
        tokenizedComment = nltk.word_tokenize(comment)
        tokenizedComments.append((tokenizedComment, likes, replies))
    return tokenizedComments

def sanatizeComments(comments):
    
    
    sanatizedComments = []
    stopWords = set(stopwords.words('english'))
    regex = r"^[A-Za-z]+$"
    for comment, likes, replies in comments :
        sanatizedComment = []
        for word in comment :
            if re.match(word, regex) :
                if word.lower() not in stopWords :
                    sanatizedComment.append(word)
        sanatizedComments.append(sanatizedComment,likes, replies)
    return sanatizedComments

def transcriptProcessor(transcript, mode):
    
    cleanedTranscript = re.sub(r'\[[^\]]*\]', '', transcript)
    cleanedTranscript = re.sub(r'\s+', ' ', cleanedTranscript).strip()
    
    tokenizedTranscript = nltk.word_tokenize(cleanedTranscript)
    
    chunkedStrings = []
    
    if mode == 0 :
        chunkSize = 100
        chunks = [tokenizedTranscript[i:i + chunkSize] for i in range(0, len(tokenizedTranscript), chunkSize)]
        chunkedStrings = [' '.join(chunk) for chunk in chunks]
    elif mode == 1 :
        chunkSize = 3
        sentences = nltk.sent_tokenize(cleanedTranscript)
        chunks = [sentences[i:i + chunkSize] for i in range(0, len(sentences), chunkSize)]
        chunkedStrings = [' '.join(chunk) for chunk in chunks]
        
    return chunkedStrings
    
def wordScoring(comments, weightL, weightR):
    
    words = {}
    maxLikes = max(comments, key=lambda pair: pair[1])
    maxReplies = max(comments, key=lambda pair: pair[2])
    
    for comment, likes, replies in comments :
        for word in comment :
            score = weightL * likes/maxLikes + weightR * replies/maxReplies
            if word.lower() in words :
                words[word.lower()] += score
            else :
                words[word.lower()] = score
    return words
    
    


def main() :
   comments = processFile('temp')
   cleaned = cleanComments(comments)
   tokenized = tokenizeComments(cleaned)
   
   sentecneLengths = [len(pair[0]) for pair in tokenized]
   
   lenFreqDist = FreqDist(sentecneLengths)
   
   
   sanatized = sanatizeComments(tokenized)   
   
   
   