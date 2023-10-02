import pandas as pd
import nltk
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import cmudict

df1 = pd.read_excel('Output Data Structure.xlsx') #to get the columns for the values needed
df2 = pd.read_csv('articles.csv') #the scraped data
articles = pd.merge(df1, df2, on='URL_ID', how='left')

articles_df=articles.dropna(subset=['Title','Body']).reset_index(drop=True)
#the output data structures had 2 additional urls which were not in Input.xlsx, thus they have been removed. 
print('\nData Imported.\n')

def get_text(path,filename, delimiter = None):
    words_text = open(os.path.join(path,f'{filename}.txt'), "r")
 
    #read whole file to a string
    words = words_text.read()
 
    #close file
    words_text.close()
    words = words.replace('|','')
    words = words.lower()
 
    return list(set(words.split(delimiter)))

def clean_text():
        tokenized_text = word_tokenize(text)
        clean_text = []
        for word in tokenized_text:
            if word not in all_stop_words:
                clean_text.append(word)
        return clean_text

pronouncing_dict = cmudict.dict()

def count_syllables(word):
    # Check for exceptions: words ending with "es" or "ed"
    if word.endswith("es") or word.endswith("ed"):
        return 0
    
    # Use the CMU Pronouncing Dictionary to count syllables
    if word.lower() in pronouncing_dict:
        # The dictionary returns a list of possible pronunciations,
        # so we take the number of syllables in the first one.
        return max([len([ph for ph in pron if ph[-1].isdigit()]) for pron in pronouncing_dict[word.lower()]])
    else:
        # If the word is not found in the dictionary, use a simple heuristic
        # based on vowels to estimate syllables.
        vowels = "AEIOUaeiou"
        count = 0
        prev_char_is_vowel = False
        for char in word:
            if char in vowels:
                if not prev_char_is_vowel:
                    count += 1
                prev_char_is_vowel = True
            else:
                prev_char_is_vowel = False
        return count

def total_words(text):
    tokenized_text = word_tokenize(text)
    punc = list('!"#$%&()*+,-./:;<=>?@[\]^_`{|}~' + "'")
    # Subtract String Lists
    # using loop + remove()
    no_punc = [ ele for ele in tokenized_text ]
    for a in punc:
      if a in tokenized_text:
        no_punc.remove(a)
    return len(no_punc)

def pronouns(text):
    count = 0
    for word in text:
        if word == 'US':
            count += 0
        elif word.lower() == 'i' or word.lower() == 'we' or word.lower() == 'my' or word.lower() == 'ours' or word == 'us' or word == 'Us':
            count += 1
    return count

path = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'StopWords')

auditor = get_text(path, 'StopWords_Auditor')
currencies = get_text(path, 'StopWords_Currencies')
dates_numbers = get_text(path, 'StopWords_DatesandNumbers')
generic = get_text(path, 'StopWords_Generic')
generic_long = get_text(path, 'StopWords_GenericLong')
geographic = get_text(path, 'StopWords_Geographic')
names = get_text(path, 'StopWords_Names')
default = stopwords.words('english')
punc = list('!"#$%&()*+,-./:;<=>?@[\]^_`{|}~' + "'")

all_stop_words = list(set(auditor + currencies + dates_numbers + generic + generic_long + geographic + names + default + punc))

dictionary_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'MasterDictionary')

positive_words = get_text(dictionary_path,'positive-words')
negative_words = get_text(dictionary_path,'negative-words')

#Textual Analysis
print('Analysing... Please Wait.\n')
for index, text in enumerate(articles_df['Body']):
    positive_score = 0
    negative_score = 0
    complex_word_count = 0
    cleaned_text = clean_text()
    for word in cleaned_text:
        if word in positive_words:
            positive_score += 1
        elif word in negative_words:
            negative_score -= 1
    
    negative_score = abs(negative_score)
    polarity_score = (positive_score - negative_score)/ ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score)/ (len(cleaned_text) + 0.000001)
    word_count = len(cleaned_text)
    syllable_count_per_word = count_syllables(text)/word_count
    total_word_count = total_words(text)
    sentence_count = len(sent_tokenize(text))
    average_number_of_words_per_sentence = total_word_count/sentence_count
    no_spaces = text.replace(' ','')
    average_sentence_length = len(list(no_spaces))/sentence_count
    average_word_length = len(list(no_spaces))/total_word_count
    personal_pronouns = pronouns(text)
    
    for word in cleaned_text:
        if count_syllables(word)>2:
            complex_word_count += 1
    
    percent_complex = 100*((complex_word_count + 0.001)/total_word_count)
    fog_index = 0.4*((average_number_of_words_per_sentence)/percent_complex)
    
    articles_df.loc[index, 'POSITIVE SCORE'] = positive_score
    articles_df.loc[index, 'NEGATIVE SCORE'] = negative_score
    articles_df.loc[index, 'POLARITY SCORE'] = polarity_score
    articles_df.loc[index, 'SUBJECTIVITY SCORE'] = subjectivity_score
    articles_df.loc[index, 'AVG SENTENCE LENGTH'] = average_sentence_length
    articles_df.loc[index, 'PERCENTAGE OF COMPLEX WORDS'] = percent_complex
    articles_df.loc[index, 'FOG INDEX'] = fog_index
    articles_df.loc[index, 'AVG NUMBER OF WORDS PER SENTENCE'] = average_number_of_words_per_sentence
    articles_df.loc[index, 'COMPLEX WORD COUNT'] = complex_word_count
    articles_df.loc[index, 'WORD COUNT'] = word_count
    articles_df.loc[index, 'SYLLABLE PER WORD'] = syllable_count_per_word
    articles_df.loc[index, 'PERSONAL PRONOUNS'] = personal_pronouns
    articles_df.loc[index, 'AVG WORD LENGTH'] = average_word_length 
print('Analysis Complete.\n')
print('Exporting the articles to .txt files...\n')
#Exporting the .txt files containing the scraped articles
for index, text in enumerate(articles_df['Body']):
    title_text = articles_df['Title'][index]
    body_text = text
    file_name = articles_df['URL_ID'][index]
    directory = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'Scraped Articles', f'{file_name}.txt')
    
    text_file = open(directory, "w", encoding = 'utf-8')
    text_file.write(f'{title_text}\n\n{body_text}')
    text_file.close()
print('Export Complete.\n')
print('Exporting the articles to a .csv file...\n')
#Exporting the output to a .csv file
output = articles_df.drop(['Title', 'Body'], axis = 1)
output.to_csv('Output.csv', index = False)
print('Export Complete.\n')

