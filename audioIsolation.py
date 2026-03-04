'''
Docstring for 333_Final_Project.Python Scripts.audio_token_isolation
File Name: audio_token_isolation.py
Last Changed: 26/11/2025
Description: Based on textgrid tiers isolates words carrying desired tokens and exports them 
-> as seperate audio files using pytorch
'''

import textgrid
import csv
from fileorganize import dir_to_df
import numpy as np
import pandas as pd
from pathlib import Path 
from pydub import AudioSegment
import platform
import os
from tqdm import tqdm

def getContainingWord(phone_interval, word_tier):
    """
    This function takes a particular phone from the textgrid package and a tier of words, 
    returning the index of the word interval containing the phone. 
    The function returns an integer index of the word containing the specified phone

    :phone_interval: is a praat interval tier taken from the textgrid package containing your phones.
    :word_tier: is a praat interval tier taken from the textgrid package containing your words.
    """
    s, e = phone_interval.minTime, phone_interval.maxTime
    floating_point_rounding = 0.001
    for j, outer_int in enumerate(word_tier):
        if (outer_int.minTime <= s + floating_point_rounding) and (e <= outer_int.maxTime + floating_point_rounding):
            return j
    return None

def splitAudio(audio_segment, minTime, maxTime, outputpath = None, makeMono = None, selectMonoChannel = None):
    """
    Function takes a segment of a larger audio file and extracts it, 
    returning an audio file unless output path is explicitly set

    :audio_segment: Accepts an AudioSegment object instead of a path to avoid repeated disk I/O.
    :minTime: specifies the start of the clip you want to extract in s.
    :maxTime: specifies the end of the clip you want to extract in s.
    :outputpath: optional argument that specifies where the output should be saved to.
    :makeMono: integer that decides whether or not the file should be exported as mono or stay as stereo, set to 1 if you want mono
    :selectMonoChannel: Decides the mono channel, 0 = left, 1 = right.
    """
    audio = audio_segment

    #convert time from s to ms
    minTime = minTime * 1000
    maxTime = maxTime * 1000

    # Safety checks
    if minTime < 0:
        raise ValueError("minTime cannot be negative.")
    if maxTime > len(audio):
        raise ValueError("maxTime exceeds audio length.")
    if minTime >= maxTime:
        raise ValueError("minTime must be less than maxTime.")
    
    if (maxTime) - (minTime-30) <= 128:
        extracted = audio[minTime-30:minTime+99] # Dr.VOT requires minimum length of 128ms
    else:
        extracted = audio[minTime-30:maxTime] # Chodroff and wilson 2017

    if makeMono == 1:
        extracted = extracted.split_to_mono()
    
    if outputpath:
        extracted = extracted[selectMonoChannel]
        extracted.export(outputpath, format=outputpath.split('.')[-1])
        return None

    return extracted

# --- Setup DataFrames ---
path_to_input_audio = Path(r'/home/seb/Documents/UBC/UBC Coding Environment/Projects/Suyuan MeLi VOT/Input/Actual Input/Audio/')
path_to_input_tg = Path(r'/home/seb/Documents/UBC/UBC Coding Environment/Projects/Suyuan MeLi VOT/Output/')
# Ensure fnpat matches your actual file extensions (Linux is case-sensitive!)
audio_input_df = dir_to_df(path_to_input_audio, fnpat=r".wav", addcols=["dirname", "barename", "ext"])
tg_input_df = dir_to_df(path_to_input_tg, fnpat=r".Textgrid", addcols=["dirname", "barename", "ext"])


audio_input_df.tail() # Get Dataframe of all files in directory
tg_input_df.head()
#eng_input_df.head()

#print(audio_input_df["barename"][5])

for n in tqdm(range(len(tg_input_df)), desc="Overall Progress"):
    tg_row = tg_input_df.iloc[n]
    #print(str(tg_row))
    barename = tg_row['barename']
    tgin = os.path.join(tg_row['dirname'], barename[0:4], barename[0:8], tg_row['fname'])
    audio_match = audio_input_df[audio_input_df['barename'] == barename[0:8]]

    if audio_match.empty:
        print(f"Skipping {barename}: No matching .wav found in subdirectories.")
        continue

   # input('wait to press enter')

    audio_row = audio_match.iloc[0]
    audioInputFile = os.path.join(audio_row['dirname'], audio_row['fname'])

    base_output = r'/home/seb/Documents/UBC/UBC Coding Environment/Projects/Suyuan MeLi VOT/Output'
    speaker_id_folder = f"{barename[0:4]}/{barename[0:4]}_audio" 
    speaker_audio_dir = os.path.join(base_output, speaker_id_folder, barename)
    #os.makedirs(speaker_audio_dir, exist_ok=True)

    try:
        tg = textgrid.TextGrid.fromFile(tgin)
        audiofile = AudioSegment.from_file(audioInputFile)
    except Exception as e:
        print(f"Error loading files for {barename}: {e}")
        continue

    audio_clip_file = speaker_audio_dir # I can't be assed to fix this code atm
    
    print('importing audio from ' + audioInputFile)
                                                                    
    #tgin = f'{tg_input_df['dirname'][n]}/{tg_input_df['fname'][n]}'
    print('importing tg from ' + tgin)
    
    tg = textgrid.TextGrid.fromFile(tgin)
    tgIsolatedPhones = tg[4]
    tgWords = tg[2]
    #print(tgIsolatedPhones)

    targets = ['K','G','B','P','T','D', 'k', 'g', 'b', 'd', 'p', 't', 'ʈ']
    for tok in range(len(tgIsolatedPhones)):
        token = tgIsolatedPhones[tok].mark
        # Check if the token starts with any of our target characters
        # and ensure we aren't adding a duplicate
        if any(token.startswith(char) for char in targets) and (token not in targets):
            targets.append(token)
    #print(targets)
    #input('press enter')
    target_counts = {target: 0 for target in targets} # Used for a clip counter for each token type

    

    audiofile = AudioSegment.from_file(audioInputFile) #IMPORT ONCE TO SAVE PROCESSING TIME

    is_mandarin = "_man" in barename
    is_english = "_eng" in barename
    speaker_id = barename[0:4]

    suffix = "M" if is_mandarin else "E"
    outputpath = os.path.join(base_output, speaker_id, f"{speaker_id}_audio", f"{speaker_id}_clips_{suffix}")

    #os.makedirs(outputpath, exist_ok=True)
    #print('starting loop')
    #print(tgin)
    for x in tqdm(range(len(tg[4])), desc=f"Extracting Clips", leave=False):
        #print('entering loop')
        current_token = tgIsolatedPhones[x].mark
        #print(current_token)
        #print(targets)
        if current_token in targets:
            idx = getContainingWord(tgIsolatedPhones[x], tgWords)
            
            if idx is not None:
                # Construct the filename using the confirmed suffix
                outputfile = os.path.join(outputpath, f"{speaker_id}_{suffix}_clip_{current_token}_({target_counts[current_token]}).wav")
                
                splitAudio(audiofile, 
                        tgWords[idx].minTime, 
                        tgWords[idx].maxTime,
                        outputfile,
                        1, 0)
                
                target_counts[current_token] += 1

print('Done splitting audio!')