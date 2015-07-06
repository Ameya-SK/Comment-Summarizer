##//////////////////////////////////////////////////////
##  Simple Summarizer
##//////////////////////////////////////////////////////
import nltk
from nltk import tokenize
from nltk import word_tokenize
from nltk import pos_tag
from nltk.util import *
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import nltk.data
import nltk
import re

class SimpleSummarizer:

	def reorder_sentences( self, output_sentences, inputContent ):
		output_sentences.sort( lambda s1, s2: inputContent.find(s1) - inputContent.find(s2) )
		return output_sentences
	
	def get_summarized(self, inputContent, num_sentences ):
	
		base_words = [word.lower()
			for word in nltk.word_tokenize(inputContent)]
		words = [word for word in base_words if word not in stopwords.words()]
		word_frequencies = FreqDist(words)
		
		most_frequent_words = [pair[0] for pair in
			word_frequencies.items()]
		
		
		sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
		actual_sentences = sent_detector.tokenize(inputContent)
		working_sentences = [sentence.lower()
			for sentence in actual_sentences]

		
		output_sentences = []

		for word in most_frequent_words:
			for i in range(0, len(working_sentences)):
				if (word in working_sentences[i]
				  and actual_sentences[i] not in output_sentences):
					output_sentences.append(actual_sentences[i])
					break
				if len(output_sentences) >= num_sentences: break
			if len(output_sentences) >= num_sentences: break
			
		
		return output_sentences
	def summarize(self, inputContent, num_sentences):return " ".join(self.get_summarized(inputContent, num_sentences))

class RatedWordgroup:

    def __init__(self,wordgroup,rating):
        self.wordgroup = wordgroup
        self.rating = rating

    def __str__(self):
        result = str(self.wordgroup) +" - " + str(self.rating)
        return result

    def __eq__(self,other):
        return self.wordgroup.eq(other.wordgroup) and self.rating.eq(other.rating)

    def __hash__(self):
        return hash(self.__str__())


class RatedSentence:

    def __init__(self,position,sentence,rating):
        self.position = position
        self.sentence = sentence
        self.rating = rating

    def __str__(self):
        result = "(" + str(self.position) +") (" + str(self.rating) +") " + self.sentence
        return result

    def __eq__(self,other):
        return self.position.eq(other.position) and self.sentence.eq(other.sentence) and self.rating.eq(other.rating)

    def __hash__(self):
        return hash(self.rating)

def get_word_bag(text) :

    text = text.lower()
    text = re.sub("[^a-ž]+", " ", text)
    text = re.sub("\n", " ", text)
    text = re.sub("[ ]+", " ", text)
    wordlist = text.split(" ")
    word_bag = list()
    for word in wordlist :
        word_bag.append(word.strip())
    #print("The text contains " + str(len(word_bag)) + " words.")
    return word_bag

def get_sentences(text,delimiter='.') :

    text = re.sub("\n", " ", text)
    text = re.sub("[ ]+", " ", text)
    sentences = text.split(delimiter)
    
    print("The text contains " + str(len(sentences)) + " sentences.")
    return sentences

def group_words(text) :

    word_bag = get_word_bag(text)

    cleanset = set() 
    used_words = set()
    word_groups = list()

    for word in word_bag : 
        cleanset.add(word.strip())

    for word in cleanset :
        if word not in used_words :
            wordfamily = list()
            wordfamily.append(word)
            if(len(word)>2) :
                used_words.add(word)
                for other in cleanset :
                    if other not in used_words :
                        same_chars = 0
                        (min_len,max_len) = (len(word),len(other)) if len(word) <= len(other) else (len(other),len(word))
                        for x in range(0,min_len) :
                            if word[x] == other[x] :
                                same_chars += 1
                            else :
                                break
                        if same_chars > 3 and (max_len - same_chars) < 7 :
                            wordfamily.append(other)
                            used_words.add(other)
            word_groups.append(wordfamily)
    print("The text contains " + str(len(word_groups)) + " word groups. (GW)")
    return word_groups

def get_wordlist_rate(text) :
    word_groups = group_words(text)
    word_bag = get_word_bag(text)
    rated_word_set = set()
    for group in word_groups :
        occur = 0
        for word in group :
            occur += word_bag.count(word)
        rated_word_set.add(RatedWordgroup(group,occur))
        #if(occur>5 and len(group[0]) > 4) :
        #    print(group)
        #    print(occur)
    #sort_wg = sorted(rated_word_set, key = lambda group : group.rating, reverse=True)
    #for rwg in sort_wg:
        #rwg = sort_wg[i]
    #    if rwg.rating > 4 and len(rwg.wordgroup[0]) > 4 and len(rwg.wordgroup) > 1:
    #        print(rwg)
    return rated_word_set

def rate_sentences(text,percentage,verbose=True) :
    result = str()
    sentences = get_sentences(text)
    wordlist = get_wordlist_rate(text)
    rated = list()
    topwords = list()
    sort_wg = sorted(wordlist, key = lambda group : group.rating, reverse=True)
    for rwg in sort_wg:
        if rwg.rating > 1 and len(rwg.wordgroup[0]) > 4 :
          #and len(rwg.wordgroup) > 1:
            weight = 1
            weight += rwg.rating/2
            weight += len(rwg.wordgroup[0])/2
            weight += len(rwg.wordgroup)/1
            for word in rwg.wordgroup :
                #topwords.add((word, weight))
                topwords.append((weight,word))
    if(verbose):
        for tw in sorted(topwords):
            print("(" + str(tw[0]) + ") - " + tw[1])
   #print(topwords)
    position = 0
    for sentence in sentences :
        rating = 0
        position += 1
        bag = get_word_bag(sentence)
        for word in bag :
            for record in topwords :
                 if word.lower()==record[1]:
                     rating += record[0]
        if(rating>0 and len(bag) > 0):
            rating = rating/((len(bag))/7)

        rated_sentence = RatedSentence(position, sentence, rating)

        rated.append(rated_sentence)

        #if rating > min_rating :
            #print(rating)
            #result += sentence + "."
            #print(str(position) + " " + sentence + ".")
            #print(rating)
    #for rs in rated:
    #    print(rs)

    sort_sentences = sorted(rated, key = lambda sen : sen.rating, reverse=True)

    for rs in sort_sentences:
        print(rs)

    num_of_sen = int(percentage)

    unsorted_result = list()

    counter = 0
    for rs in sort_sentences:
        if(counter>num_of_sen):
            break
        else:
            unsorted_result.append(rs)
            counter += 1

    sort_result = sorted(unsorted_result, key = lambda sen : sen.position, reverse=False)

    for rs in sort_result:
        result += rs.sentence + "."

    return result
	
def redundant(text1, text2):
    tag1 = nltk.pos_tag(text1)
    tag2 = nltk.pos_tag(text2)
    
    l1=len(tag1)
    l2=len(tag2)
    i=0
    count = 0
    while i < l1 :
        j = 0
        #print(tag1[i])
        s1 = tag1[i]
        #print(s1[1])
        while j < l2 :
            s2 = tag2[j]
            if str(s1[1]) == str(s2[1]) and str(s1[0]) == str(s2[0]) :
                #print(s1[0]+s1[1])
                count = count + 1                
            j = j + 1
        i = i + 1
    match = 2*count / (l1 + l2)
    match = match * 100
    #print(str(count))        
    #if count > 1 :
    #print("match percent ",match,"% ")
        #return 1
    #else:
    if match > 70:
        return 1
    else:
        return 0
        
filename = input("Enter file name: ")
f = open(filename)
f2 = open ("summary.txt",'w')
content = f.read()
ob = SimpleSummarizer()
sent = nltk.sent_tokenize(content)

length = len(sent)
if length > 100: length = 50
elif length > 50: length = 35
elif length > 35: length = 20
else : length = 15
print(length)
content = ob.summarize(content,length)

sent = nltk.sent_tokenize(content)
length = len(sent)
content = rate_sentences(content,length)
print(length)

sentence1 = nltk.sent_tokenize(content)
sentence2 = nltk.sent_tokenize(content)
length = len(sentence1)
print(length)
i=0
j=0
s1 = len(sentence1)
s2 = s1
while i < s1:
		j = i + 1
		while j < s2:
			text1  = nltk.word_tokenize(sentence1[i])       #breaking sentence into words
			text2  = nltk.word_tokenize(sentence2[j])
			res = redundant(text1,text2)                    #checking redundancy
			
			if res == 1:
				del sentence2[j]    #deleting redundant sentence
				j = j - 1           #index of all next sentences are decreased by 1
				s2 = s2 - 1         #so the size is decreased by 1
			j = j + 1
		i = i + 1
"""		
	print("Most commonly used words: ")
	word1 = word_freq.most_common(5)
	print(word1)
	 ___________________________________________ """


strsentence = " ".join(sentence2)
length = nltk.sent_tokenize(strsentence)
length = len(length)
print(length)
f2.write(strsentence)
f2.close()
f.close()
input("\n--End--")
	
