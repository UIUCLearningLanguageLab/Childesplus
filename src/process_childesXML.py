import xml.etree.ElementTree as ET
import csv
import os
from copy import deepcopy
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

def combine_quotation_utterances(utterances, direction="forward"):
    # If backward, reverse the list and change the terminator type condition
    if direction == "backward":
        utterances = list(reversed(utterances))
        terminator_type_to_check = "quotation precedes"
    else:
        terminator_type_to_check = "quotation next line"

    num_utterances = len(utterances)
    combined_data = []

    i = 0
    while i < num_utterances:
        current_utterance = deepcopy(utterances[i])

        # Ensure there is a next row to combine with
        if i < num_utterances - 1:
            next_utterance = deepcopy(utterances[i + 1])

            # Combine current and next utterances based on the terminator type and speaker
            if current_utterance["terminator_type"] == terminator_type_to_check and current_utterance["speaker_id"] == \
                    next_utterance["speaker_id"]:
                combined_text = current_utterance["utterance_text"] + " " + next_utterance["utterance_text"]
                next_utterance["utterance_text"] = combined_text  # Modify the next utterance

                # Skip appending the current utterance as it has been combined
                i += 1  # Move to the next pair of utterances
            else:
                combined_data.append(current_utterance)
        else:
            # If it's the last row, just append it as-is
            combined_data.append(current_utterance)

        i += 1  # Move to the next utterance (or skip if combined)

    # If we processed in reverse, reverse the combined data back
    if direction == "backward":
        combined_data = list(reversed(combined_data))

    return combined_data

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
                        "q": "?",
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
                        "question exclamation": "?",
                        "None": ".",
                        "p": ".",
                        "question": "?",
                        "e": "!"}
    return punctuation_dict[utterance_terminator]