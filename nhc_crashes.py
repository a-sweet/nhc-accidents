import pandas as pd
import streamlit as st
import math
import numpy as np

st.title('Auto Accidents in New Haven County, CT')

st.markdown('Data obtained from [Connecticut Crash Data Repository](https://www.ctcrash.uconn.edu).')

st.markdown('---')

#Prevents loading the file every time the user interacts with widgets
@st.cache_data
def load_data():
    df = pd.read_csv('/Users/asweet/Desktop/NHC Crash Data/nhc_crashes.csv', parse_dates=['full_date'])
    indexed_df = df.set_index('full_date')
    return indexed_df

#load the dataset, parsing the date & time column as a date object
crashes = load_data()

#create the date range input slider
st.subheader('Dates')
d_range = st.date_input(
    "Date range",
    value = (crashes.index[0], crashes.index[-1]),
    min_value = crashes.index[0],
    max_value = crashes.index[-1])

#limit to the specified date range if it has a start and end
# if len(d_range) > 1:
#    crashes = crashes.loc[d_range[0]:d_range[1], :]

st.markdown('---')

#severity of accident set of checkboxes
st.subheader('Crash Severity')

injury_list = []
if st.checkbox('Property Damage Only', value=True):
    injury_list.append('Property Damage Only')
if st.checkbox('Injury of Any Type (Excluding Fatalities)', value=True):
    injury_list.append('Injury of any type (Serious, Minor, Possible)')
if st.checkbox('Fatality', value=True):
    injury_list.append('Fatal (Kill)')

#filter dataframe to contain only rows with the checked crash severities
crashes = crashes.loc[crashes['Crash Severity'].isin(injury_list)]

st.markdown('---')

#weather conditions set of checkboxes
st.subheader('Weather Conditions')
weather_list = []

col1, col2 = st.columns(2)

with col1:
    if st.checkbox('Clear', value=True):
        weather_list.append('Clear')
    if st.checkbox('Rain', value=True):
        weather_list.append('Rain')
    if st.checkbox('Cloudy', value=True):
        weather_list.append('Cloudy')
    if st.checkbox('Sleet or Hail ', value=True):
        weather_list.append('Sleet or Hail ')
    if st.checkbox('Snow', value=True):
        weather_list.append('Snow')
    if st.checkbox('Blowing Snow', value=True):
        weather_list.append('Blowing Snow')

with col2:
    if st.checkbox('Freezing Rain or Freezing Drizzle', value=True):
        weather_list.append('Freezing Rain or Freezing Drizzle')
    if st.checkbox('Fog, Smog, Smoke', value=True):
        weather_list.append('Fog, Smog, Smoke')
    if st.checkbox('Blowing Sand, Soil, Dirt', value=True):
        weather_list.append('Blowing Sand, Soil, Dirt')
    if st.checkbox('Severe Crosswinds', value=True):
        weather_list.append('Severe Crosswinds')
    if st.checkbox('Other', value=True):
        weather_list.append('Other')
    if st.checkbox('Unknown', value=True):
        weather_list.append('Unknown')

#filter dataframe to contain only rows with the checked weather conditions
crashes = crashes.loc[crashes['Weather Condition'].isin(weather_list)]

st.markdown('---')
#checkboxes for town in NHC
st.subheader('Towns')

col1, col2, col3 = st.columns(3)
#get the town names in the set
town_list = crashes['Town Name'].unique()
#sort them alphabetically
town_list.sort()

#split into three smaller lists to make the columns
list1, list2, list3 = np.array_split(town_list, 3)

chosen_towns = []

with col1:
    for town in list1:
        if st.checkbox(town, value=True):
            chosen_towns.append(town)

with col2:
    for town in list2:
        if st.checkbox(town, value=True):
            chosen_towns.append(town)

with col3:
    for town in list3:
        if st.checkbox(town, value=True):
            chosen_towns.append(town)

#filter dataframe to contain only records for chosen towns
crashes = crashes.loc[crashes['Town Name'].isin(chosen_towns)]

st.markdown('---')

#add the map last, so it is the last element of the page
st.subheader('Map')
st.map(crashes)

st.markdown('---')

st.subheader('Streets and Accidents Table')

#count accidents for each street name
street_list = crashes['Roadway Name'].unique()

#make new dataframe to store average daily traffic values, which change over time and are sometimes missing
# calculate the mean of the values present in the selected subset, and use this value for presenting data on 
# a given street
av_d_trf_df = pd.DataFrame()
d_trf_list = []
av_trf_dict = {}

for street in street_list:
  #calculate the mean of the daily traffic values, since it changes over time
  av_d_trf = crashes.loc[crashes['Roadway Name'] == street, ['Average Daily Traffic']].mean()[0]
  #print(f'Street: {street}, Av. Traffic: {av_d_trf}')
  #add to a dictionary with street name and calculated mean daily traffic unless trf is NaN 
  if math.isnan(av_d_trf) == False:
    av_trf_dict[street] = av_d_trf

#count accidents, make a dataframe
dangerous_streets = crashes.groupby(['Roadway Name','Route Class','Town Name'])['Roadway Name'].count().to_frame()

#convert the extra index from groupby to a column
dangerous_streets.reset_index(level=['Route Class', 'Town Name'], inplace=True)

#remove the name label from the index
dangerous_streets.index.name = None

#rename the columns to reflect their actual data: 
dangerous_streets.rename(columns = {'Roadway Name':'Number of Accidents','Route Class':'Road Type'}, inplace=True)

#add a new column to the dataframe with values from the dictionary (df index and dict keys are both street names)
dangerous_streets['Average Daily Vehicles'] = dangerous_streets.index.map(av_trf_dict)
dangerous_streets['Average Daily Vehicles'] = round(dangerous_streets['Average Daily Vehicles'], 2)

dangerous_streets['Accidents per 1000 ADV'] = round(dangerous_streets['Number of Accidents'] / (dangerous_streets['Average Daily Vehicles'] / 1000), 2)


st.dataframe(dangerous_streets, height = 200)

st.write("*Average Daily Vehicles values of 'None' or '<NA>' mean there is no data for that street in the chosen date range.")


