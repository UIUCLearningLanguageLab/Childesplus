from src import childes

def main():
    input_path = 'data/childes_xml/'
    output_path = 'data/childes_json/full_childes_20241019.json'

    test_path = 'data/test_xml/'

    childes_corpus = childes.Childes()
    childes_corpus.add_childes_xml(input_path)
    childes_corpus.set_unknown_token()

    childes_corpus.save_json(output_path)

if __name__ == "__main__":
    main()