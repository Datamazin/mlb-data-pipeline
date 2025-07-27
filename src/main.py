from src.etl.extract import extract_data
from src.etl.transform import transform_data
from src.etl.load import load_data

def main():
    # Extract data from the MLB API
    extracted_data = extract_data()
    
    # Transform the extracted data
    transformed_data = transform_data(extracted_data)
    
    # Load the transformed data into the database
    load_data(transformed_data)

if __name__ == "__main__":
    main()