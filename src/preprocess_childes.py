import csv

def preprocess_childes(csv_path):
    import csv

    # Open the CSV file
    with open('your_file.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        # Convert the CSV reader object to a list of lists
        data = list(csvreader)