from __future__ import print_function
import json
import pandas as pd
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account


def save_to_spreadsheet(data_to_insert, spreadsheet_id):

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'assignment_track_revenue/keys.json'

    creds=None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    SAMPLE_SPREADSHEET_ID = spreadsheet_id

    service = build('sheets', 'v4', credentials=creds)

    sheet=service.spreadsheets()
    aoa=[['Ankur', 'Tagra'],['Ankur1', 'Tagra1'], ['Ankur2', 'Tagra2']]
    value_range_body={'values':data_to_insert}

    request = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="df_import!A1",
                                                     valueInputOption="USER_ENTERED", body=value_range_body)
    response = request.execute()
    print(response)

    return 0


if __name__=='__main__':
    # read json file
    json_file_path='assignment_track_revenue/input_json.json'
    saved_file_path='assignment_track_revenue/result.csv'
    spreadsheet_id=''

    # Opening JSON file
    Json_file = open(json_file_path, )
    # returns JSON object as
    # a dictionary
    data = json.load(Json_file)
    # print(data)

    #create an empty dataframe to store combinations of profiles and privileges
    priveleges_df = pd.DataFrame(columns=['Profile', 'Privilege'])

    # iterate dictionary to generate all combinations of profiles and privileges
    for item in data.items():
        # print(item)
        profile = item[0]

        privileges = item[1]
        for privilege in privileges:
            # Append rows in Empty Dataframe by adding dictionaries
            priveleges_df = priveleges_df.append({'Profile': profile, 'Privilege': privilege}, ignore_index=True)

    # print(priveleges_df)

    # for all combinations that exist count value should be 1,
    # for all other count value should be 0
    priveleges_df['count'] = 1


    # unmelt the dataframe based on Profiles
    output_df = priveleges_df.pivot(index='Profile', columns='Privilege').reset_index()

    print(output_df)

    # replacing nan with 0 (these are all such combinations that don't exist) hence 0 value
    output_df = output_df.fillna(0)

    # all user profiles
    user_profiles = output_df['Profile']

    # all counts
    output_df = output_df['count'].reset_index()

    # concatenating user profiles with counts
    output_df['user_profile'] = user_profiles

    # selecting subset of coulmns and reordering
    output_df = output_df[['user_profile', 'view_grades', 'change_grades',
                           'add_grades', 'delete_grades', 'view_classes',
                           'change_classes', 'add_classes', 'delete_classes']]


    # convert float to numeric 1.0-> 1, 0.0-> 0
    for col in output_df.columns.values:
        try:
            output_df[col] = output_df[col].astype('int64')
        except:
            pass

    # save locally
    #Bonus point 1: If u can do it in python or PHP
    output_df.to_csv(saved_file_path, index=False)

    # prepare data for spreadsheet
    # convert dataframe into list of lists
    rows = output_df.values.tolist()
    columns=list(output_df.columns)
    rows.insert(0, columns)
    data_to_insert=rows

    # Bonus Point 2: if u can leverage Google API to create a spreadsheet
    # call save to spreadsheet method
    save_to_spreadsheet(data_to_insert, spreadsheet_id)


