import xml.etree.ElementTree as ET
import csv
import os
import re

def get_document_file_path_list(input_directory):
    file_path_list = []
    for root_dir, _, files in os.walk(input_directory):
        for file_name in files:
            if file_name.endswith('.xml'):
                file_path = os.path.join(root_dir, file_name)
                file_path_list.append(file_path)
    return file_path_list

def process_xml_file(file_path, namespace):
    """Process a single XML file and extract utterances as dictionaries."""

    # Parse XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract participants and target child age
    participants = extract_participants(root, namespace)
    target_child_age = extract_target_child_age(root, namespace)
    utterance_list = extract_utterances(root, namespace)

    return participants, target_child_age, utterance_list

def extract_participants(root, namespace):
    """Extract participants from the XML."""
    return {
        participant.get('id'): {
            'role': participant.get('role', 'unknown'),
            'name': participant.get('name', participant.get('id')),
            'age': participant.get('age', 'unknown'),
            'sex': participant.get('sex', 'unknown'),
            'language': participant.get('language', 'unknown')
        }
        for participant in root.findall('.//ns:participant', namespace)
    }

def extract_target_child_age(root, namespace):
    """Extract target child's age in days."""
    target_child = root.find('.//ns:participant[@id="CHI"]', namespace)
    if target_child is not None and target_child.get('age'):
        return convert_age_to_days(target_child.get('age'))
    return "unknown"

def extract_utterances(root, namespace):
    """Extract utterances and their metadata from the XML."""
    utterance_list = []
    for utterance in root.findall('.//ns:u', namespace):
        speaker_id = utterance.get('who')
        words = ' '.join(word.text for word in utterance.findall('.//ns:w', namespace) if word.text)

        # Extract <mt> type attribute if available
        mt_tag = utterance.find('.//ns:mt', namespace)
        mt_type = mt_tag.get('type') if mt_tag is not None else "None"

        # Extract media and comments data
        media = utterance.find('.//ns:media', namespace)
        start_time = media.get('start') if media is not None else 'unknown'
        end_time = media.get('end') if media is not None else 'unknown'
        duration = (
            str(float(end_time) - float(start_time))
            if start_time != 'unknown' and end_time != 'unknown'
            else 'unknown'
        )
        comments = ' | '.join(comment.text for comment in utterance.findall('.//ns:a[@type="comments"]', namespace))

        # Create the utterance dictionary
        utterance_list.append({
            "utterance_text": words,
            "speaker_id": speaker_id,
            "start_time_sec": start_time,
            "end_time_sec": end_time,
            "duration_sec": duration,
            "comments_text": comments,
            "terminator_type": mt_type
        })
    return utterance_list

def find_consecutive_cases(utterances):
    """Check for consecutive 'quotation next line' or 'quotation precedes' cases
    and print them with surrounding context."""
    consecutive_next_line = []
    consecutive_precedes = []

    # Loop through the utterances and find consecutive patterns
    for i in range(len(utterances) - 1):
        if (utterances[i]["terminator_type"] == "quotation next line" and
            utterances[i + 1]["terminator_type"] == "quotation next line"):
            consecutive_next_line.append(i)

        if (utterances[i]["terminator_type"] == "quotation precedes" and
            utterances[i + 1]["terminator_type"] == "quotation precedes"):
            consecutive_precedes.append(i)

    # Print the results with context
    if consecutive_next_line:
        print("Consecutive 'quotation next line' cases found:")
        for index in consecutive_next_line:
            print_with_context(utterances, index, index + 1)

    if consecutive_precedes:
        print("Consecutive 'quotation precedes' cases found:")
        for index in consecutive_precedes:
            print_with_context(utterances, index - 1, index)

def print_with_context(utterances, start_index, end_index):
    """Print the utterances between start and end indices, with context."""
    print(f"\nContext from index {start_index} to {end_index}:")

    # Print each utterance in the specified range
    for i in range(max(0, start_index), min(end_index + 2, len(utterances))):
        print(f"Index {i}: {utterances[i]}")


def combine_rows(first_row, second_row, template_row):
    """Combine two rows by keeping all values of 'template_row' except
    for 'utterance_text', which is concatenated from both rows."""
    # Create a copy of the template row to avoid modifying the original
    combined_row = template_row.copy()

    # Concatenate the 'utterance_text' fields with a space in between
    combined_row["utterance_text"] = first_row["utterance_text"] + " " + second_row["utterance_text"]

    return combined_row


def combine_quotation_rows(utterances):
    total_replacements = 0  # Track total replacements across iterations

    while True:
        """Combine rows based on the 'terminator_type' column rules."""
        replacements_made = 0  # Track the number of replacements made in this pass
        combined_data = []  # Store the resulting combined rows
        combined_row_index_list = []  # Track combined row indices
        skip_next = False  # Flag to skip the next row

        i = 0  # Index to iterate through the utterances
        while i < len(utterances) - 1:
            current_row = utterances[i]
            next_row = utterances[i + 1]

            if skip_next:
                skip_next = False  # Reset the flag and continue
                i += 1
                continue

            if current_row["terminator_type"] == "quotation next line":
                # Handle multiple consecutive "quotation next line"
                combined_text = current_row["utterance_text"]
                template_row = next_row

                # Merge all consecutive "quotation next line" rows
                j = i + 1
                while j < len(utterances) and utterances[j]["terminator_type"] == "quotation next line":
                    combined_text += " " + utterances[j]["utterance_text"]
                    j += 1

                # Add the non-quotation row's text at the end
                if j < len(utterances):
                    combined_text += " " + utterances[j]["utterance_text"]
                    template_row = utterances[j]

                # Create the combined row and track it
                combined_row = template_row.copy()
                combined_row["utterance_text"] = combined_text
                combined_data.append(combined_row)
                combined_row_index_list.append(len(combined_data) - 1)
                replacements_made += 1

                # Skip all processed rows
                i = j

            elif next_row["terminator_type"] == "quotation precedes":
                # Handle multiple consecutive "quotation precedes"
                combined_text = current_row["utterance_text"]

                j = i + 1
                while j < len(utterances) and utterances[j]["terminator_type"] == "quotation precedes":
                    combined_text += " " + utterances[j]["utterance_text"]
                    j += 1

                # Create the combined row and track it
                combined_row = current_row.copy()
                combined_row["utterance_text"] = combined_text
                combined_data.append(combined_row)
                combined_row_index_list.append(len(combined_data) - 1)
                replacements_made += 1

                # Skip all processed rows
                i = j

            else:
                # If no combination is needed, add the current row as-is
                combined_data.append(current_row)
                i += 1  # Move to the next row

        # Add the last row if it wasn't part of a combination
        if i == len(utterances) - 1:
            combined_data.append(utterances[-1])

        # Accumulate total replacements
        total_replacements += replacements_made

        # If no replacements were made in this iteration, stop
        if replacements_made == 0:
            break

    print(f"Total replacements made: {total_replacements}")

    return combined_data, total_replacements


def save_to_csv(data, output_path):
    """Save the combined utterances to a CSV file."""
    output_file_name = 'all_utterances.csv'
    output_file = os.path.join(output_path, output_file_name)

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = data[0].keys()  # Use the headers from the first row
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"All utterances have been successfully written to {output_file}")


def convert_age_to_days(age_string):
    """Convert an ISO 8601 age string (e.g., 'P2Y6M10D') to total days."""
    match = re.match(r'P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?', age_string)

    if match:
        years, months, days = [int(x) if x else 0 for x in match.groups()]
        return years * 365 + months * 30 + days
    else:
        #print(f"Warning: Invalid age string '{age_string}'")
        return "unknown"  # Return 'unknown' if the format is invalid


def get_punctuation(utterance_terminator):
    punctuation_dict = {'declarative': ".",
                        "question": "?",
                        "trail off": ";",
                        "imperative": "!",
                        "imperative_emphatic": "!",
                        "interruption": ":",
                        "self interruption": ";",
                        "quotation next line": ";",
                        "interruption question": "?",
                        "missing CA terminator": ".",
                        "broken for coding": ".",
                        "trail off question": "?",
                        "quotation precedes": ".",
                        "self interruption question": "?",
                        "question exclamation": "?"}
    return punctuation_dict[utterance_terminator]