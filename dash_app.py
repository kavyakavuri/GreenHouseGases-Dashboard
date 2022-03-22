from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

## Read data

df = pd.read_csv("./transformed_df_allsectors_filled.csv")
df.drop('Unnamed: 0',axis=1,inplace=True)

df_countries = pd.read_csv("./countries.csv")
df_countries.drop('Unnamed: 0',axis=1,inplace=True)

df_sunburst = pd.read_csv("./pie_chart_data.csv")
df_sunburst.drop('Unnamed: 0',axis=1,inplace=True)

def get_countries_options():
    global df_countries
    return list(df_countries.apply(lambda x: {"label": x[1],"value":x[0]},axis=1))



app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('GHG- A Global Perspective', className="app-header--title")
        ]
    ),
    html.Div([
        html.H1('GHG Emissions around the world'),
        dcc.Dropdown(id="slct_gas",
                     options=[
                         {"label": 'Carbon dioxide(CO2)', "value": 'Carbon dioxide(CO2)'},
                         {"label": 'Nitrous oxide(N2O)', "value": 'Nitrous oxide(N2O)'},
                         {"label": 'methane(CH4)', "value": 'methane(CH4)'},
                         {"label": 'All Gases', "value": 'GHG'}],
                     multi=False,
                     value='GHG',
                     # style={'width': "60%"}
                     ),
        dcc.Graph(id="choropleth_graph",figure={}),
        html.H1('Yearly Emissions (Thousand Metric Ton CO2eq)'),
        dcc.Dropdown(id="slct_country",
                     options=get_countries_options(),
                     multi=True,
                     value='USA',
                     ),
        dcc.Graph(id="country_line_chart",figure={}),
        html.H2("Sector Wise Emissions"),
        dcc.Graph(id="pie_chart",figure={}),
    ])
])

## Callback to update choropleth map according to gas selected
@app.callback(
    Output("choropleth_graph", "figure"), 
    Input("slct_gas", "value"))

def display_choropleth(gas_selected):
    global df
    # df = px.data.election() # replace with your own data source
    # geojson = px.data.election_geojson()
    df3 = df[df['Gas']==gas_selected].groupby(['CountryName','CountryCode']).mean()
    df3.reset_index( drop=False, inplace=True )
    df3.reindex(['CountryName','CountryCode','Year','LUCF','agriculture','allsectors',
                        'electricity and heat production','energy','gaseous fuel consumption',
                        'liquid fuel consumption','manufacturing industries and construction',
                        'other sectors, excluding residential buildings and commercial and public services',
                        'residential buildings and commercial and public services','solid fuel consumption','transport'], axis=1)

    fig = px.choropleth(df3, locations="CountryCode",
                    color="allsectors", # encode colors according to allsectors column
                    hover_name="CountryName", # column to add to hover information
                    hover_data = {
                    'CountryName':False,
                    'allsectors': True,
                    'CountryCode': False
                    },
                    color_continuous_scale=px.colors.sequential.Plasma, width=1800, height=900)
    fig.update_geos(projection_type="orthographic")
    fig.update_layout(clickmode='event+select')
    # fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    return fig


## Callback to update Line graphs according to country and gas selected
@app.callback(
    Output("country_line_chart", "figure"),
    [Input("slct_country", "value"),
    Input("slct_gas","value"),
    Input('choropleth_graph', 'selectedData')])

def update_line_chart(countries_selected,gas_selected, selected_data):
    global df
    # print("dcc data: ", dcc_data)
    # print("countries selected from choropleth: ",type(selected_data))
    
    if(type(countries_selected)!=list):
        countries_selected = [countries_selected]

    
    if(selected_data != None):
        for item in selected_data['points']:
            countries_selected.append(item['location'])

    
    mask = (df['CountryCode'].isin(countries_selected)) & (df['Gas']==gas_selected)
    fig = px.line(df[mask], x="Year", y="allsectors", color='CountryName',width=900, height=500)
    return fig

# @app.callback(
#     Output('dcc_store_countries_selected', 'data'),
#     [Input("slct_country", "value"),
#     Input('choropleth_graph', 'selectedData')])

# def update_store_data(countries_selected,selected_data):
#     print("updating data in dcc store")
#     if(type(countries_selected)!=list):
#         countries_selected = [countries_selected]

    
#     if(selected_data != None):
#         for item in selected_data['points']:
#             countries_selected.append(item['location'])

#     return {'countries':countries_selected}

@app.callback(
    Output('pie_chart','figure'),
    [Input("slct_country", "value"),
    Input('choropleth_graph', 'selectedData')])

def update_pie_chart(countries_selected,selected_data):
    global df_sunburst
    # print("calling pie chart thing")

    if(type(countries_selected)!=list):
        countries_selected = [countries_selected]

    
    if(selected_data != None):
        for item in selected_data['points']:
            countries_selected.append(item['location'])

    mask = df_sunburst['CountryCode'].isin(countries_selected)
    fig = px.sunburst(df_sunburst[mask], path=['CountryName', 'Gas', 'Sector'], values='Emissions', width=600, height=600)
    return fig





app.run_server(debug=True)