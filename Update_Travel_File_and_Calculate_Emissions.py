'''
Author: Kyle Sprague
Date: 8/22/2022

The aim of this program is to calculate flight emissions. It does this by reading a busness travel file Excel sheet,
determining whether or not the airports listed in the business travel file sheet exists in a sheet with
airport information (including coordinates), and updating the airport information sheet "modified_air_codes.csv"
if an origin or destination airport is not included using airport_codes.csv. After all relevant information is
obtained, flight distances are calculated using a triple for loop and Numpy arrays; finally, these
distances are multiplied by the appropriate emissions factor to determine kgs of CO2 and tons of CO2 for
all flights.

'''

import pandas as pd
import numpy as np
import math

def read_travel_file() -> object:
    '''
    Function that reads the travel file it is given.
    Inputs:
        obj -- name: manually inputted travel file name
    Returns:
        a data frame containing information from the inputted excel file
    '''
    name = input("Please enter the full name of the travel file and .xlsx extension")
    #name = "JPM Airline Activity 7.1.2020 - 6.30.21 for Tom.xlsx"
    travel_file_df = pd.read_excel(name)
    return travel_file_df

def update_modified_aircodes_file(travel_df: object, modified_aircodes_file_df: object, air_codes_df: object) -> object:

    '''
        Function that updates the existing modified_air_codes.csv with any airports found in the travel file that do not
        currently exist in this file.

        Inputs:
            obj -- travel_df: the travel file's dataframe
            obj -- modified_air_codes_file_df: the modified_air_codes.csv data frame
            obj -- air_codes_df: the airport_codes.csv data frame with all international airports

        Returns:
            An updated data frame contianing all airports in the business travel file
    '''


    travel_array = pd.concat([travel_df['Origination'], travel_df['Destination']]).unique() #this creates an array of unique airports from the
    #"Origination" and "Destination" columns of the inputted travel file
    unique_trav_airports = [i for i in travel_array if i != '---']


    short_mod_trav_array = pd.concat([modified_aircodes_file_df['local_code'], modified_aircodes_file_df['iata_code']]).unique() #creates an array of unique
    #airports from the shortened version of the airport_codes.csv file modified_air_codes.csv, which only contains airports that Bates employees have
    #previously been to
    unique_mod_trav_airports = [i for i in short_mod_trav_array if i != '---'] #list comprehension to remove an airport deemed as unique that is
    #actually a blank entry; a precautionary measure in this case that will likely not be of issue

    missing_airports = [i for i in unique_trav_airports if i not in unique_mod_trav_airports]
    print(f'The missing airports include {missing_airports}. Note the index where each airport first occurs in the travel file in case of conflicts')
    #this will pull out any airprots that were in the new business travel file but not in the modified_air_codes.csv file

    if len(missing_airports) == 0: #Essentially this says that if no missing airports are identified, exit out of this function
        return modified_aircodes_file_df #added after file working

    else:

        rows_in_aircodes = []
        removal_list = []

        for index in range(0, len(missing_airports)):

            aircodes_indx_val = air_codes_df[(air_codes_df["local_code"] == missing_airports[index]) |
            (air_codes_df["iata_code"] == missing_airports[index])].index.values #get the index of the missing airport in airport_codes.csv's
            #data frame air_codes_df where there is a local_code OR iata_code match


            additional_indx_val = air_codes_df[(air_codes_df["local_code"] == missing_airports[index]) &
            (air_codes_df["iata_code"] == missing_airports[index])].index.values #get the index of the missing airport in airport_codes.csv's
            #data frame air_codes_df where there is a local_code AND an iata_code match

            com_aircodes_indx_val = np.concatenate((aircodes_indx_val, additional_indx_val)) #create a composite list of indeces in the
            #aircodes_df where missing indeces were found

            if len(com_aircodes_indx_val.copy()) == 0:
                removal_list.append(missing_airports[index]) #append to the removal list those airports in the travel file which could not be found
            if len(com_aircodes_indx_val.copy()) >= 2:
                print(f'Indeces to choose between are {com_aircodes_indx_val}')
                correct_index = int(input("Please enter the correct airport index in airport_codes.csv corresponding to the airport in missing airports "))
                rows_in_aircodes.append([correct_index]) #ask the user to manually input the index of the airport in airport_codes.csv (index, not row!) where
                #the correct missing airport has been identified. Recall that some airprots have the same iata_code or local_code and can therefore have
                #two indeces in airport codes
            else:
                rows_in_aircodes.append(com_aircodes_indx_val.tolist()) #if the length of the index list potential entry is one, append it as this
                #means there are no conflicts with regard to local/iata_code

        rows_in_aircodes_new = [i for i in rows_in_aircodes if i not in removal_list] #create a new list containing the rows of airports that could actually be found
        rows_in_aircodes_final = [i for i in rows_in_aircodes if i != []] #remove those airport entries that appear as [] in rows_in_aircodes_final
        print(rows_in_aircodes_final)


        new_df = pd.DataFrame()
        for indx in range(0, len(rows_in_aircodes_final)):

            row_df = air_codes_df.iloc[[rows_in_aircodes_final[indx][0]]]
            new_df = pd.concat([new_df, row_df]) #concatenate each row which could not be found initially in modified_air_codes.csv that contains an airport in the travel
            #file to a new data frame after it is found

        final_df = pd.concat([modified_aircodes_file_df, new_df]) #concatenate the new dataframe to the existing dataframe
        final_df.to_csv("modified_air_codes.csv", index = True, index_label = None) #replace modified_air_codes.csv wth the version containing new lines with new airports
        returned_df = pd.read_csv("modified_air_codes.csv", index_col = 0)
        return returned_df


################################################################################


def calculate_flight_distance(alt_travel_df -> object, short_air_df -> object) -> array:
    '''
        The purpose of this function is to find the coordinates of airports in the short_air_df where an airport matches one
        inside the alt_travel_df. After coordinates are found for the "Origination" and "Destination" airport, the Haversine formula
        for a spherical object is used to calculate travel distance.

        Inputs:
            obj -- alt_travel_df: the travel data frame with just the Origination and Destination columns of the travel file
            obj -- short_air_df: the newly updated airport information file with all relevant airports from the airport_codes.csv file

        Returns:
            An array of flight distances
    '''

    orig_arr = alt_travel_df["Origination"].to_numpy()
    dest_arr = alt_travel_df["Destination"].to_numpy()
    coord_arr = short_air_df["coordinates"].to_numpy()

    flight_distance_list = []
    for i in range(0, len(orig_arr)):
        origin_airport = orig_arr[i]
        dest_airport = dest_arr[i]
        #print(origin_airport) working
        #print(dest_airport) working
        #print(len(coord_arr))
        print(i)

        orig_lattitude = ""
        origin_longitude = ""
        dest_lattitude = ""
        dest_longitude = ""


        for j in range(0, len(coord_arr)):

            if (((origin_airport == short_air_df.at[j, "local_code"]) | (origin_airport == short_air_df.at[j, "iata_code"])) | (
            (origin_airport == short_air_df.at[j, "local_code"]) & (origin_airport == short_air_df.at[j, "iata_code"])
            )): #essentially, find where the airport in the origin array has a match in the short_air_df data frame
                o_row_of_interest = j #the row where the match occurs
                coordinate_set_1 = short_air_df.at[o_row_of_interest, "coordinates"] #the coordinates in the row where the match occurs
                o_comma_indx = coordinate_set_1.find(",")
                orig_lattitude = coordinate_set_1[0: o_comma_indx]
                orig_longitude = coordinate_set_1[o_comma_indx+1: (len(coordinate_set_1)+1)]
                #print(f"The origin lattitude is {orig_lattitude}")
                #print(f"The origin longitude is {orig_longitude}")
                #input()
                #print(coord_arr[index]) cx
                #print(f"The origin lattitude is {orig_lattitude}")
                #print(f"The origin longitude is {orig_longitude}")

                for k in range(0, len(coord_arr)): #now that we have moved through the origin column, we need to find out information
                #about the destination for the origin airport located at row j in the short_air_df; to do so, we employ a for loop
                #which enables us to keep the origin airport information while moving through the short_air_df to find a match for the
                #destination in the same row as the origin

                    if ((dest_airport == short_air_df.at[k, "local_code"]) | (dest_airport == short_air_df.at[k, "iata_code"])) | (
                    (dest_airport == short_air_df.at[k, "local_code"]) & (dest_airport == short_air_df.at[k, "iata_code"])
                    ): #essentially find where there is a match between the destination at row i in the travel file and
                    #the airport at row k in the short_air_df file

                        d_row_of_interest = k #the row where the match occurs
                        coordinate_set_2 = short_air_df.at[d_row_of_interest, "coordinates"] #coordinates in the row where the match occurs
                        d_comma_indx = coordinate_set_2.find(",")
                        dest_lattitude = coordinate_set_2[0: d_comma_indx]
                        dest_longitude = coordinate_set_2[d_comma_indx+1: (len(coordinate_set_2)+1)]
                        #print(f"The destination lattiude is {dest_lattitude}")
                        #print(f"The destination longitude is {dest_longitude}")


                        if ((orig_lattitude != "" and orig_longitude != "") or (dest_lattitude != "" and dest_longitude != "")) or (orig_lattitude != dest_lattitude):
                            #the purpose of this line is to not concern ourselves with cases where information can not be found about the airport at index i. This
                            #can happen if the airport is not in short_air_df because it was also not in airport_codes.csv or if the line is blank "---"

                            #print(orig_lattitude)
                            #print(orig_longitude)
                            #print(dest_lattitude)
                            #print(dest_longitude)

                            #working for test case on Esri https://community.esri.com/t5/coordinate-reference-systems-blog/distance-on-a-sphere-the-haversine-formula/ba-p/902128
                            #but their printed distance is incorrect

                            orig_latt_rad = np.radians(float(orig_lattitude)) #coordinates always come in degree pairs, so we must convert our data to radians
                            dest_latt_rad = np.radians(float(dest_lattitude))

                            delta_latt = np.radians(float(dest_lattitude) - float(orig_lattitude))
                            delta_long = np.radians(float(dest_longitude) - float(orig_longitude))
                            #Haversine Fomula link: https://www.movable-type.co.uk/scripts/latlong.html
                            a = np.sin(delta_latt / 2.0) ** 2 + np.cos(orig_latt_rad) * np.cos(dest_latt_rad) * np.sin(delta_long / 2.0) ** 2
                            print(a)
                            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
                            d = 6371*c #all calculations are about correct with variation due to formula used and also selection of earth radius size
                            print(d)
                            if d != 0.0:
                                d_miles = d/1.60934

                            #Alt choice would be to use Vincenty's formula (https://www.calculator.net/distance-calculator.html?type=3&la1=-0.116773&lo1=38.889931&la2=-77.009003&lo2=51.510357&ctype=dec&lad1=38&lam1=53&las1=51.36&lau1=n&lod1=77&lom1=2&los1=11.76&lou1=w&lad2=39&lam2=56&las2=58.56&lau2=n&lod2=75&lom2=9&los2=1.08&lou2=w&x=91&y=29#latlog);
                            #note that Haversine formula can be quite inaccurate for large distances

        flight_distance_list.append(d_miles)
        #print(flight_distance_list)

    return flight_distance_list

            #df.insert(0, "col0", pd.Series([5, 6], index=[1, 2]))

def calculate_emissions(travel_df, new_modified_aircodes_file_df):

    '''
        The goal of this function is to calculate emissions using the flight_distance list obtained from the calculate_flight_distance function;
        emissions factors are from the EPA and are in kg C02 per mile.

        Inputs:

        obj -- travel_df: the travel data from the travl file as a dataframe
        obj -- new_modified_aircodes_file_df: data frame contianing information from airport_codes.csv that was added to modified_air_codes.csv
        in the case where there were missing airports that occured in the travel file but not modified_air_codes.to_csv

        Returns:
            None; just prints kg CO2 for Bates 

    '''

    alt_travel_df = travel_df[["Origination", "Destination"]].copy().reset_index()
    alt_travel_df.to_csv("alt_travel_df.csv") #we have created a data frame with only the origin and destination colums from the travel file
    short_air_df = new_modified_aircodes_file_df[["local_code", "iata_code", "coordinates"]].copy().reset_index() #short_air_df is a truncated version of modified_air_codes.csv only containing relevant columsn
    short_air_df.to_csv("short_air_df.csv")
    flight_distance = calculate_flight_distance(alt_travel_df, short_air_df)

    #short haul: <300 miles 0.206kg CO2
    #Med haul: between 300 and 2300 miles 0.131kg CO2
    #long haul: >2300 miles 0.161 CO2
    kg_co2 = 0
    tons_co2 = 0
    for i in range(len(flight_distance)):
        if flight_distance[i] < 300:
            kg_co2 = kg_co2 + (flight_distance[i]*0.206)
        elif (flight_distance[i] >= 300) and (flight_distance[i] <2300):
            kg_co2 = kg_co2 + (flight_distance[i]*0.131)
        elif flight_distance[i] > 2300:
            kg_co2 = kg_co2 + (flight_distance[i]*0.161)

    print(f"total Bates CO2 is {kg_co2}kg")

def main():
    travel_df = read_travel_file()
    modified_aircodes_file_df = pd.read_csv("modified_air_codes.csv", index_col = 0)
    air_codes_df = pd.read_csv("airport_codes.csv")
    new_modified_aircodes_file_df = update_modified_aircodes_file(travel_df, modified_aircodes_file_df, air_codes_df)
    total_emissions = calculate_emissions(travel_df, new_modified_aircodes_file_df)
    print(total_emissions)

main()
