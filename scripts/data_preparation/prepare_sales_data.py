"""
Module 2: Prep Sales Data
File: scripts/prepare_customers_data.py
This script is responsible for preparing customer data by reading it from CSV files
and processing it into a pandas DataFrame object.
"""

import pathlib
import sys
import pandas as pd

# For local imports, temporarily add project root to Python sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import logger
from utils.logger import logger

# Define folder paths
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw_data"
prepared_data_dir = PROJECT_ROOT / "data" / "prepared" 

# Constants
DATA_DIR: pathlib.Path = PROJECT_ROOT.joinpath("data")
RAW_DATA_DIR: pathlib.Path = DATA_DIR.joinpath("raw")

# Create the 'data/prepared' directory if it doesn't exist
prepared_data_dir = PROJECT_ROOT / "data" / "prepared"
prepared_data_dir.mkdir(parents=True, exist_ok=True)

# File paths
input_file = RAW_DATA_DIR / "sales_data.csv"
output_file = prepared_data_dir/ "sales_data_prepared.csv"

# Expected valid values for cleaning
DISCOUNTPERCENT_MIN = 0
DISCOUNTPERCENT_MAX = 100
expected_columns = {
            "TransactionID": "int64",
            "SaleDate": "datetime64[ns]",
            "CustomerID": "int64",
            "ProductID": "int64", 
            "StoreID": "int64", 
            "CampaignID": "int64",
            "SaleAmount": "float64",
            "DiscountPercent": "int64",
            "State": "object",}

def read_raw_data(file_name: str) -> pd.DataFrame:
    """Read raw data from CSV."""
    file_path: pathlib.Path = RAW_DATA_DIR.joinpath(file_name)
    try:
        logger.info(f"Reading raw data from {file_path}.")
        return pd.read_csv(file_path)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame if the file is not found
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if any other error occurs

def process_data(file_name: str) -> pd.DataFrame:
    """Process raw data by reading it into a pandas DataFrame object."""
    df = read_raw_data(file_name)

    # Remove duplicate 
    df = df.drop_duplicates()
    logger.info(f"After duplicates removal: shape = {df.shape}")

    # Convert SaleDate to datetime 
    df["SaleDate"] = pd.to_datetime(df["SaleDate"])

    logger.info("Verifying columns and types...")

    # Check if the number of columns is correct
    if len(df.columns) != len(expected_columns):
        logger.error(f"Incorrect number of columns. Expected: {len(expected_columns)}, Found: {len(df.columns)}")
        return pd.DataFrame()
    
     # Check if all expected columns are present
    for col_name in expected_columns:
        if col_name not in df.columns:
            logger.error(f"Missing column: {col_name}")
            return pd.DataFrame()
        
    # Convert DiscountPercent to int64 and handle errors
    try:
        df["DiscountPercent"] = pd.to_numeric(df["DiscountPercent"], errors='coerce').astype('int64')
    except Exception as e:
        logger.error(f"Error converting DiscountPercent to int64: {e}")
        return pd.DataFrame()

    # Check the data type of each column
    for col_name, expected_type in expected_columns.items():
        actual_type = str(df[col_name].dtype)
        if actual_type != expected_type:
            logger.error(f"Incorrect data type for column '{col_name}'. Expected: {expected_type}, Found: {actual_type}")
            return pd.DataFrame()

    logger.info("Columns and types verified successfully.")
    
    # Filter DiscountPercent outliers: keep only values between DISCOUNTPERCENT_MIN and DISCOUNTPERCENT_MAX
    before = df.shape[0]
    df = df[(df['DiscountPercent'] >= DISCOUNTPERCENT_MIN) & (df['DiscountPercent'] <= DISCOUNTPERCENT_MAX)]
    logger.info(f"Dropped {before - df.shape[0]} rows due to DiscountPercent outliers")

     # Clean State: strip and standardize case; drop rows with invalid values
    df['State'] = df['State'].astype(str).str.strip().str.upper()
    before = df.shape[0]
    def process_data(file_name: str) -> pd.DataFrame:
        """Process raw data by reading it into a pandas DataFrame object."""
    df = read_raw_data(file_name)

    # Remove duplicates
    df = df.drop_duplicates()
    logger.info(f"After duplicates removal: shape = {df.shape}")

    # Convert SaleDate to datetime
    df["SaleDate"] = pd.to_datetime(df["SaleDate"])

    logger.info("Verifying columns and types...")

    # Check if the number of columns is correct
    if len(df.columns) != len(expected_columns):
        logger.error(f"Incorrect number of columns. Expected: {len(expected_columns)}, Found: {len(df.columns)}")
        return pd.DataFrame()

    # Check if all expected columns are present
    for col_name in expected_columns:
        if col_name not in df.columns:
            logger.error(f"Missing column: {col_name}")
            return pd.DataFrame()

    # Convert DiscountPercent to int64 and handle errors
    try:
        df["DiscountPercent"] = pd.to_numeric(df["DiscountPercent"], errors='coerce').astype('int64')
    except Exception as e:
        logger.error(f"Error converting DiscountPercent to int64: {e}")
        return pd.DataFrame()

    # Check the data type of each column
    for col_name, expected_type in expected_columns.items():
        actual_type = str(df[col_name].dtype)
        if actual_type != expected_type:
            logger.error(f"Incorrect data type for column '{col_name}'. Expected: {expected_type}, Found: {actual_type}")
            return pd.DataFrame()

    logger.info("Columns and types verified successfully.")

    # Filter DiscountPercent outliers: keep only values between DISCOUNTPERCENT_MIN and DISCOUNTPERCENT_MAX
    before = df.shape[0]
    df = df[(df['DiscountPercent'] >= DISCOUNTPERCENT_MIN) & (df['DiscountPercent'] <= DISCOUNTPERCENT_MAX)]
    logger.info(f"Dropped {before - df.shape[0]} rows due to DiscountPercent outliers")

    # Clean State: strip and standardize case; drop rows with invalid values
    df['State'] = df['State'].astype(str).str.strip().str.upper()
    before = df.shape[0]
    df = df[df['State'].str.len() == 2]
    logger.info(f"Dropped {before - df.shape[0]} rows due to invalid State")

    return df

def main() -> None:
    """Main function for processing customer, product, and sales data."""
    logger.info("Starting data preparation...")
    df_clean = process_data("sales_data.csv")
    if not df_clean.empty:
        try:
            df_clean.to_csv(output_file, index=False)
            logger.info(f"Cleaned sales data saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving cleaned data: {e}")
    else:
        logger.error("Data preparation failed. No data to save.")

if __name__ == "__main__":
    main()