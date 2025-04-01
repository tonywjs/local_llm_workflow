from io import BytesIO

import pandas as pd


def load_data(file):
    """
    Load data from uploaded file with improved error handling and debugging
    """
    try:
        # Debug information

        # Read file in chunks to handle large files
        chunks = []
        chunk_size = 1024 * 1024  # 1MB chunks

        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)

        # Combine chunks and create BytesIO object
        file_content = BytesIO(b"".join(chunks))
        file.seek(0)  # Reset file pointer for potential future reads

        if file.name.endswith(".csv"):
            try:
                data = pd.read_csv(file_content, on_bad_lines="skip")
            except Exception as e:
                raise ValueError(f"Error reading CSV file: {str(e)}")
        elif file.name.endswith(".tsv"):
            try:
                data = pd.read_csv(file_content, sep="\t", on_bad_lines="skip")
            except Exception as e:
                raise ValueError(f"Error reading TSV file: {str(e)}")
        elif file.name.endswith(".xlsx"):
            try:
                data = pd.read_excel(file_content)
            except Exception as e:
                raise ValueError(f"Error reading Excel file: {str(e)}")
        else:
            raise ValueError(
                "Unsupported file format. Please upload a CSV, TSV, or Excel file."
            )

        # Basic data validation
        if data is None or data.empty:
            raise ValueError("The uploaded file contains no data")

        return data
    except Exception as e:
        raise Exception(f"Error loading file: {str(e)}")


def validate_data(data):
    """
    Validate the uploaded data with more flexible validation
    """
    try:
        # Basic validation checks
        if data.empty:
            raise ValueError("The uploaded file contains no data")
        if len(data.columns) < 1:
            raise ValueError("Data must have at least one column")
        return True

    except Exception as e:
        raise ValueError(f"Data validation error: {str(e)}")


def get_data_summary(data: pd.DataFrame):
    """
    Generate a comprehensive summary of the data including basic statistics,
    column types, and missing value information
    """
    try:
        # Get column types
        numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = data.select_dtypes(include=["object"]).columns.tolist()

        # Calculate missing values percentage
        missing_percentages = (data.isnull().sum() / len(data) * 100).round(2)
        summary = {
            "shape": data.shape,
            "rows": data.index,
            "columns (first 7)": data.columns.tolist()[:7],
            # "null_percentage": missing_percentages.to_dict(),
        }
        return summary
    except Exception as e:
        raise Exception(f"Error generating data summary: {str(e)}")
