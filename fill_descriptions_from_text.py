# -*- coding: utf-8 -*-
import pandas as pd
import re

def extract_short_description(full_text, max_sentences=2):
    """Первые 2 предложения из текста"""
    if not full_text or pd.isna(full_text):
        return ''
    
    # Убираем HTML теги
    text = re.sub(r'<br\s*/?>', ' ', str(full_text))
    text = re.sub(r'<[^>]+>', '', text)
    
    # Разбиваем на предложения
    sentences = re.split(r'[.!?]\s+', text)
    
    # Берём первые max_sentences
    short = '. '.join(sentences[:max_sentences])
    
    if short and not short.endswith('.'):
        short += '.'
    
    return short[:300]  # Максимум 300 символов

def fill_descriptions(input_file='MASTER_CATALOG_RSS.csv', 
                      output_file='MASTER_CATALOG_WITH_DESCRIPTIONS.csv'):
    
    print('=' * 80)
    print('FILLING DESCRIPTIONS FROM TEXT')
    print('=' * 80)
    
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print("\nTotal offers: " + str(len(df)))
    
    # Счётчики
    filled = 0
    already_filled = 0
    no_text = 0
    
    for idx, row in df.iterrows():
        has_desc = not (pd.isna(row['Description']) or row['Description'] == '')
        has_text = not (pd.isna(row['Text']) or row['Text'] == '')
        
        if has_desc:
            already_filled += 1
            continue
        
        if not has_text:
            no_text += 1
            continue
        
        # Создаём Description из Text
        short_desc = extract_short_description(row['Text'])
        
        if short_desc:
            df.at[idx, 'Description'] = short_desc
            filled += 1
    
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print('\n' + '=' * 80)
    print('RESULTS')
    print('=' * 80)
    print("Total offers: " + str(len(df)))
    print("Already had Description: " + str(already_filled))
    print("Filled from Text: " + str(filled))
    print("No Text available: " + str(no_text))
    print("\nFile saved: " + output_file)
    print('=' * 80)

if __name__ == '__main__':
    fill_descriptions()
