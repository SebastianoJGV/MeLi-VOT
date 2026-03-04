import csv
import os
from pathlib import Path

def process_and_tally_csvs(source_directory, output_file):
    source_path = Path(source_directory)
    
    # Define the columns that contain the tally data
    tally_cols_eng = ['K','G','B','P','D','T','ʈ','k','g','b','p','d','t','DH','TH']
    tally_cols_man = ['K','G','B','P','D','T','ʈ','k','g','b','p','d','t','tɕ','ʈʂ','tʰ','pʲ','ts','tɕʰ','kʷ','pʷ','pʰ','tɕʷ','tʷ','tʲ','ʈʂʰ','kʰ','tsʰ']
    if 'English' in source_directory: totals = {col: 0 for col in tally_cols_eng}
    elif 'Mandarin 'in source_directory: totals = {col: 0 for col in tally_cols_man}
    
    header_written = False
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        
        for file_path in source_path.rglob('*.csv'):
            if file_path.name == os.path.basename(output_file):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f_in:
                reader = list(csv.reader(f_in))
                if len(reader) < 3: continue # Skip files too small to have data
                
                header = reader[0]
                data_rows = reader[1:-1]
                tally_row = reader[-1]
                
                # 1. Write Header once 
                if not header_written:
                    writer.writerow(['Source_File'] + header)
                    header_written = True
                
                # Map tally row to header names and update totals
                # Dict used to ensure we match the right column even if order shifts
                row_dict = dict(zip(header, tally_row))
                if 'English' in source_directory:
                    for col in tally_cols_eng:
                        try:
                            # Convert to float/int and add to running total
                            totals[col] += float(row_dict.get(col, 0))
                        except ValueError:
                            pass # Handle non-numeric tally data if necessary
                elif 'Mandarin' in source_directory:
                    for col in tally_cols_man:
                        try:
                            # Convert to float/int and add to running total
                            totals[col] += float(row_dict.get(col, 0))
                        except ValueError:
                            pass # Handle non-numeric tally data if necessary

                # 3. Write data rows with source file name
                for row in data_rows:
                    writer.writerow([file_path.name] + row)
        
        # 4. Write the Grand Total Row at the very end
        # We create a blank row, then fill in the totals where they belong
        final_row = ['GRAND TOTAL'] + ([''] * len(header))
        for i, col_name in enumerate(header):
            if col_name in totals:
                # i + 1 because of the 'Source_File' column shift
                final_row[i + 1] = totals[col_name]
        
        writer.writerow([]) # Empty line for visual separation
        writer.writerow(final_row)

# Execute
process_and_tally_csvs('/mnt/7dcb7dc5-1dac-4ad3-bf5b-02dbda1356ee/MeLi/All Mandarin CSVs', 'final_consolidated_man_data.csv')