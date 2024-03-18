# import libraries
from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd
import numpy as np
import plotly.express as px
import random
import math

# initialize app
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet
app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app

# read CSV in and visually inspect
df = pd.read_csv('gdp_pcap.csv', low_memory=False)
df.head()

## some data cleaning
# I noticed that some rows have values in the thousands represented as *k, so wanted to convert to integers
# source: https://stackoverflow.com/questions/39684548/convert-the-string-2-90k-to-2900-or-5-2m-to-5200000-in-pandas-dataframe
def value_to_int(x):
    if type(x) == int:
        return x
    if 'k' in x:
        if '.' in x:    # I added this to account for decimal points
            x = x.replace('k','')
            vals = x.split('.')
            return int(vals[0]) * 1000 + int(vals[1]) * 100
        if len(x) > 1:
            return int(x.replace('k', '')) * 1000
        return 1000.0
    return int(x)

for col in df.columns[1:]:  # be sure to update all columns
    df[col] = df[col].apply(value_to_int)

df.head() # visually verify the data is clean

## Dropdown, slider div

##### Dropdown
# gather data for country, plus a random sampling to begin with
countries = df['country']
starting_countries = countries.sample(5)

# country div (dropdown, multiselect):
country_div = html.Div(children = [
    html.Label('Country'),
    dcc.Dropdown(
        id = 'country',
        options = countries,
        value =  starting_countries,
        multi = True # this makes dropdown multi-select
        )
], className = 'six columns')

##### Slider
# gather data for slider, plus random sample to begin with
years = (df.columns[1:].values).astype(int)
start = random.randint(0,math.floor(2*len(years)/3))
end = start + math.floor(len(years)/3)

# slider div
slider_div = html.Div([
    html.Label('Year(s)'),
    dcc.RangeSlider(
        id = 'year',
        min = years[0], 
        max = years[len(years)-1], 
        #step = 10, ## I commented out this line because there were too many ticks and it was unreadable
        value = [years[start], years[end]], #default values
        marks={i: '{}'.format(i) for i in range(years[0], years[len(years)-1], 25)},
        allowCross=False,
    ),
], className = 'six columns')

# add both divs to a mega-div for the controls:
control_div = html.Div([
    country_div,
    slider_div
], className = 'row')

## graph

# mini-fy df down to only include the countries we want to include
mini_df = df.loc[df['country'].isin(starting_countries)]

# plus remove columns for years we don't want
mini_df = mini_df.drop(mini_df.columns[1:start+1], axis=1)
mini_df = mini_df.drop(mini_df.columns[end-start+2:len(mini_df.columns)+1], axis=1)

# make it 'tidy' data so it can be easily graphed
melted_df = pd.melt(mini_df, id_vars=["country"], var_name="year")
melted_df['year'] = pd.to_numeric(melted_df['year'], errors='coerce')
melted_df['value'] = pd.to_numeric(melted_df['value'], errors='coerce')

# rename 'value' column to something meaningful
melted_df = melted_df.rename(columns={'value': 'gdp_pcap'})

# build the line chart
fig_line_marker = px.line(melted_df, 
                      x = 'year', 
                      y = 'gdp_pcap',
                      color = 'country',
                      markers = True,
                      symbol = 'country',
                      title = 'Year vs GDP per Capita by Country')

# define layout
graph_div = html.Div([
    dcc.Graph(
        figure = fig_line_marker, id='graph'
    ),
])

description_div = html.Div([
    html.H1("GDP per Capita of Various Countries by Year"),
    html.P(["This application allows a user to view and compare various countries GDP (per capita) dependant upon the year. ",
            html.A("The dataset",href='https://www.gapminder.org/gdp-per-capita/')," used is from gapminder, a Swedish organization \
            which Wikipedia describes as \"a non-profit venture registered in Stockholm, Sweden, that promotes sustainable global \
            development and achievement of the United Nations Millennium Development Goals by increased use and understanding of \
            statistics and other information about social, economic, and environmental development at local, national, and global levels.\" \
            This data was cleaned to fix number formatting and to display the values corresponding to the controls below, but is otherwise \
            unchanged. You can select different countries using the dropdown menu and/or select a different date range with the sliders."]),
    html.P(["A random selection of countries and years are initially set; feel free to adjust as you wish to explore different trends."])
], className = 'row')

## combine control div and graph div
app.layout = html.Div([
    description_div,
    control_div,
    graph_div

], className = 'row')

@callback(
        Output('graph', 'figure'),
        Input('country','value'),
        Input('year','value')
)
def update_graph(selected_countries, selected_years):
    # mini-fy df down to only include the countries we want to include
    mini_df = df.loc[df['country'].isin(selected_countries)]

    # plus remove columns for years we don't want
    small = selected_years[0] - years[0]
    big = selected_years[1] - years[0]
    mini_df = mini_df.drop(mini_df.columns[1:small+1], axis=1)
    mini_df = mini_df.drop(mini_df.columns[big-small+2:len(mini_df.columns)+1], axis=1)

    # make it 'tidy' data so it can be easily graphed
    melted_df = pd.melt(mini_df, id_vars=['country'], var_name="year")
    melted_df['year'] = pd.to_numeric(melted_df['year'], errors='coerce')
    melted_df['value'] = pd.to_numeric(melted_df['value'], errors='coerce')

    # rename 'value' column to something meaningful
    melted_df = melted_df.rename(columns={'value': 'gdp_pcap'})

    # build the line chart
    fig_line_marker = px.line(melted_df, 
                    x = 'year', 
                    y = 'gdp_pcap',
                    color = 'country',
                    markers = True,
                    symbol = 'country',
                    title = 'Year vs GDP per Capita by Country')
    return fig_line_marker


# run app in new tab - just for when developing to have it easier to see
if __name__ == '__main__':
    app.run(jupyter_mode='tab', debug=True)