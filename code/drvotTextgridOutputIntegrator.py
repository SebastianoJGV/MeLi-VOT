import csv
import os
import textgrid
import csv
from pathlib import Path
from tqdm import tqdm

def build_nested_dict(csv_file_path):
    nested_dict = {}
    #print(csv_file_path)
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        #print(reader)
        rows = list(reader)
        for i, row in enumerate(rows[:-1]):
            speaker = row['Source_File'][0:4]
            token = row['phone']
            index = row['phoneIndex']

            # Build the nested structure
            if speaker not in nested_dict:
                nested_dict[speaker] = {}
            if token not in nested_dict[speaker]:
                nested_dict[speaker][token] = {}
            if index not in nested_dict[speaker][token]:
                nested_dict[speaker][token][index] = i + 1 # This is so that it skips the header row!
                #print(f"adding row {i} to {index}")
            else:
                # This should never happen
                print(f"Conflict: Speaker '{speaker}' already has a row for token '{token}' with index {index}.")
    value = nested_dict.get('M98B', {}).get('G', {}).get('3')
    #print(f'value is: {value}')
    return nested_dict

def getVOT(tg):
    vot_tier = tg
    vot = 0
    for segments in range(len(vot_tier)):
        #print(segments)
        if "VOT" in vot_tier[segments].mark:
            vot = vot_tier[segments].maxTime - vot_tier[segments].minTime
    return vot

#------------------------------ CHANGE THIS IF YOU MOVE THE INPUT FILES
eng_csv_path = Path("/home/seb/Documents/UBC/UBC Coding Environment/final_consolidated_eng_data.csv")
eng_nested_dict = build_nested_dict(eng_csv_path)

man_csv_path = Path("final_consolidated_man_data.csv")
man_nested_dict = build_nested_dict(man_csv_path)
#------------------------------

row_keys = eng_nested_dict.keys()
#print(row_keys)


## -------------------------------------------
#  HERE IS THE TEXTGRID OPENING
## -------------------------------------------
#input('wait here')
with open(eng_csv_path, 'r', newline='', encoding='utf-8') as infile:
    eng_old_rows = [row for row in csv.reader(infile)]

with open(man_csv_path, 'r', newline='', encoding='utf-8') as infile:
    man_old_rows = [row for row in csv.reader(infile)]

#input('wait here')
textgrid_directory_path = '/mnt/7dcb7dc5-1dac-4ad3-bf5b-02dbda1356ee/School Stuff/MeLi/Dr.VOT Output TextGrids'


for root, dirs, files in tqdm(os.walk(textgrid_directory_path), desc="Analyzing Tiers", leave=False):
    for file in files:
        file_path = os.path.join(root, file)
        #print(f"Found file: {file_path}")
        current_tg = textgrid.TextGrid.fromFile(file_path)
        #print(current_tg)
        #print(current_tg[1][1].mark)
        parts = file.replace(".TextGrid", "").split("_")
        speaker = parts[0]
        language = parts[1]
        phone = parts[3]
        index = parts[4][1:-1]
        prediction = parts[5]

        #print(speaker, language, phone, index, prediction)
        row_index = None
        if language == "E":
            row_index = eng_nested_dict.get(speaker, {}).get(phone, {}).get(index)
        elif language == "M":
            row_index = man_nested_dict.get(speaker, {}).get(phone, {}).get(index)
        #print(row_index)

        if row_index is not None:
            # Get VOT
            # print(f'getting vot from {current_tg}')
            vot = getVOT(current_tg[1])

            # Append VOT and prediction to the row
            if language == "E":
                eng_old_rows[row_index].extend([vot, prediction])
            elif language == "M":
                man_old_rows[row_index].extend([vot, prediction])
            #print(eng_old_rows[1])

#input('wait')
#print(eng_old_rows[0])
with open("updated_eng.csv", 'w', newline='', encoding='utf-8') as eng_out:
    eng_writer = csv.writer(eng_out)
    eng_writer.writerow(eng_old_rows[0] + ["VOT", "VOT_Type"])  # Add headers at the end
    for row in eng_old_rows[1:]:  # Skip header row
        eng_writer.writerow(row)
        #print(eng_old_rows[row])

with open("updated_man.csv", 'w', newline='', encoding='utf-8') as man_out:
    man_writer = csv.writer(man_out)
    man_writer.writerow(man_old_rows[0] + ["VOT", "VOT_Type"])  # Add headers at the end
    for row in man_old_rows[1:]:  # Skip header row
        man_writer.writerow(row)
