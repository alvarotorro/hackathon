import pandas as pd

def analyze_excel(file_path: str):
    """Analyze the structure of an Excel file."""
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        print(f"\nExcel file contains {len(excel_file.sheet_names)} sheets:")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\nSheet: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Columns: {', '.join(df.columns)}")
            print(f"Sample data:")
            print(df.head())
            print("\n" + "="*50)
            
    except Exception as e:
        print(f"Error analyzing Excel file: {str(e)}")

if __name__ == "__main__":
    analyze_excel("data/mock_data.xlsx") 