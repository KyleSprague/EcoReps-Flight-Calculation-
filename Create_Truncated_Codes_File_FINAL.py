'''
Author: Kyle Sprague
Date: 08/15/2022
contact: ksprague2020@gmail.com

The aim of this program is to create a truncated version of the air_codes file that contains only airports Bates faculty and staff have been to based on the business travel file "JPM Airline Activity 7.1.2020 - 6.30.21 for Tom.xlsx".
The formatting of the new file, entitled "modified_air_codes.csv" is the same as "airport_codes.csv" such that it can be processed in the same manner as "airport_codes.csv" by an existing emissions calculation program created by Biruk Chafamo in 2022.
Unfortunately, the program could not be optimized such that the index of the row in the Bates business travel could be tracked despite an extensive amount of time being dedicated to this task. Ideally,
this program could be altered in the future such that the index could be tracked; this would mean that, should any aiports share the same IATA or local_code in the future, the user could easily deduce and choose which
one to include in the generated spreadsheet by simply looking at the appropriate row the Bates business travel file.

The programs contains the functions read_airport_codes, read_travel_file, unique_airports, and create_modif_airport_codes, the details of which are provided below.

'''

'''
importing relevant libraries
'''

import numpy as np
import pandas as pd

def read_airport_codes(filename: str) -> object:
    '''This function takes the file name as a string, reads the file and assigns it to a data frame:

    Inputs:
        str -- filename: the name of the file as a string

    Returns: a Pandas dataframe object containing information in "airport_codes.csv"
    '''
    air_codes_df = pd.read_csv(filename)
    return air_codes_df

def read_travel_file() -> object:
    '''
    A function which takes the excel file it is handed, reads, it, and stores this information in a Pandas data frame.

    Inputs:
        None

    Returns: a Pandas data frame object with information from the travel file
    '''
    name = 'JPM Airline Activity 7.1.2020 - 6.30.21 for Tom.xlsx' #alt code: input("Please enter the name of your travel file along with the file extension ")
    travel_df = pd.read_excel(name)
    return travel_df

def unique_airports(travel_df) -> array:
    '''
    A function which identifies unique airports within the travel dataframe, then removes the unique airport identified by "---" (aka the placeholder Bates uses
    when the origin and/or destionation of a flight is unknown)

    Inputs:
        object -- travel_df: the data frame containing the Bates travel file data

    Returns:
        The list of unique airports as a Numpy array

    '''
    unique_airports = pd.concat([travel_df['Origination'], travel_df['Destination']]).unique() #creates an array with all airports and selects the unique ones
    mod_unique_airports = [i for i in unique_airports if i != "---"] #takes out any origin/destination marked as "---"
    return mod_unique_airports

def create_modif_airport_codes(air_codes_df: object, airports: list) -> object:

    '''
        This function is the heart of the program. It identifies the indexes of the unique airports in the airports list it is handed in the air_codes_df.
        If the airport is not found, the length of the array which is to contain the indexes is zero; such indexes are dropped. If the array is longer than
        zero, meaning that two potential rows in airport_codes.csv share the same local code or the same iata_code, the user must manually decipher the appropriate index
        and input this. Otherwise, the index is assumed to be correct and appended to a list. A new data frame is initialized and the row
        of each index in this new index list is appended to the new data frame.

        Inputs:

        object -- air_codes_df: the data frame containing information from airport_codes.csv
        airports -- list: the list of unique airports from the travel file

        Returns:

            A csv file containing all information corresponding to unique airports in the travel file

    '''

    aircodes_indx_list = []

    for indx, airport in enumerate(airports):
        aircodes_indx_val = air_codes_df[(air_codes_df["local_code"] == airports[indx]) | (air_codes_df["iata_code"] == airports[indx])].index.values #checks
        #air_codes file to see if there are matches between it and any of the airports in the unique airports array for every airport in the
        #unique airports array

        aircodes_indx_val_as_list = aircodes_indx_val.tolist()

        if (len(aircodes_indx_val_as_list)) == 0: #removes empty entries from the aircodes_indx_val_as_list array
            del aircodes_indx_val_as_list

        elif (np.size(aircodes_indx_val_as_list)) >= 2: #if the length of an entry in the array is greater than one (meaning two indeces were identified), pick one
            correct_index = int(input(f'{aircodes_indx_val_as_list} These indeces represent rows in "airport_codes" that were identified by the program as corresponding\
            to origins in the business travel file you entered. Please review the airport_codes file and input the index of the correct origin '))
            aircodes_indx_val_as_list = [correct_index]
            aircodes_indx_list.append(aircodes_indx_val_as_list)

        else:
            aircodes_indx_list.append(aircodes_indx_val_as_list) #otherwise, keep the entry


    new_df = pd.DataFrame(index = np.arange(len(aircodes_indx_list)-1), columns=['','ident','type','name','elevation_ft','continent','iso_country',
    'iso_region', 'municipality', 'gps_code', 'iata_code', 'local_code', 'coordinates']) #creating a new data frame with the same strucutre as "airport_codes.csv"

    for code in range(0, len(aircodes_indx_list)-1):
        value = aircodes_indx_list[code][0] #value is an integer, it pulls an integer out of a list, code, within a larger list aircodes_indx_list
        row = (air_codes_df.iloc[[value]]) #pull out all information in the row with index "value"
        row_df = pd.DataFrame(row) #create a new dataframe for this new row
        row_df = row_df.reset_index()
        row_df.drop(row_df.columns[[0]], axis=1, inplace=True) #reset the index for this data frame to remove an additional column that pops up populated by "value"
        #row_df.to_csv("row2.csv")
        new_df.iloc[code] = row_df
    new_df.to_csv("modified_air_codes.csv", index = False) #create the new csv file without a standard index column starting at 0 


def main():

    air_codes_df = read_airport_codes("airport_codes.csv")
    travel_df = read_travel_file()
    airports = unique_airports(travel_df)
    modified_air_codes_df = create_modif_airport_codes(air_codes_df, airports)

main()
