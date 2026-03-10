'''
Docstring for 333_Final_Project.Python Scripts.K_Isolator
File Name: K_Isolator.py
Last Updated: 12/6/2025
Description: Goes through a textgrid, creating a new tier for isolated tokens based on preset criteria.
'''
import textgrid
import csv
from fileorganize import dir_to_df
import numpy as np
import pandas as pd
from pathlib import Path 
from pydub import AudioSegment
import platform
from tqdm import tqdm
import os

def getContainingWord(phone_interval, word_tier):
    """
    This function takes a particular phone from the textgrid package and a tier of words, 
    returning the index of the word interval containing the phone. 
    The function returns an integer index of the word containing the specified phone

    :phone_interval: is a praat interval taken from the textgrid package containing your phones.
    :word_tier: is a praat interval tier taken from the textgrid package containing your words.
    """
    s, e = phone_interval.minTime, phone_interval.maxTime
    for j, outer_int in enumerate(word_tier):
        if outer_int.minTime <= s and e <= outer_int.maxTime:
            return j
    return None

def getSpeechRate(tg_phones, tg_token):
    """
    Calculates the number of phones within 0.75s BEFORE the word starts
    and 0.75s AFTER the word ends, excluding the word's own duration.
    tg_phones is the input phone textgrid
    tg_token is the exact word that contains tg_phones
    """
    # Define the two exclusion windows
    pre_window_start = max(0, tg_token.minTime - 0.75)
    pre_window_end = tg_token.minTime
    
    post_window_start = tg_token.maxTime
    post_window_end = tg_token.maxTime + 0.75
    
    phone_count = 0
    silence_time = 0.0

    for p in tg_phones:
        # Use the midpoint to determine which window the phone belongs to
        mid = (p.minTime + p.maxTime) / 2
        
        # Check if the phone is in the Pre-buffer OR the Post-buffer
        is_in_pre = pre_window_start <= mid < pre_window_end
        is_in_post = post_window_start < mid <= post_window_end
        

        if is_in_pre or is_in_post:
            # Exclude silence/noise markers to get a true articulation rate
            if p.mark not in ['', 'spn', '{ls}', 'sil']:
                phone_count += 1
            else:
                # Determine which window we are in to find the overlap
                w_start = pre_window_start if is_in_pre else post_window_start
                w_end = pre_window_end if is_in_pre else post_window_end
                
                # Calculate the intersection of the phone and the window
                overlap_start = max(w_start, p.minTime)
                overlap_end = min(w_end, p.maxTime)
                overlap_duration = max(0, overlap_end - overlap_start)
                
                silence_time += overlap_duration

    # Calculate duration observed if at file edges, remove the time of silences like for example if its a phrase initial plosive
    actual_duration = ((pre_window_end - pre_window_start) + (post_window_end - post_window_start))-silence_time

    try: # For divide by zero errors (Trying to figureout why theyre happening)
        return phone_count / actual_duration
    except:
        return 0
    

def getIsolatedTokens(filepath, csvfilepath, tgout):
    '''
    Docstring for getIsolatedTokens
    
    :param filepath: Input Textgrid Filepath
    :param csvfilepath: Output CSV filepath
    :param tgout: Output textgrid filepath
    '''
    tg = textgrid.TextGrid.fromFile(filepath)
    tgPhones = tg[3]
    tgWords = tg[2]

    f = open(csvfilepath, 'w', newline = '')#Open csv file, create new if not available
    
    #Initialising variables
    vowels = 'ioaeuIOAEU'
    excludedTargets = ['i','o','a','e','u','I','O','A','E','U', 'spn', 'ng', 'n', 'm']
    kept_intervals = []
    targets = ['K', 'G', 'B', 'P', 'D', 'T', 'ʈ', 'k', 'g', 'b', 'p', 'd', 't']
    for n in range(len(tgPhones)):
        token = tgPhones[n].mark
        # Check if the token starts with any of our target characters
        # and ensure we aren't adding a duplicate
        if any(token.startswith(char) for char in targets) and (token not in targets):
            targets.append(token)
    print(token)
    target_counts = {target: 0 for target in targets}

    #input("Press Enter to continue to the next file...")

    fieldname = ['phone', 'minTime', 'maxTime', 'Preceding Token', 'Following Token', 'isWordInitial', 'Containing Word', 'Phones Per Second', 'Phone Index'] + targets
    dictWriter = csv.DictWriter(f, fieldnames=fieldname)
    dictWriter.writeheader()
    UID = 0

    for x in range(len(tgPhones)):
        currentMark = tgPhones[x].mark
        isWordInitial = False
        if currentMark in targets:
            word_index = getContainingWord(tgPhones[x], tgWords)
            #print(tgWords[word_index])
            #print('proper ' + tgPhones[x].mark + ' found')
            kept_intervals.append(textgrid.Interval(tgPhones[x].minTime, tgPhones[x].maxTime, tgPhones[x].mark)) # Add interval with intervocalic target
            if tgPhones[x].minTime == tgWords[word_index].minTime:
                isWordInitial = True
            
            # Check if x is the last index in the list or the first in the file
            following_token = str(tgPhones[x+1].mark) if (x + 1) < len(tgPhones) else "END_OF_FILE"
            preceding_token = str(tgPhones[x-1].mark) if x > 0 else "START_OF_FILE"

            speech_rate = getSpeechRate(tgPhones, tgPhones[x])

            dictWriter.writerow({
                'phone': str(tgPhones[x].mark), 
                'minTime': str(tgPhones[x].minTime), 
                'maxTime': str(tgPhones[x].maxTime),
                'Preceding Token' : preceding_token,
                'Following Token' : following_token,
                'isWordInitial' : str(isWordInitial),
                'Containing Word' : str(tg[2][word_index]),
                'Phones Per Second' : speech_rate,
                'Phone Index' : target_counts[currentMark]
            })
            target_counts[currentMark] += 1

    dictWriter.writerow(target_counts)

    new_tier = textgrid.IntervalTier(name='plosive isolation', minTime=tg[3].minTime, maxTime=tg[3].maxTime) # Create a new tier just for K
    for inter in kept_intervals: # Loop through adding the old set to this new tier
        new_tier.addInterval(inter)
    tg.append(new_tier)
    tg.write(tgout) # Write to a new file with updated output

    f.close()

#Original filepath, csv output, and new textgrid output
path_to_input = r"/home/seb/Documents/UBC/UBC Coding Environment/Projects/Suyuan MeLi VOT/Input/Actual Input/TextGrids"


tg_input_df = dir_to_df(path_to_input,
                    fnpat = ".TextGrid",
                    addcols = ["dirname", "barename", "ext"])
tg_input_df.head()

#tg_input_df["dirname"][0]
filepath = ""
csvfilepath = ""
tgout = ""
print(filepath)
print(csvfilepath)
print(tgout)


output_base = "/home/seb/Documents/UBC/UBC Coding Environment/Projects/Suyuan MeLi VOT/Output"

for n in tqdm(range(len(tg_input_df)), desc="Analyzing Tiers", leave=False):
    # Combines the directory path, the filename, and the extension dynamically
    filepath = os.path.join(tg_input_df["dirname"][n], tg_input_df["barename"][n] + tg_input_df["ext"][n])
    
    # Extract speaker and check language/type
    current_speaker = str(tg_input_df["barename"][n])[0:4]
    barename = tg_input_df["barename"][n]

    # Create speaker-specific output directory if it doesn't exist
    speaker_dir = os.path.join(output_base, current_speaker)
    os.makedirs(speaker_dir, exist_ok=True)

    speaker_language = ''
    speaker_language_dir = ''

    # Define output paths using f-strings 
    if "man" in barename:
        speaker_language_dir = os.path.join(speaker_dir, barename)
        os.makedirs(speaker_language_dir, exist_ok=True)
        csvfilepath = f"{speaker_dir}/{barename}/{barename}_isolated.csv"
        tgout = f"{speaker_dir}/{barename}/{barename}_isolated.Textgrid"
    elif "eng" in barename:
        speaker_language_dir = os.path.join(speaker_dir, barename)
        os.makedirs(speaker_language_dir, exist_ok=True)
        csvfilepath = f"{speaker_dir}/{barename}/{barename}_isolated.csv"
        tgout = f"{speaker_dir}/{barename}/{barename}_isolated.Textgrid"
    else:
        # Fallback in case the filename doesn't match "man" or "English"
        csvfilepath = f"{speaker_dir}/{barename}_misc.csv"
        tgout = f"{speaker_dir}/{barename}_misc.Textgrid"

    # Call function
    print(f"Processing: {barename}")
    getIsolatedTokens(filepath, csvfilepath, tgout)