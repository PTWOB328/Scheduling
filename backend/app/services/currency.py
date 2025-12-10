import pandas as pd
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, date
from ..models.currency import CurrencyRecord
from ..models.pilot import Pilot


def parse_excel_file(file_path: str) -> pd.DataFrame:
    """Parse Excel file and return DataFrame"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        raise ValueError(f"Error parsing Excel file: {str(e)}")


def parse_csv_file(file_path: str) -> pd.DataFrame:
    """Parse CSV file and return DataFrame"""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")


def map_pilot_from_spreadsheet(row: Dict[str, Any], pilot_mapping: Dict[str, int]) -> int:
    """
    Map spreadsheet row to pilot ID
    pilot_mapping should map spreadsheet identifiers (call_sign, name, etc.) to pilot IDs
    """
    # Try to find pilot by various identifiers
    for identifier_key in ['call_sign', 'name', 'pilot_name', 'pilot_id', 'id']:
        if identifier_key in row:
            identifier = str(row[identifier_key]).strip()
            if identifier in pilot_mapping:
                return pilot_mapping[identifier]
    
    raise ValueError(f"Could not map row to pilot: {row}")


def extract_currency_data(df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Extract currency data from DataFrame using column mapping
    column_mapping: maps spreadsheet columns to our data model
    """
    currency_records = []
    
    for _, row in df.iterrows():
        record = {}
        for our_field, spreadsheet_column in column_mapping.items():
            if spreadsheet_column in row:
                record[our_field] = row[spreadsheet_column]
        currency_records.append(record)
    
    return currency_records


def import_currency_records(
    db: Session,
    file_path: str,
    file_type: str,
    pilot_mapping: Dict[str, int],
    column_mapping: Dict[str, str]
) -> List[CurrencyRecord]:
    """
    Import currency records from spreadsheet file
    
    Args:
        db: Database session
        file_path: Path to the spreadsheet file
        file_type: 'excel' or 'csv'
        pilot_mapping: Maps spreadsheet identifiers to pilot IDs
        column_mapping: Maps our fields to spreadsheet columns
    """
    # Parse file
    if file_type == 'excel':
        df = parse_excel_file(file_path)
    elif file_type == 'csv':
        df = parse_csv_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # Extract data
    raw_records = extract_currency_data(df, column_mapping)
    
    # Create currency records
    currency_records = []
    for raw_record in raw_records:
        try:
            pilot_id = map_pilot_from_spreadsheet(raw_record, pilot_mapping)
            
            # Parse dates if present
            last_completed_date = None
            expiration_date = None
            if 'last_completed_date' in raw_record and raw_record['last_completed_date']:
                try:
                    last_completed_date = pd.to_datetime(raw_record['last_completed_date']).date()
                except:
                    pass
            
            if 'expiration_date' in raw_record and raw_record['expiration_date']:
                try:
                    expiration_date = pd.to_datetime(raw_record['expiration_date']).date()
                except:
                    pass
            
            # Determine status
            status = "current"
            if expiration_date:
                if expiration_date < date.today():
                    status = "expired"
                elif (expiration_date - date.today()).days <= 30:
                    status = "expiring"
            
            currency_record = CurrencyRecord(
                pilot_id=pilot_id,
                currency_type=raw_record.get('currency_type', 'unknown'),
                last_completed_date=last_completed_date,
                expiration_date=expiration_date,
                status=status,
                raw_data=raw_record
            )
            
            db.add(currency_record)
            currency_records.append(currency_record)
        except Exception as e:
            # Log error but continue with other records
            print(f"Error processing record: {e}")
            continue
    
    db.commit()
    return currency_records
