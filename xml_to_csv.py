from src import process_childesXML

def main():
    input_path = 'data/childes_xml/'
    output_path = 'data/childes_csv/'

    process_childesXML.xml_to_csv(input_path, output_path)

if __name__ == "__main__":
    main()