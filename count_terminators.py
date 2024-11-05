import csv
from collections import Counter

def import_csv(csv_file):
    """
    Imports a CSV file and returns a list of dictionaries representing the rows.
    """
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        utterance_info_list = list(reader)  # Convert the reader to a list of dictionaries

    return utterance_info_list

def print_particular_utterances(utterance_info_list):
    for row in utterance_info_list:
        print_next_line = False
        terminator_type = row.get('terminator_type', 'None')  # Default to 'None' if not found
        utterance = row.get("utterance_text", 'None')

        if terminator_type == 'quotation next line':
            print_next_line = True
            print(utterance)
        if print_next_line:
            print(utterance)
            print_next_line = False

def count_terminator_types(utterance_info_list):
    """
    Counts the frequency of different values in the 'terminator_type' column.
    """
    terminator_counts = Counter()

    # Iterate over each row and count the values in 'terminator_type' column
    for row in utterance_info_list:
        terminator_type = row.get('terminator_type', 'None')  # Default to 'None' if not found
        terminator_counts[terminator_type] += 1

    return terminator_counts

def print_terminator_counts(counts):
    # Print the results
    print("Frequency of terminator types:")
    for terminator, count in counts.items():
        print(f"{terminator}: {count}")

# Example usage
csv_file = './data/childes_csv/all_utterances.csv'  # Replace with your CSV file path

utterance_info_list = import_csv(csv_file)
counts = count_terminator_types(utterance_info_list)
print_particular_utterances(utterance_info_list)
print_terminator_counts(counts)

