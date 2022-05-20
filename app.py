from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from raceplotly.plots import barplot
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import numpy as np
import dash_daq as daq


external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap',
     dbc.themes.BOOTSTRAP
]


app = Dash(__name__,external_stylesheets=external_stylesheets)




## READ DATA

df_final = pd.read_csv("./df_final.csv")

df_countries = pd.read_csv("./countries.csv")

#TODO: Make this Dynamic
top_10_polluters = ['United States', 'China', 'Russian Federation', 'India', 'Japan', 'United Kingdom', 'Canada', 'Brazil', 'Germany', 'France']

#TODO: Add more dark colors
all_colors = ['#1f77b4','#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
np.random.shuffle(all_colors)






## STATIC PLOTS

def get_countries_options():
    global df_countries
    return list(df_countries.apply(lambda x: {"label": x[1],"value":x[0]},axis=1))

def display_raceplot():
    global df_final
    df = df_final[df_final['predicted']=='No']
    race_df = df.groupby(['CountryName','CountryCode','Year']).sum()
    race_df.reset_index( drop=False, inplace=True )
    race_df.reindex(['CountryName','CountryCode','Year','LUCF','agriculture','allsectors',
        'electricity and heat production','energy','gaseous fuel consumption','liquid fuel consumption',
        'manufacturing industries and construction','other sectors, excluding residential buildings and commercial and public services',
        'residential buildings and commercial and public services','solid fuel consumption','transport'], axis=1)
    my_raceplot = barplot(race_df,  item_column='CountryName', value_column='allsectors', time_column='Year')
    fig = my_raceplot.plot(item_label = 'Top 10 countries', value_label = 'Emissions (tonnes)', frame_duration = 800)
    fig.update_layout(height=700)
    return fig

def display_red_grey_pie_chart():
    global df_final
    global top_10_polluters
    df_copy = df_final[df_final['predicted']=='No'].copy()
    df_copy.drop(['LUCF','allsectors','predicted'],axis=1,inplace=True)
    df_pie = df_copy.melt(id_vars=['Region','CountryName','CountryCode','Year','Gas'], var_name='Sector', value_name='Emissions')

    # top_10_polluters = df_pie.groupby(['CountryName','CountryCode']).sum().reset_index().nlargest(10,'Emissions')['CountryName'].tolist()
    colormap = {}
    for country in df_pie['CountryName'].unique().tolist():
      colormap[country] = 'grey'
    for country in top_10_polluters:
      colormap[country] = 'red'
    fig = px.sunburst(df_pie, path=['CountryName'], values='Emissions', color='CountryName',color_discrete_map=colormap, height=600, width=600)
    return fig

def display_area_graphs():
    global df_final
    global top_10_polluters

    df = df_final[df_final['predicted']=='No'].copy()

    fig = make_subplots(
        rows=2, cols=5,
        subplot_titles=(top_10_polluters))
    count =0
    for r in range(1,3):
      for c in range(1,6):
        # print(count,r,c)
        tempdf = df[df['CountryName']==top_10_polluters[count]].groupby(['Year']).sum().reset_index()
        X = tempdf['Year'].to_list()
        Y = tempdf['allsectors'].to_list()
        fig.add_trace(go.Scatter(x=X,y=Y,fill='tozeroy',showlegend=False),row=r,col=c)
        count +=1
    return fig

def get_interesting_facts():
    facts = ["TWO THIRDS of the global emissions are just from the top 10 global emitters!",
    "Carbon Dioxide(CO2) is the most emitted greenhouse gas accounting for about 74 % of the total \
                            GHG emissions followed by Methane(CH4) and Nitrous oxide(N20) with 7% and 17% of the total GHG emissions respectively",
                            "As of 2016, Energy Consumption is the largest contributing sector to the overall GHG emissions, accounting for about 75% of the total emissions",
                            "As of the year 2016, China is the largest contributor to the GHG emissions with about 13.918 Giga Ton CO2 eq of the total emissions",
                            "As of the year 2012, the total GHG emissions across the world has been about 52.56 Giga ton CO2 equivalent.",
                            "Fuel Combustion is the largest contributor of GHG emissions in USA, accounting for about 74% of the total emission levels"]

    return [html.Li(fact,style={'font-size':20,'font-weight': 'bold','color': '#0E5D12'}) for fact in facts]

def display_treemap():
    global df_final
    fig = px.treemap(df_final, path=[px.Constant("world"), 'Region', 'CountryName'], values='allsectors',
                  color='Region', hover_data=['Region'],
                  color_continuous_scale='RdBu',)
                  
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    return fig

def get_marks():
    marks = {}
    for x in range(1960,2040,4):
        marks[x] = str(x)
    return marks





## MAIN APP LAYOUT 
app.layout = html.Div([
    
     dbc.NavbarSimple(
        children=[
            dbc.Col(
                    html.Div(html.A("GHG- A Global Perspective",href="#",style={'text-decoration':'none','color':'white'}),id="top",style={'align':'left','font-size':'40px','font-family': 'Archivo Black,sans-serif','margin-left':'-250px', 'width':'800px'})
                )
                ,
            dbc.Col(
                    dbc.Button(html.A("Yearly Emissions",href="#choropleth_text",style={'text-decoration':'none','color':'white'}),style={'align':'right','width':'200px','margin-top':'20px','margin-left':'130px','font-weight':'bold'},color="white", className="me-1")
                )
                ,
            dbc.Col(
                    dbc.Button(html.A("Top 10 pollutors", href="#br1", style={'text-decoration':'none','color':'white'}),style={'align':'right','width':'200px','margin-top':'20px','margin-left':'-50px','font-weight':'bold'},color="white", className="me-1")
                ),
            dbc.Col(
                    dbc.Button(html.A("Treemap for regions", href="#treemapbr", style={'text-decoration':'none','color':'white'}),style={'align':'right','width':'200px','margin-top':'20px','margin-left':'-50px','font-weight':'bold'},color="white", className="me-1")
                    ),
            dbc.Col(
                    dbc.Button(html.A("Interesting Facts", href="#interesting_factsbr", style={'text-decoration':'none','color':'white'}),style={'align':'right','width':'200px','margin-top':'20px','margin-left':'-50px','font-weight':'bold'},color="white", className="me-1")
                    
                ),
            dbc.Col(
                    dbc.Button(html.A("Carbon Footprint", href="#carbon_footprint", style={'text-decoration':'none','color':'white'}),style={'align':'right','width':'200px','margin-top':'20px','margin-left':'-50px','font-weight':'bold'},color="white", className="me-1")
                    
                )
            
        ],
        brand_href="#",
        color='#0E5D12',
        light=True,
        sticky ='top',
    ),
    
    html.Br(),
    
    html.Div([
        
        
        dbc.Row(dbc.Col(dcc.Dropdown(id="slct_gas",
                     options=[
                         {"label": 'Carbon dioxide(CO2)', "value": 'Carbon dioxide(CO2)'},
                         {"label": 'Nitrous oxide(N2O)', "value": 'Nitrous oxide(N2O)'},
                         {"label": 'methane(CH4)', "value": 'methane(CH4)'},
                         {"label": 'All Gases', "value": 'GHG'}],
                     multi=False,
                     value='GHG',
                     # style={'width': "60%"}
                     ),
                    width={'size': 6, 'offset': 3},
                ),
        ),
        dcc.Graph(id="choropleth_graph",figure={}),
        dcc.RangeSlider(1960, 2040, 4, 
            id='year_range_slider',
            marks=get_marks(),
            value=[1970, 2020],  
            tooltip={"placement": "bottom", "always_visible": True}),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2('Summary of choropleth graph:',style={'color': 'white','background': '#0e5d12','border': '1px solid #fff','border-radius': '0 10px 0 10px','padding': '5px 15px'}),
        html.P(id='choropleth_text',children=[],style={'padding-left': '10px','color': '#0E5D12','font-size':20,'font-weight': 'bold'}),
        html.Br(),
        html.H2('Yearly Emissions (Thousand Metric Ton CO2eq)'),
        dbc.Row(
            [  
                dbc.Col(dcc.Dropdown(id="slct_country",
                             options=get_countries_options(),
                             multi=True,
                             value=['USA','CHN','IND'],
                             ),
                        width={'size':6},
                ),
                dbc.Col(html.H3("Emissions by Sector"), width={'size':5}, style={'text-align':'right','margin-left':'800px','z-index':'6'}),
            ],
        ),
        html.Div(id='line_plus_sunburst',children=[
            dcc.Graph(id="country_line_chart",figure={},style={'display': 'inline-block'}),
            dcc.Graph(id="sunburst_chart",figure={},style={'display': 'inline-block','position':'absolute','margin-top':'-20px','margin-left':'200px'})
        ]),
        html.Br(id='br1'),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2("An overview of top 10 polluter countries",id='top10overview'),
        dcc.Graph(id="area_graphs",figure=display_area_graphs()),
        html.P(id="area_curve_text",children="All the countries are showing an increasing trend except the top polluters of EU, i.e., United Kingdom, Germany, France.",style={'padding-left': '10px','color': '#0E5D12','font-size':20,'font-weight': 'bold'}),
        html.H2("Racing Bar graph of Top 10 Countries",id="top10_race_plot"),
        dcc.Graph(id="raceplot",figure=display_raceplot()),
        html.Br(id='treemapbr'),
        html.Br(),
        html.Br(),
        html.H2('Treemap showing total emissions by regions',id="treemap_h3"),
        dcc.Graph(id="treemap",figure=display_treemap()),
        html.Br(id='interesting_factsbr'),
        html.Br(),
        html.Br(),
        html.H2("Interesting Facts", id='interesting_facts'),
        dbc.Row(dbc.Col(dcc.Graph(id="pie_chart_red_grey",figure=display_red_grey_pie_chart()),width={'size': 6, 'offset': 3},
            ),
        ),
        html.Ul(id="interesting_facts_list",children=get_interesting_facts()),
        html.Br(id="carbon_footprint"),
        html.H2('Carbon Footprint Calculator'),
        html.Div(children=[
            dbc.Row([
                dbc.Col(html.P(children=["Your Monthly Electricity Bill:"],style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.Input(
                    id='electricity_bill',
                    type='number',
                    placeholder='monthly electricity bill($)',
                    style={'display': 'inline-block', 'verticalAlign': 'top','font-weight':'bold'},
                ),width={'size': 4}),
            ]),
            dbc.Row([
                dbc.Col(html.P(["Your Monthly Gas Bill:"],style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.Input(
                    id='gas_bill',
                    type='number',
                    placeholder='monthly gas bill($)',
                    # rows=1,
                    style={'display': 'inline-block', 'verticalAlign': 'top','font-weight':'bold'},
                ),width={'size': 4})
            ]),
            dbc.Row([
                dbc.Col(html.P(["Your Monthly Oil bill:"],style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.Input(
                    id='oil_bill',
                    type='number',
                    placeholder='monthly oil bill($)',
                    style={'display': 'inline-block', 'verticalAlign': 'top','font-weight':'bold'},
                ),width={'size': 4}),
            ]),
            dbc.Row([
                dbc.Col(html.P(["Yearly Mileage on your Car:"],style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.Input(
                    id='mileage',
                    type='number',
                    placeholder='mileage on your car(miles)',
                    style={'display': 'inline-block', 'verticalAlign': 'top','font-weight':'bold'},
                ),width={'size': 4}),
            ]),
            dbc.Row([
                dbc.Col(html.P(["Number of Flights(<4 hours duration) you have taken in the past year:"],style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.Input(
                    id='flights_short',
                    type='number',
                    placeholder='no. of flights taken(<4h)',
                    style={'display': 'inline-block', 'verticalAlign': 'top', 'font-weight':'bold'},
                ),width={'size': 4}),
            ]),
            dbc.Row([
                dbc.Col(html.P(["Number of Flights(>4 hours duration) you have taken in the past year:"],style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.Input(
                    id='flights_long',
                    type='number',
                    placeholder='no. of flights taken(>4h)',
                    style={'display': 'inline-block', 'verticalAlign': 'top','font-weight':'bold'},
                ),width={'size': 4}),
            ]),
            dbc.Row([
                dbc.Col(html.P("Do you recycle paper?",style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.RadioItems(id="recycle_paper",options=['Yes','No'],value='No', inline=True),width={'size': 2}),
            ]),
            dbc.Row([
                dbc.Col(html.P("Do you recycle aluminium and tin",style={'padding-left': '10px','font-weight':'bold'}),width={'size':2}),
                dbc.Col(dcc.RadioItems(id="recycle_metal",options=['Yes','No'],value='No', inline=True),width={'size': 2}),
            ]),
            dbc.Row([
            dbc.Col(html.Button('Calculate My Carbon Footprint!', id='submit-val', n_clicks=0,style={'padding-left': '10px'}),width={'size':2,'offset':1}),
            ]),
            html.Div(id="carbon_foot_print_result",children=["Enter your values and press the button!"],style={'padding-left': '10px','font-size': 20,'font-weight':'bold'}),
            html.Div([daq.Gauge(
                    id='guage_indicator',
                    color={"gradient":True,"ranges":{"green":[0,15999],"yellow":[15999,22000],"red":[22000,40000]}},
                    value=20000,
                    label='Carbon Footprint Indicator',
                    max=40000,
                    min=0,
                ),
            ]),
            html.Div(["6,000 to 15,999 pounds per year is considered as low carbon footprint, 16,000-22,000 pounds per year is considered average. Above 22,000 pounds per year is very high and you need to change your lifestyle!"],style={'padding-left': '10px','font-size': 20,'font-weight':'normal'}),
            html.Br(),
            html.Br(),
        ]),

    ])
])






## ALL CALLBACKS
## Callback to update choropleth map according to gas selected
@app.callback(
    [Output("choropleth_graph", "figure"),Output("choropleth_text","children")], 
    [Input("slct_gas", "value"),
    Input("year_range_slider","value")])

def display_choropleth(gas_selected,year_range):
    global df_final
    
    df3 = df_final[(df_final['Gas']==gas_selected)&(df_final['Year']>=year_range[0])&(df_final['Year']<=year_range[1])].groupby(['CountryName','CountryCode']).mean().reset_index()

    fig = px.choropleth(df3, locations="CountryCode",
                    color="allsectors", # encode colors according to allsectors column
                    hover_name="CountryName", # column to add to hover information
                    hover_data = {
                        'CountryName':False,
                        'allsectors': True,
                        'CountryCode': False
                    },
                    color_continuous_scale='RdYlGn_r', width=1800, height=900)
    fig.update_layout(clickmode='event+select')

    highest_emitter_df = df3.nlargest(1,'allsectors')
    highest_country_name = "no country"
    highest_emission = 0
    percentage_share = 0

    if(highest_emitter_df.shape[0]!=0):
        highest_country_name = highest_emitter_df['CountryName'].to_list()[0]
        highest_emission = np.format_float_positional(highest_emitter_df['allsectors'].to_list()[0]/1000000, precision=3)
        percentage_share = np.format_float_positional(highest_emitter_df['allsectors'].to_list()[0]/df3['allsectors'].mean(),precision=3)
    
    lowest_emitter_df = df3.nsmallest(1,'allsectors')
    lowest_country_name = "no country"
    lowest_emission = 0
    if(lowest_emitter_df.shape[0]!=0):
        lowest_country_name = lowest_emitter_df['CountryName'].to_list()[0]
        lowest_emission = np.format_float_positional(lowest_emitter_df['allsectors'].to_list()[0],precision=3)

    
    mean = np.format_float_positional(df3['allsectors'].mean()/1000000,precision=3)

    text = ["Between year ",year_range[0] ," and " ,year_range[1]," the top polluter is ",highest_country_name, ", with an average emission of ", 
    highest_emission," Giga Ton CO2eq contributing to ",percentage_share,"%"," of the total emissions. On the other side, the least polluting country is ",lowest_country_name," and the average amount of gaseous emissions is ", 
    lowest_emission, " Kilo Ton CO2eq. On an average the value of emissions per country is ", mean," Giga Ton CO2eq."]
    
    return fig, text


## Callback to update Line graphs according to country and gas selected
@app.callback(
    Output("country_line_chart", "figure"),
    [Input("slct_country", "value"),
    Input("slct_gas","value"),
    Input('choropleth_graph', 'selectedData'),
    Input("year_range_slider","value")])

def update_line_chart(countries_selected,gas_selected, selected_data,year_range):
    global df_final
    
    if(type(countries_selected)!=list):
        countries_selected = [countries_selected]

    
    if(selected_data != None):
        for item in selected_data['points']:
            countries_selected.append(item['location'])
    
    
    mask2 = (df_final['CountryCode'].isin(countries_selected)) & (df_final['Gas']==gas_selected) & (df_final['Year']>=year_range[0]) & (df_final['Year']<=year_range[1])
    
    trimmed_df = df_final[mask2]
    fig = go.Figure()
    # line plots
    actual_df = trimmed_df[trimmed_df['predicted']=='No']
    if(actual_df.shape[0]>0):
        for i in range(len(countries_selected)):
            tempdf = actual_df[actual_df['CountryCode']==countries_selected[i]]
            Y = tempdf['allsectors'].to_list()
            X = tempdf['Year'].to_list()
            country_name = tempdf['CountryName'].to_list()[0]
            fig.add_trace(go.Scatter(x=X, y=Y, name=country_name,line=dict(color=all_colors[i])))

    #dotted lines
    predicted_df = trimmed_df[trimmed_df['predicted']=='Yes']
    if(predicted_df.shape[0]>0):
        for i in range(len(countries_selected)):
            tempdf = predicted_df[predicted_df['CountryCode']==countries_selected[i]]
            Y = tempdf['allsectors'].to_list()
            X = tempdf['Year'].to_list()
            country_name = tempdf['CountryName'].to_list()[0]
            fig.add_trace(go.Scatter(x=X, y=Y, name=country_name,line=dict(color=all_colors[i],dash='dash')))

    fig.update_layout(height=600,width=1000)
   

    return fig


# Callback to update Sunburst chart
@app.callback(
    Output('sunburst_chart','figure'),
    [Input("slct_country", "value"),
    Input('choropleth_graph', 'selectedData'),
    Input("year_range_slider","value")])

def update_sunburst_chart(countries_selected,selected_data,year_range):
    global df_final

    df_copy = df_final.copy()
    df_copy.drop(['LUCF','allsectors','predicted'],axis=1,inplace=True)
    df_pie = df_copy.melt(id_vars=['Region','CountryName','CountryCode','Year','Gas'], var_name='Sector', value_name='Emissions')
    # print("calling pie chart thing")

    if(type(countries_selected)!=list):
        countries_selected = [countries_selected]

    
    if(selected_data != None):
        for item in selected_data['points']:
            countries_selected.append(item['location'])

    mask = df_pie['CountryCode'].isin(countries_selected) & (df_pie['Year']>=year_range[0]) & (df_pie['Year']<=year_range[1])
    fig = px.sunburst(df_pie[mask], 
                        path=['Region','CountryName', 'Gas', 'Sector'], 
                        values='Emissions',
                        color_continuous_scale=all_colors,#px.colors.sequential.algae,
                        width=650, 
                        height=650)
    text = {'family':'Times New Roman','size':15,'color':'black'}
    fig.update_traces(textinfo="label+percent root")
    fig.update_layout(font=text)
    return fig


# Callback to update Guage Indicator
@app.callback(
    [Output('carbon_foot_print_result','children'),Output('guage_indicator', 'value')],
    Input('submit-val','n_clicks'),
    [State('electricity_bill','value'),State('gas_bill','value'),
    State('oil_bill','value'),State('mileage','value'),
    State('flights_short','value'),State('flights_long','value'),
    State('recycle_paper','value'),State('recycle_metal','value')])

def calculate_carbon_footprint(n_clicks,electricity_bill,gas_bill,oil_bill,mileage,flights_short,flights_long,recycle_paper,recycle_metal):
    cp=0.0
    if(n_clicks>0):
        cp += (electricity_bill+ gas_bill)*105 
        cp+= oil_bill*113 
        cp+= mileage*0.79 
        cp+= flights_short*1100 
        cp+= flights_long*4400

        if(recycle_paper=='No'):
            cp += 184
        if(recycle_metal=='No'):
            cp += 166
        # print("cp: ",cp)
        indicator = cp
        if(cp>40000):
            indicator = 40000
        return "your carbon footprint is: "+str(cp) + " pounds per year",indicator
    return "Enter your values and press the button!",20000

app.run_server(debug=True)
