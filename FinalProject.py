import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, tight_layout, xticks, subplots, title, pie
import numpy as np
import streamlit as st
import pydeck as pdk

#st config
st.set_page_config(page_title="Skyscraper Visualization with Python",
                   page_icon=":bar_chart:")

#default values
default_city = ["Las Vegas", "Boston", "Miami"]
default_height = 200
default_year = 1950

#read in data
def read_data():
    #read the CSV file and set the index
    df = pd.read_csv("skyscrapers.csv").set_index("id")
    #filter out rows where 'status.completed.year' is 0 or less and messed up values for lat
    df = df[df['status.completed.year'] > 0]
    df = df[df['latitude'] > 0]
    return df


#filter the data
def filter_data(sel_city, max_height, min_year):
    df = read_data()
    df = df.loc[df['location.city'].isin(sel_city)]
    df = df.loc[df['statistics.height'] > max_height]
    df = df.loc[df['status.completed.year'] > min_year]

    return df

#unique cities function
def all_cities():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['location.city'] not in lst:
            lst.append(row['location.city'])

    return lst

#data = filter_data(default_city, default_height, default_year)
#print(data)

#count the frequency of cities
def count_cities(cities, df):
    #return a list of skyscraper counts for each selected city
    return [df.loc[df["location.city"].isin([city])].shape[0] for city in cities]

#extract the heights of skyscrapers by city
def skyscraper_heights(df):
    heights = [row["statistics.height"] for ind, row in df.iterrows()]
    skyscrapers = [row["location.city"] for ind, row in df.iterrows()]

    dict = {}
    for skyscraper in skyscrapers:
        dict[skyscraper] = []

    #append heights to the respective city
    for i in range(len(heights)):
        dict[skyscrapers[i]].append(heights[i])

    return dict

#calculate the average height of skyscrapers by city
def skyscraper_averages(dict_heights):
    dict = {}
    for key in dict_heights.keys():
        dict[key] = np.mean(dict_heights[key])

    return (dict)


#pie chart
def generate_pie_chart(counts, sel_cities):
    if len(counts) == 0:
        st.warning("No data available for the selected criteria.")
        return

    figure()
    #blow out the city with the highest skyscraper count
    explodes = [0 for i in range(len(counts))]
    if len(counts) > 0:
        maximum = counts.index(np.max(counts))
        explodes[maximum] = 0.25
    #create pie chart
    pie(counts, labels=sel_cities, explode=explodes, autopct="%.2f")
    title(f"Skyscraper Distribution: {', '.join(sel_cities)}")

    return plt

#bar chat
def generate_bar_chart(dict_averages):
    figure()
    x = list(dict_averages.keys())
    y = list(dict_averages.values())

    # create bar chart
    fig, ax = subplots()
    ax.bar(x, y, color='skyblue')
    ax.set_xlabel("Cities")
    ax.set_ylabel("Average Height (ft)")
    ax.set_title("Average Heights of Skyscrapers by City")

    #rotate the x-axis labels
    xticks(rotation=45)

    return plt

#map diagram
def generate_map(df):
    #filter the dataframe to include only relevant columns and drop rows with missing latitude or longitude
    map_df = df[['location.city', 'latitude', 'longitude', 'name']].dropna(subset=['latitude', 'longitude'])

    #ensure there is valid data for the map
    if map_df.empty:
        st.write("No valid data for selected cities.")
        return

    #center the map around the mean latitude and longitude of the filtered data
    view_state = pdk.ViewState(
        latitude=map_df['latitude'].mean(),
        longitude=map_df['longitude'].mean(),
        zoom=4,  #default zoom level, can be adjusted based on the number of cities
        pitch=0  #flat view
    )

    #define the custom icon
    icon_url = "https://i.postimg.cc/XvLxzctB/5776223.png"
    map_df['icon_data'] = [{
        "url": icon_url,
        "width": 128,
        "height": 128,
        "anchorY": 128,
    }] * len(map_df)

    #create the custom icon
    icon_layer = pdk.Layer(
        "IconLayer",
        data=map_df,
        get_icon="icon_data",
        get_size=4,  # adjust size scaling
        size_scale=10,  #scale factor for the size
        get_position='[longitude, latitude]',  #position based on longitude and latitude
        pickable=True  # allows interaction with the icons
    )

    #set up the map using Deck with a map style and layers
    map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",  #using the 'light' map style for clarity
        initial_view_state=view_state,
        layers=[icon_layer],  #use the IconLayer
        tooltip={"html": "<b>{name}</b>", "style": {"backgroundColor": "steelblue", "color": "white"}}  # Tooltip showing the city name
    )

    #display the map in Streamlit
    st.pydeck_chart(map)

#compare graphs
def compare_graphs(data, city):
    #filter the data for the selected city
    city_data = data[data['location.city'] == city]

    #ensure data for the selected city
    if city_data.empty:
        st.write(f"No data available for {city}.")
        return

    #get the top 5 tallest skyscrapers (sorted by height, descending)
    tallest_skyscrapers = city_data[['name', 'statistics.height']].sort_values(by='statistics.height',
                                                                                ascending=False).head(5)

    #get the top 5 shortest skyscrapers (sorted by height, ascending)
    shortest_skyscrapers = city_data[['name', 'statistics.height']].sort_values(by='statistics.height',
                                                                                ascending=True).head(5)

    #Create two subplots for the bar charts in a vertical arrangement
    chart, (ax1, ax2) = subplots(2, 1, figsize=(12, 10))  # 2 rows, 1 column layout

    #plot the 5 tallest skyscrapers
    ax1.barh(tallest_skyscrapers['name'], tallest_skyscrapers['statistics.height'], color='blue')
    ax1.set_title(f"5 Tallest Skyscrapers in {city}")
    ax1.set_xlabel("Height (ft)")
    ax1.set_ylabel("Skyscraper Name")

    #Rotate y-axis labels for readability
    ax1.tick_params(axis='y', labelrotation=45)

    #Plot the 5 shortest skyscrapers
    ax2.barh(shortest_skyscrapers['name'], shortest_skyscrapers['statistics.height'], color='red')
    ax2.set_title(f"5 Shortest Skyscrapers in {city}")
    ax2.set_xlabel("Height (ft)")
    ax2.set_ylabel("Skyscraper Name")

    #Rotate y-axis labels for readability
    ax2.tick_params(axis='y', labelrotation=45)

    #adjust spacing between the plots
    tight_layout()

    #display the graphs
    st.pyplot(chart)


def main():
    st.title("Data Visualization with Python")
    st.write("Welcome to this Skyscraper Data! Open the sidebar to begin.")

    #city selection in sidebar
    st.sidebar.write("Please choose your city to display data.")
    cities = st.sidebar.multiselect(
        "Select a city:",
        all_cities(),
        default=["Las Vegas"]  # defualt to Las Vegas
    )

    #filter the data based on selected cities
    df = read_data()
    filtered_df = df[df['location.city'].isin(cities)]

    #fynamically set the max height slider based on the selected cities
    if not filtered_df.empty:
        max_sky_scraper_height = int(filtered_df['statistics.height'].max())  #cast to int to match slider type
        min_year_completed = int(filtered_df['status.completed.year'].min())  #min year for the selected cities
        max_year_completed = int(filtered_df['status.completed.year'].max())  #max year for the selected cities
    else:
        max_sky_scraper_height = 600  #defualt if no data for selected cities
        min_year_completed = 1900  #defualt min year
        max_year_completed = 2024  #defualt max year

    #sliders for filtering data by height and year
    max_height = st.sidebar.slider(
        "Max Height: ",
        0,
        max_sky_scraper_height,
        step=1  #ensure the step value is integer
    )
    min_year = st.sidebar.slider(
        "Minimum Year Completed: ",
        min_year_completed,
        max_year_completed,
        step=1  #ensure the step value is integer
    )

    #filter data based on user selections
    data = filter_data(cities, max_height, min_year)

    #check if data is valid after filtering
    if data.empty:
        st.write("No valid data available for the selected parameters.")
    else:
        #get count of skyscrapers per city for pie chart
        series = count_cities(cities, data)

        #display map of skyscrapers
        st.write("View a map of skyscrapers")
        generate_map(data)

        #display pie chart
        st.write("View a pie chart")
        st.pyplot(generate_pie_chart(series, cities))

        #display bar chart
        st.write("View a bar chart")
        st.pyplot(generate_bar_chart(skyscraper_averages(skyscraper_heights(data))))

        selected_city = cities[0]  #use the first city from the selected cities list
        st.write(f"Compare the 5 Tallest and 5 Shortest Skyscrapers in {selected_city}")
        compare_graphs(data, selected_city)

        #display the filtered dataframe
        st.write("View the filtered dataframe")
        filtered_columns = data[['name', 'location.city', 'status.completed.year']]
        st.dataframe(filtered_columns, height=750)

        #display the top 5 tallest skyscrapers of all time
        st.write("View the 5 Tallest Skyscrapers of All Time (completed)")
        data = read_data()
        tallest_skyscrapers = data[['name', 'location.city', 'statistics.height']].sort_values(by='statistics.height', ascending=False).head(5)
        st.dataframe(tallest_skyscrapers)

main()



