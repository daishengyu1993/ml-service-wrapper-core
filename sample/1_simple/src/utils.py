import pandas as pd
import re
import numpy as np
from gensim.models import FastText
from scipy.spatial.distance import cosine
from unidecode import unidecode
import string
import Constants
import pickle
from nltk import flatten


def replace_special_characters(text):
    '''
    Replace the semicolons or double pipe symbol to single pipe.
    
    Args:
        text (string): The first parameter.       

    Returns:
        text (string)   
    '''
    # checking null values for string.
    if str(text) !='nan' and text !='N/A' and text != None:
        # checking if string ends with semicolon or comma and removing it.
        if (text.strip()[-1] == ',' or text.strip()[-1] == ';'):
            text = text.strip()[0:-1]
        # checking for semicolons between text and replacing it with pipe symbol
        text = re.sub(r'[;；]','|',text)
        # checking for double pipe symbol seperated single space or multiple spaces and replacing it with single pipe symbol.
        text = re.sub(r'[|]\s+[|]|[|][|]','|', text)
        return text
    
def replace_punctuation(text):
    '''
    Remove special characters from string.
    
    Args:
        text (string): The first parameter.       

    Returns:
        text_val (string)   
    '''
    delimeter ='|'
    # empty list object
    address_list = list()
    # checking if delimeter present in string.
    if delimeter in text:
        # iterate through all addresses splitted through pipe.
        for each_address in text.split(delimeter):
            # removing the punctuation from the string.
            each_address_value = each_address.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
            # appending addresses to the empty list obejct 
            address_list.append(each_address_value)
        # joining multiple addresses with pipe and return it
        return delimeter.join(address_list)
    else:
        # removing the punctuation from the string, if no delimeter in string
        text_val = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    return text_val


def read_excel_file(path, sheet_name=None):
    
    '''
    Reading dataset file.
    
    Args:
        path (string): The first parameter.
        sheet_name (string): The second parameter.

    Returns:
        full_dataset_df (DataFrame)   
    '''    
    # read file based on worksheet
    full_dataset_df = pd.read_excel(path, sheet_name)    
    return full_dataset_df




def put_spaces_between_words(text):
    '''
    Put spaces between words and numbers, if not available and remove parentheses and inside text.
    
    Args:
        text (string): The first parameter.       

    Returns:
        text (string)   
    '''
    
    # checking null values for string.
    if str(text) !='nan' and text !='N/A' and text !=None:  
        # put spaces between small case and capital case
        #text = re.sub(r"\B([a-z])([A-Z])", r"\1 \2",text)    
        # put spaces between number and string 
        text = re.sub(r"(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])",r" ", text)
        # remove parentheses and text
        text = re.sub(r"\([^)]*\)",r"",text)
    
        return text

# Calculate JACCARD Similarity
def get_jaccard_sim(address1,address2):
    '''
    Calculate JACCARD similarity for address1 and address2.
    
    Args:
        address1 (string): The first parameter.
        address2 (string): The second parameter.

    Returns:
        similarity (float)
    '''
    # generate unique words from address1
    unique_word_address1 = set(address1.lower().split()) 
    # generate unique words from address2
    unique_word_address2 = set(address2.lower().split())  
    # generate intersect words between address1 and address2
    intersection = unique_word_address1.intersection(unique_word_address2)
    if len(intersection) == len(unique_word_address1) or len(intersection) == len(unique_word_address2):
        similarity = float(100)
        return similarity
    else:
        # generate union words between address1 and address2
        union = unique_word_address1.union(unique_word_address2)
        # calculate similarity score
        similarity = float(len(intersection)) / len(union) *100
        return similarity


def convert_non_ascii_to_ascii(text):
    '''
    Decode non-english character to english characters.
    
    Args:
        text (string): The first parameter.
        
    Returns:
        text (string)
    '''
    # checking null values for string.
    if str(text) !='nan' and text !='N/A' and text != None:
        return unidecode(text)

def replace_country_with_dict(text): 
    
    '''
    Replace country name with common_countries_dict dictionary.
    
    Args:
        text (string): The first parameter.
        
    Returns:
        text (string)
    '''
    delimeter='|'
    
    # empty list object 
    replace_text_list = list()
    # checking null values for string.
    if str(text) !='nan' and text !='N/A' and text !=None:        
        # checking if delimeter present in string.
        if delimeter in text: 
            # iterate through all addresses splitted through pipe.
            for each_address in text.split(delimeter):
                # replace country name with common_countries_dict dictionary and joing words with spaces
                replace_text = ','.join([common_countries_dict.get(word.lower().strip(),word.lower().strip()) for word in                                                        each_address.split(',')])
                
                # appending addresses to the empty list obejct 
                replace_text_list.append(replace_text) 
            return delimeter.join(replace_text_list)
        else:
            return ','.join([common_countries_dict.get(word.lower().strip(),word.lower().strip()) for word in text.split(',')])

def replace_short_abbr_with_dict(text): 
    '''
    Replace short form with short_abbrivation_dict dictionary in a text.
    
    Args:
        text (string): The first parameter.
        
    Returns:
        text (string)
    '''
    delimeter='|'
    # empty list object 
    replace_text_list=list()
    # checking null values for string.
    if str(text) !='nan' and text !='N/A' and text !=None:
        # checking if delimeter present in string.
        if delimeter in text:
            # iterate through all addresses splitted through pipe.
            for each_address in text.split(delimeter):
                 # replace short abbreviation with short_abbrivation_dict dictionary and joing words with spaces
                replace_text = ' '.join([short_abbrivation_dict.get(word,word) for word in each_address.split()])
                # appending addresses to the empty list obejct
                replace_text_list.append(replace_text)  
                
             # joining multiple addresses with pipe and return it
            return delimeter.join(replace_text_list)
        else:
            
            return ' '.join([short_abbrivation_dict.get(word,word) for word in text.split()])    
    


def remove_single_characters(texts):   
    '''
    Remove single and double characters and removes all extra spaces from string.
    
    Args:
        text (string): The first parameter.
        
    Returns:
        text (string)
    '''
    text_list = list()
    delimeter = '|'
    if str(texts) !='nan' and texts !='N/A' and texts !=None:
        if delimeter in texts:
            splitted_text = texts.split(delimeter)
            for txt in splitted_text:
                #remove single and double characters from text
                txt = re.sub(r'\b[^\d\W]{1,2}\b', ' ', txt)
                #remove extra spaces from starting of a text
                txt = re.sub(r'^\s+','',txt)
                #remove extra spaces between words
                txt = re.sub(r'\s+',' ',txt)
                text_list.append(txt)
        else:
            #remove single and double characters from text
            texts = re.sub(r'\b[^\d\W]{1,2}\b', ' ', texts)
            #remove extra spaces from starting of a text
            texts = re.sub(r'^\s+','',texts)
            #remove extra spaces between words
            texts = re.sub(r'\s+',' ',texts)
            text_list.append(texts)

        return delimeter.join(text_list)
    

def split_and_remove_comp_name(text):
    '''
    Remove first entry from a list after splitting it with comma.
    
    Args:
        text (string): The first parameter.
        
    Returns:
        data (string)
    '''
    
    # spitting text with comma and removing the first entry from list and letter joining it with spaces
    data = ' '.join(text.split(',')[1::])
    return data   


def fast_text_word_model(data,col_name):   
    '''
    Creating word vectors using fastText library.
    
    Args:
        data (DataFrame): The first parameter.
        col_name (string): The second parameter.
        
    Returns:
        model (word embedding model)
    '''
    sentences_list = list()
    delimeter = '|'
    
    for index,  row in data.iterrows():        
        if row[col_name] != None:
            # Creating a list of text
            sentences_list.extend(row[col_name].split(delimeter))
    strip_list = [item.strip() for item in sentences_list]
    # Removing duplicates entry from strip_list
    sentences = list(set(strip_list))
    # Creating FastText object
    model = FastText(size=100, window=10, min_count=1, workers=4,sg=1)
    # adding list of sentences to model
    model.build_vocab(sentences)
    total_words = model.corpus_total_words
    # Training the model to generate the vectors 
    model.train(sentences, total_words=total_words,epochs=100)
    return model


def Vectorizer(sentence,model):
    '''
    Convert word to a vectors and calculate the mean of the sentence vectors.
    
    Args:
        sentence (list): The first parameter.
        model (model): The second parameter.
        
    Returns:
        array
    '''
    
    vector = list()
    numw = 0
    for word in sentence.split():
        try:
            if numw==0:
                # Generate vectors for a word and store it to a list.
                vector = model[word]                
            else:
                # Generate vectors for a word and store it to a list.
                vector = np.add(vector, model[word])               
            numw +=1
        except:
            pass
    # return mean of the word vectors    
    return np.asarray(vector)/numw 

def get_cosine_similarity(address1,address2,model):
    
    '''
    Calculate cosine similarity for address1 and address2.
    
    Args:
        address1 (string): The first parameter.
        address2 (string): The second parameter.
        model (model): The third parameter

    Returns:
        similarity (float)
    '''
    
    similarity = (1- cosine(Vectorizer(address1.strip(), model),Vectorizer(address2,model))) * 100
    return similarity

def save_model(model,model_name):
    '''
    Save the model to the disk.
    
    Args:
        model (model): The first parameter.  
    '''
    #filename = Constants.fastText_model_name
    # save the model to disk
    pickle.dump(model, open(model_name, 'wb'))

def load_model_method(model_name):
    '''
    Load the saved model from disk.
    
    Returns:
        loaded_model (model)
    '''
    # load the model from disk
    loaded_model = pickle.load(open(model_name, 'rb'))
    return loaded_model


# new add


def zip_code_submethod(zip_code_regex, text): 
    '''
    Extract the address without zip code and the zip code from address list.
    Args:
        zip_code_regex (string): The first parameter.
        text (str): The second parameter.

    Returns:
        address_wo_zipcode (string) : address without zipcode
        postal_code_val (string) : zipcode    
    '''
    # get the zipcode pattern based on regex expression
    postal_code = re.findall(zip_code_regex,text)  
    
    if len(postal_code) !=0:     
        address_wo_zipcode = re.sub(postal_code[-1],'',text)
        postal_code_val = postal_code[-1]        
    elif len(postal_code) == 0:
        address_wo_zipcode = text
        postal_code_val = 'None'       
    else:     
        address_wo_zipcode = text
        
    return address_wo_zipcode, postal_code_val

def extract_zip_code(texts):
    '''
    Concat the address without zip code and the zip code from zip_code_submethod method.
    Args:
        texts (string): addresses with and without seprated by delimeter.       

    Returns:
        concat_address (string) : address concat with delimeter
        concat_postal_code (string) : concat list of zipcode    
    '''
    
    delimeter = '|'  
    address_list , postal_code_list = list(),list()
    
    if str(texts) !='nan' and texts !='N/A' and texts != None:       
        if delimeter in texts:
            for text in texts.split(delimeter):
                address_list_val,postal_code_val = zip_code_submethod(Constants.zip_code_regex,text)
                address_list.append(address_list_val)
                postal_code_list.append(postal_code_val)
        else:        
            postal_code = re.findall(Constants.zip_code_regex,texts)
            address_list_val,postal_code_val = zip_code_submethod(Constants.zip_code_regex,texts)
            address_list.append(address_list_val)
            postal_code_list.append(postal_code_val)
        
        concat_address = delimeter.join(address_list)    
        concat_postal_code = flatten(postal_code_list)
    
        return concat_address,concat_postal_code

def apply_and_concat(dataframe, field, func, column_names):
    '''
    Apply the function to a dataframe columns and append to the dataframe field.
    
    Args:
        dataframe (DataFrame): The first parameter.
        field (new column name) : The second parameter.
        func (method name) : The third parameter.
        column_names (columns name) : The fourth parameter

    Returns:
        dataframe (DataFrame)   
    '''
    return pd.concat((
        dataframe,
        dataframe[field].apply(
            lambda cell: pd.Series(func(cell), index=column_names))), axis=1)

def zip_code_extraction(dataframe):
    '''
    Method to extract zip code from address and append to a new columns.
    
    Args:
        dataframe (DataFarme): The first parameter.
        
    Returns:
        df_with_apm_zipcode (DataFrame)   
    '''
    
    df_with_pm_zipcode = apply_and_concat(dataframe, Constants.non_empty_pm_df, extract_zip_code, [Constants.pm_wo_zip_code, Constants.pm_zip_code])
    df_with_apm_zipcode = apply_and_concat(df_with_pm_zipcode, Constants.non_empty_license_pm_df, extract_zip_code, [Constants.license_pm_wo_zip_code, Constants.license_pm_zip_code])
    
    return df_with_apm_zipcode


def data_cleaning(dataframe):
    '''
    Method to clean dataset based on business needs.
    
    Args:
        dataframe (DataFarme): The first parameter.
        
    Returns:
        dataframe (DataFrame)   
    '''
    
    dataframe[Constants.cleaned_pm] = dataframe[Constants.pm_wo_zip_code].apply(lambda x : convert_non_ascii_to_ascii(x))
    dataframe[Constants.cleaned_pm] = dataframe[Constants.cleaned_pm].apply(lambda x:replace_country_with_dict(x))    
    dataframe[Constants.cleaned_pm] = dataframe[Constants.cleaned_pm].apply(lambda x:put_spaces_between_words(x))
    dataframe[Constants.cleaned_pm] = dataframe[Constants.cleaned_pm].apply(lambda text:replace_punctuation(text) if str(text) !='nan' and text !='N/A' and text !=None else text)
    dataframe[Constants.cleaned_pm] = dataframe[Constants.cleaned_pm].apply(lambda x:replace_short_abbr_with_dict(x))
    dataframe[Constants.cleaned_pm] = dataframe[Constants.cleaned_pm].apply(remove_single_characters)
    
    dataframe[Constants.cleaned_license_pm] = dataframe[Constants.license_pm_wo_zip_code].apply(convert_non_ascii_to_ascii)
    dataframe[Constants.cleaned_license_pm] = dataframe[Constants.cleaned_license_pm].apply(lambda x:replace_country_with_dict(x))
    dataframe[Constants.cleaned_license_pm] = dataframe[Constants.cleaned_license_pm].apply(lambda x:put_spaces_between_words(x))    
    dataframe[Constants.cleaned_license_pm] = dataframe[Constants.cleaned_license_pm].apply(lambda text:replace_punctuation(text) if str(text) !='nan' and text !='N/A' and text !=None else text)
    dataframe[Constants.cleaned_license_pm] = dataframe[Constants.cleaned_license_pm].apply(lambda x:replace_short_abbr_with_dict(x))
    dataframe[Constants.cleaned_license_pm] = dataframe[Constants.cleaned_license_pm].apply(remove_single_characters)       
    
    return dataframe

def handling_empty_cells(dataframe):
    '''
    Method to remove non text value from the dataset like N/A, INFORMATION NOT AVAILABLE etc.
    
    Args:
        dataframe (DataFarme): The first parameter.
        
    Returns:
        dataframe (DataFrame)   
    '''
    
    dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]] = dataframe[[Constants.physical_manufacture, Constants.license_pm]].replace(r'^\s+', '', regex=True)
    dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]] = dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]].replace(r'', 'N/A', regex=True)
    dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]] = dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]].replace(0, 'N/A', regex=True)
    dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]] = dataframe[[Constants.non_empty_pm_df,Constants.non_empty_license_pm_df]].replace('INFORMATION NOT AVAILABLE', 'N/A', regex=True)
    
    return dataframe

def distance_matrix(df,model, **kwds):
    '''
    Method to calculate similarity score using Jaccard Similarity or Cosine Similarity.
    
    Args:
        df (DataFarme): The first parameter.
        model (fastText word embedding model) : The second parameter.
        
    Returns:
        df (DataFrame)   
    '''
        
        
    delimeter = '|'
    final_distance_metric = list()
    assigned_physical_mf = list()
    max_similarity_score = list()
    max_similarity_index = list()
    max_similarity = list()
    
    for index, row in df.iterrows():        
        distance_metrics = list()     
        if str(row[Constants.cleaned_license_pm]) =='nan' or row[Constants.cleaned_license_pm] =='N/A' or row[Constants.cleaned_license_pm] == None :
                assigned_physical_mf.append(Constants.license_pm_error_message)
                final_distance_metric.append(Constants.no_value)
                max_similarity.append(Constants.no_value)
                max_similarity_index.append(Constants.no_value)                
               
        elif delimeter in row[Constants.cleaned_license_pm]:
            split_license_pm = row[Constants.cleaned_license_pm].split(delimeter)
            
            if str(row[Constants.cleaned_pm]) == 'nan' or row[Constants.cleaned_pm] =='N/A' or row[Constants.cleaned_pm] == None:
                assigned_physical_mf.append(Constants.pm_error_message)
                final_distance_metric.append(Constants.no_value)
                max_similarity.append(Constants.no_value) 
                max_similarity_index.append(Constants.no_value)              
                
            else:                
                for each_license_pm in split_license_pm: 
                     if bool(kwds):
                        for key, value in kwds.items():
                            if key =='model':                                
                                similarity = get_cosine_similarity(row[Constants.cleaned_pm],each_license_pm,value)                               
                                distance_metrics.append(round(similarity,2))                                
                     else:
                        similarity = get_jaccard_sim(row[Constants.cleaned_pm],each_license_pm)    
                        distance_metrics.append(round(similarity,2))              
               
                if np.max(distance_metrics,axis=0) <= Constants.jaccard_threshold:
                    distance_metrics = list()
                    for each_address in split_license_pm:                
                        if (each_address.strip() != ''):  
                            row[Constants.cleaned_pm] = convert_non_ascii_to_ascii(row[Constants.pm_wo_zip_code])
                            row[Constants.cleaned_pm] = split_and_remove_comp_name(row[Constants.cleaned_pm])
                            row[Constants.cleaned_pm] = replace_country_with_dict(row[Constants.cleaned_pm])                            
                            row[Constants.cleaned_pm] = put_spaces_between_words(row[Constants.cleaned_pm])
                            row[Constants.cleaned_pm] = replace_punctuation(row[Constants.cleaned_pm])                           
                            row[Constants.cleaned_pm] = replace_short_abbr_with_dict(row[Constants.cleaned_pm]) 
                            row[Constants.cleaned_pm] = remove_single_characters(row[Constants.cleaned_pm])                    
                            df.loc[index,Constants.cleaned_pm]=  row[Constants.cleaned_pm]  
                            if bool(kwds):
                                for key, value in kwds.items():
                                    if key =='model':
                                        similarity = get_cosine_similarity(row[Constants.cleaned_pm],each_address,value)
                                        distance_metrics.append(round(similarity,2))                                       
                            else:                                
                                similarity_jaccard = get_jaccard_sim(row[Constants.cleaned_pm],each_address)
                                
                                if similarity_jaccard >= float(Constants.cosine_threshold):
                                    similarity_cosine = get_cosine_similarity(row[Constants.cleaned_pm],each_address,model)                                    
                                else:
                                    similarity_cosine = round(0,2)                                    
                                distance_metrics.append(round(np.max([similarity_jaccard,similarity_cosine]),2))
                                
                final_distance_metric.append(distance_metrics)
                max_similarity.append(np.max(distance_metrics,axis=0))           

                max_similarity_index.append(np.argmax(distance_metrics,axis=0))

                if np.max(distance_metrics,axis=0) > Constants.acceptance_threshold:
                    assigned_physical_mf.append(row[Constants.non_empty_license_pm_df].split(delimeter)[np.argmax(distance_metrics,axis=0)].strip())
                   
                else:
                    assigned_physical_mf.append(Constants.error_message) 

        else:
            assigned_physical_mf.append(row[Constants.non_empty_license_pm_df])
            final_distance_metric.append(Constants.no_value)
            max_similarity.append(Constants.no_value)
            max_similarity_index.append(Constants.no_value)         
    
    df[Constants.pm_similarity_col] = final_distance_metric
    df[Constants.max_similarity_col] = max_similarity
    df[Constants.pm_expectation_col] = assigned_physical_mf
    df[Constants.max_similarity_index_col] = max_similarity_index    
   
    return df

short_abbrivation_dict = {'in':'indiana','ma':'massachusetts','inc':'','blvd':'boulevard','mn':'minnesota',
              'uk':'united kingdom','oh':'ohio','w':'west','rd':'road','tx':'texas','pr':'puerto rico','usa':'united states',                             'pkwy':'parkway','bfreiburg':'bei freiburg','llc' :'','dr':'drive','constelation':'constellation','hwy':'highway',
              'muracherstr':'muracherstrasse','karolingerstr':'karolingerstrasse','ca':'california','str':'strasse',
              'gaatonkibbutz':'gaaton kibbutz','mi':'michigan','salvacar':'salvarcar','mi48326':'michigan','taxas':'texas',
              'solothurnerstrasse':'solothurnstrasse','ltd':'','chihuiahua':'chihuahua','depuy':'','cmw':'','strrasse':'strasse','box':'',
              'cd':'cuidad','ias':'las'}

common_countries_dict = {'great britain':'united kingdom'} 
    