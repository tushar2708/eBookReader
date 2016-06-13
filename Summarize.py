# coding=UTF-8
from __future__ import division
import re
import sys
import difflib
import collections
# This is a naive text summarization algorithm
# Created by Shlomi Babluki
# April, 2013


class SummaryTool(object):

    # Naive method for splitting a text into sentences
    def split_content_to_sentences_on_newline(self, content):
        content = content.replace("\n", ". ")
        return content.split(". ")

    def split_content_to_sentences_on_fullspot(self, content):
        return content.split(".")

    def split_sentence_to_words(self, content):
        return content.split(" ")
        
    # Naive method for splitting a text into paragraphs
    def split_content_to_paragraphs(self, content):
        return content.split("\n\n")

    # Caculate the intersection between 2 sentences
    def sentences_intersection(self, sent1, sent2):

        # split the sentence into words/tokens
        s1 = set(sent1.split(" "))
        s2 = set(sent2.split(" "))

        # If there is not intersection, just return 0
        if (len(s1) + len(s2)) == 0:
            return 0

        # We normalize the result by the average number of words
        return len(s1.intersection(s2)) / ((len(s1) + len(s2)) / 2)

    # Caculate the intersection between 2 sentences
    def keyword_intersection(self, sent1, sent2):

        # split the sentence into words/tokens
        s1 = set(sent1.split(" "))
        s2 = set(sent2.split(" "))
        print
        # If there is not intersection, just return 0
        if (len(s1) + len(s2)) == 0:
            return 0
        list_new = []
        addition = []
        for item in s1:
            print "%s in s1" %item
            addition = difflib.get_close_matches(item, s2, 1, 0.5)
            list_new+= addition
            print "for %s is %s" % (item, (', ').join(addition))
        #list_new = [itm for itm in s1 if itm in s2]
        #print "intersection of %s AND %s is %s" % (sent1, sent2, ', '.join(list_new))
        return list_new

    # Format a sentence - remove all non-alphbetic chars from the sentence
    # We'll use the formatted sentence as a key in our sentences dictionary
    def format_sentence(self, sentence):
        sentence = re.sub(r'\W+', '', sentence)
        return sentence

    def format_sentence_chars(self, sentence):
        sentence = re.sub(r'\"', '', sentence)
        return sentence

    # Convert the content into a dictionary <K, V>
    # k = The formatted sentence
    # V = The rank of the sentence
    def get_senteces_ranks(self, content):

        # Split the content into sentences
        sentences = self.split_content_to_sentences_on_fullspot(content)

        # Calculate the intersection of every two sentences
        n = len(sentences)
        values = [[0 for x in xrange(n)] for x in xrange(n)]
        for i in range(0, n):
            for j in range(0, n):
                values[i][j] = self.sentences_intersection(sentences[i], sentences[j])

        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        sentences_dic = {}
        for i in range(0, n):
            score = 0
            for j in range(0, n):
                if i == j:
                    continue
                score += values[i][j]
            sentences_dic[self.format_sentence(sentences[i])] = score
        return sentences_dic

    def get_senteces_ranks_new(self, content):

        # Split the content into sentences
        sentences = self.split_content_to_sentences_on_fullspot(content)

        # Calculate the intersection of every two sentences
        n = len(sentences)
        values = [[0 for x in xrange(n)] for x in xrange(n)]
        for i in range(0, n):
            for j in range(0, n):
                values[i][j] = self.sentences_intersection(sentences[i], sentences[j])

        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        sentences_dic = {}
        sentences_list = []
        #index = 0
        for i in range(0, n):
            score = 0
            for j in range(0, n):
                if i == j:
                    continue
                score += values[i][j]
            sentences_dic[i] = score
            #sentences_list.append(self.format_sentence(sentences[i]))
        return sentences_dic

    # Return the best sentence in a paragraph
    def get_best_sentence(self, paragraph, sentences_dic):

        # Split the paragraph into sentences
        sentences = self.split_content_to_sentences_on_fullspot(paragraph)

        # Ignore short paragraphs
        if len(sentences) < 2:
            return ""

        # Get the best sentence according to the sentences dictionary
        best_sentence = ""
        max_value = 0
        for s in sentences:
            strip_s = self.format_sentence(s)
            if strip_s:
                if sentences_dic[strip_s] > max_value:
                    max_value = sentences_dic[strip_s]
                    best_sentence = s

        return best_sentence

    def get_new_summary(self, title, content,sentences_dic, summarypercent):
        # Add the title
        summary = []
        summary.append(title.strip())
        summary.append("")

        # Split the content into sentences
        sentences = self.split_content_to_sentences_on_fullspot(content)

        # Calculate the intersection of every two sentences
        n = len(sentences)

        #choose the top 20% with the highest score
        numOfSentencesToSummary = int(summarypercent * n/100);

        tuple_list = []
        #value_list = []
        order_dict = collections.OrderedDict(sorted(sentences_dic.items(), key=lambda t: t[1]))
        for i in range(0, numOfSentencesToSummary):
            key, value = order_dict.popitem()
            print "key : %s , value %s" %(key,value)
            tuple_list.append(key)
            #value_list.append(value)

        tuple_list.sort()

        for i in range(0, numOfSentencesToSummary):
            print "sentence is %s" %sentences[tuple_list[i]]
            summary.append(sentences[tuple_list[i]].strip('\n'))

        #sorted_dict = sorted(sentences_dic.values())
        #for i in range(0, numOfSentencesToSummary):
        #    sorted_dict[i]
        # Get the best sentence according to the sentences dictionary
        #best_sentence = ""
        # max_value = 0
        # for s in sentences:
        #     strip_s = self.format_sentence(s)
        #     if strip_s:
        #         if sentences_dic[strip_s] > max_value:
        #             max_value = sentences_dic[strip_s]
        #             best_sentence = s

        return ("").join(summary)


    # Build the summary
    def get_summary(self, title, content, sentences_dic):

        # Split the content into paragraphs
        paragraphs = self.split_content_to_paragraphs(content)

        # Add the title
        summary = []
        summary.append(title.strip())
        summary.append("")

        # Add the best sentence from each paragraph
        for p in paragraphs:
            sentence = self.get_best_sentence(p, sentences_dic).strip()
            #print "best sentence is %s " %sentence
            if sentence:
                summary.append(sentence)

        return (".").join(summary)

    # def get_keyword_list(self, summary):
    #     sentences = self.split_content_to_sentences_on_fullspot(summary)
    #     n = len(sentences)
    #     for sentence in sentences:
    #         print "Sentence is %s" %sentence
    #     print "number of sentences %s" % n
    #     keywords = []
    #     #keywords = [[0 for x in xrange(n)] for x in xrange(n)]
    #     for i in range(0, n):
    #         for j in range(i+1, n):
    #             keywords += self.keyword_intersection(sentences[i], sentences[j])
    #             #print "keyword[i][j] %s" % ' '.join([str(item) for sublist in keywords for item in sublist])
    #     return keywords

    def calculate_time_to_read(self, content):
        #Average duration (in milliseconds) lang:syllable/word/coma/sentence
        avg_time_syllable = 200
        avg_time_word = 10
        avg_time_sentence = 500
        numWords = 0		#Count the words.
        numSyllables = 0	#count the syllables
        numSentences = 0
        i = j = 0
        # Split the content into sentences
        sentences= self.split_content_to_sentences_on_fullspot(content)

        # Calculate the intersection of every two sentences
        numSentences = len(sentences)
        #print "numSentences %s" % numSentences
        for sentence in sentences:
            #print "Sentence is %s" %  sentence
            words = self.split_sentence_to_words(sentence)
            numWords += len(words);
            for word in words:
                for char in word:
                    if char in ['a', 'e', 'i', 'o', 'u', 'y']:
                        i = 1
                        if (i != j):
                            numSyllables += 1
                    else:
                        i = 0
                    j = i
        print "numWords %s" % numWords
        print "numSyllables %s" % numSyllables
        print "numSentences %s" %numSentences
        time_to_read =  (avg_time_syllable * numSyllables + avg_time_word * numWords + avg_time_sentence *  numSentences)/60000
        return time_to_read
		
# Main method, just run "python summary_tool.py"
def main(filepath, summarypercent):

    # Demo
    # Content from: "http://thenextweb.com/apps/2013/03/21/swayy-discover-curate-content/"

   # title = """
   # Swayy is a beautiful new dashboard for discovering and curating online content [Invites]
   # """

    file = open(filepath, 'r')
    content = file.read()

    title = ""
    # Create a SummaryTool object
    st = SummaryTool()

    #calculate time to read
    time = st.calculate_time_to_read(content)
	
    # Build the sentences dictionary
    sentences_dic = st.get_senteces_ranks_new(content)

    # Build the summary with the sentences dictionary
    summary = st.get_new_summary(title, content, sentences_dic,int(summarypercent))
    
    return (summary, time)

'''
    # Print the summary
    print "Summary is %s" %summary

    # Print the ratio between the summary length and the original length
    print ""
    print "Original Length %s" % (len(title) + len(content))
    print "Summary Length %s" % len(summary)
    print "Summary Ratio: %s" % (len(summary) / (len(title) + len(content)))
    print "Time to read: %s" % time

    #keywords = st.get_keyword_list(summary)
    #print "keywords %s" % ' '.join([str(item) for sublist in keywords for item in sublist])
'''

    

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])