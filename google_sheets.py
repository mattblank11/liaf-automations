# Import packages
from settings import *

'''
Method: update_data_in_sheets()

Summary: Updates data in Google Sheet
'''
def update_data_in_sheets(
    df,
    tab,
):
    # Authorize Google Sheets API
    authorization_json = {
      'type': 'service_account',
      'project_id': os.environ['sheets_project_id'],
      'private_key_id': os.environ['sheets_private_key_id'],
      'private_key': os.environ['sheets_private_key'],
      'client_email': os.environ['sheets_client_email'],
      'client_id': os.environ['sheets_client_id'],
    }
    gc = pygsheets.authorize(service_file = authorization_json)
    
    # Navigate to the intended tab and clear current contents
    spreadsheet_id = os.environ['liaf_gsheet_id']
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.worksheet_by_title(tab)
    worksheet.clear()
    
    # Fill df data in tab
    df = df.fillna("")
    worksheet.set_dataframe(df, (1, 1), fit = True)

    return df

'''
Method: get_csv_from_s3()

Summary: Gets a specific csv from S3
'''
def get_data_from_s3(
    s3_bucket,
    report,
):
    try:
      return pd.read_csv(
          s3_fs.open(
              s3_bucket + '/' + report + '.csv'
          ),
          encoding='latin-1',
      )
    except pd.errors.EmptyDataError:
      return pd.DataFrame()

'''
Method: update_data_in_s3()

Summary: Posts a specific csv to S3
'''
def update_data_in_s3(
    s3_bucket,
    report,
    df,
):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_boto.Bucket(s3_bucket).put_object(
        Key =  report + '.csv',
        Body = csv_buffer.getvalue()
    )

'''
Method: update_csv()

Summary: Run code to update a specific csv
'''
def update_csv(
    report,
    data_to_append,
):
    # Get s3 bucket value
    s3_bucket = os.environ['liaf_s3_bucket']

    # Get data from S3
    df = get_data_from_s3(
        s3_bucket,
        report,
    )

    # Append data_to_append to df
    updated_df = df.append(
        data_to_append,
        ignore_index = True
    )

    # Remove duplicate rows
    updated_df = updated_df.drop_duplicates()
    
    # Post 'Completed Lectures.csv' to S3
    update_data_in_s3(
        s3_bucket,
        report,
        updated_df,
    )

    return updated_df

'''
Method: aggregate_liaf_data()

Summary: Run code to aggregate LIAF data for each day and add it to the Google Sheet
'''
def aggregate_liaf_data(
    reports_to_aggregate
):
    # Get s3 bucket value
    s3_bucket = os.environ['liaf_s3_bucket']

    # Define an empty list we'll add aggregation data to
    aggregate_data = []

    # Loop through each report in reports_to_aggregate
    for report in reports_to_aggregate:
        # Get data from S3
        report_df = get_data_from_s3(
            s3_bucket,
            report['Report'],
        )

        # Set date column as datetime
        report_df[report['Date Column']] = pd.to_datetime(report_df[report['Date Column']])

        # Set a start date
        date = dt.datetime(2021, 1, 1)

        # Loop through all dates from the start date until today
        while date <= dt.datetime.today():
            # Get date as string
            date_string = date.strftime('%m/%d/%Y')

            # Perform aggregation
            data_on_date = report_df[
                    report_df[report['Date Column']] == date
                ][
                    report['Aggregate Column']
                ]
            if report['Aggregation Type'] == 'sum':
                data_on_date = data_on_date.sum()
            elif report['Aggregation Type'] == 'count':
                data_on_date = data_on_date.count()
            
            # Add aggregate calculation to aggregate_data. If the date is already in aggregate_data,
            # add the data to that day's data. Otherwise create a new dictionary
            try:
                [
                    dictionary for dictionary in aggregate_data if dictionary['Date'] == date_string
                ][0].update({
                    report['Aggregation Name']: data_on_date,
                })
            except IndexError:
                aggregate_data.append({
                    'Date': date_string,
                    report['Aggregation Name']: data_on_date,
                })

            # print(f'{date} / {report['Aggregation Name']} / {data_on_date}')
            date += dt.timedelta(days = 1)

    # Convert aggregate_data to df
    aggregate_data_df = pd.DataFrame(aggregate_data)

    # Store aggregate_data_df in S3
    update_data_in_s3(
        s3_bucket,
        'Aggregate Data',
        aggregate_data_df,
    )
    
    # Store data in Google Sheet
    update_data_in_sheets(
        aggregate_data_df,
        'Data',
    )
