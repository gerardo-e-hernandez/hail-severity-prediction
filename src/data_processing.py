import pandas as pd
import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
import os
from datetime import datetime, timedelta

def download_spc_reports(start_date: str, end_date: str, save_path: str):
    """
    Downloads SPC storm reports (hail, wind, tornado) for a given date range.

    Args:
        start_date (str): The start date in YYYYMMDD format.
        end_date (str): The end date in YYYYMMDD format.
        save_path (str): The directory path to save the CSV files.
    """
    print(f"Downloading SPC reports from {start_date} to {end_date}...")
    os.makedirs(save_path, exist_ok=True)
    
    base_url = "https://www.spc.noaa.gov/climo/reports/"
    date_range = pd.to_datetime(pd.date_range(start=start_date, end=end_date))
    
    for date in date_range:
        report_date_str = date.strftime('%y%m%d')
        file_url = f"{base_url}{report_date_str}_rpts.csv"
        save_file = os.path.join(save_path, f"{report_date_str}_rpts.csv")
        
        try:
            df = pd.read_csv(file_url)
            df.to_csv(save_file, index=False)
            print(f"Successfully downloaded and saved {save_file}")
        except Exception as e:
            print(f"Could not download report for {report_date_str}. Reason: {e}")

def download_nexrad_data(scan_time: datetime, radar_site: str, save_dir: str):
    """
    Downloads a NEXRAD Level 2 file from AWS for a specific time and site.

    Args:
        scan_time (datetime): The UTC time of the radar scan.
        radar_site (str): The 4-letter radar site ID (e.g., 'KFTG').
        save_dir (str): The directory to save the downloaded file.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        # Use unsigned requests to access public S3 bucket
        s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
        bucket_name = 'noaa-nexrad-level2'
        
        # A more robust way is to list objects around the desired time
        prefix = scan_time.strftime(f'%Y/%m/%d/{radar_site}/{radar_site}%Y%m%d_%H')
        
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            print(f"No files found for {radar_site} around {scan_time}")
            return

        # Find the closest scan to the requested time
        files = response['Contents']
        closest_file = min(files, key=lambda x: abs(x['LastModified'].replace(tzinfo=None) - scan_time))
        
        file_key = closest_file['Key']
        filename = os.path.basename(file_key)
        save_path = os.path.join(save_dir, filename)

        if os.path.exists(save_path):
            print(f"File already exists: {save_path}")
            return

        print(f"Downloading {file_key} to {save_path}...")
        s3.download_file(bucket_name, file_key, save_path)
        print("Download complete.")

    except NoCredentialsError:
        print("Credentials not available. Please configure AWS credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")