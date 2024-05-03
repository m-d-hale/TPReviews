# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Load data
############################################
df = pd.read_csv('sentimentdata.csv')

#Rearrange cols
col_order = ['ReviewNum',  'Brand', 'Experience_Date', 'Review_Title', 'Review_Stars', 'TitleAndReview_Sentiment',
                 'Num_Of_Reviews', 'Review_Type','Review_TitleAndText']

df2 = df.reindex(columns=col_order)

#Get min max posted date
#MinPosted_DateTime = df['Posted_DateTime'].min()
MinPosted_DateTime = datetime.strptime(df['Posted_DateTime'].min(), "%Y-%m-%d %H:%M:%S%z").date().strftime("%Y-%m-%d")
MaxPosted_DateTime = datetime.strptime(df['Posted_DateTime'].max(), "%Y-%m-%d %H:%M:%S%z").date().strftime("%Y-%m-%d")

# Initialize the app - incorporate a Dash Bootstrap theme
############################################
external_stylesheets = [dbc.themes.CYBORG]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Define App layout
############################################

app.layout = html.Div(style={'backgroundColor': '#060606'}, children=[
    dbc.Container([
        #Title
        dbc.Row([
            html.Div('TrustPilot Reviews / Sentiment Analysis', className="text-left fs-4", style={'color': 'white'})
        ]),
        
        #Subtitle - Min and max posted date
        dbc.Row([
            html.Div('Reviews Posted: '+ MinPosted_DateTime +' - '+ MaxPosted_DateTime, className="text-left fs-6", style={'color': 'white'})
        ]),

        #Horizontal line for spacing
        dbc.Row([
            html.Hr()  # Add a horizontal line
        ]),

        #First tab for the visuals
        dcc.Tabs(id="tabs", children=[
            dcc.Tab(label='Visuals', style={'backgroundColor': '#060606', 'color': 'white','height': '30px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 
            selected_style={'backgroundColor': '#363636', 'color': 'white','height': '30px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
                
                #Horizontal spacing
                dbc.Row([
                    html.Br()  
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            html.Div('Select Primary Brand', className="text-left fs-6", style={'color': 'white'})
                        ]),
                        dbc.Row([
                            dcc.Dropdown(
                            id='brand-dropdown',
                            options=[{'label': i, 'value': i} for i in df['Brand'].unique()],
                            value=df['Brand'].unique()[0]  # set the default value to the first brand
                            ),
                        ]),
                        dbc.Row([
                            html.Br()  
                        ]),
                        dbc.Row([
                            html.Div('Select Competitor Brands', className="text-left fs-6", style={'color': 'white'})
                        ]),
                        dbc.Row([
                            dcc.Dropdown(
                            id='competitors-dropdown',
                            multi=True
                            ),
                        ]),
                        dbc.Row([
                            html.Br()  
                        ]),
                        dbc.Row([
                            html.Div('Select Sentiment Version', className="text-left fs-6", style={'color': 'white'})
                        ]),
                        dbc.Row([
                            dbc.RadioItems(
                                    options=[{"label": x, "value": x} for x in ['TitleAndReview_Sentiment', 'Review_Sentiment', 'Title_Sentiment']],
                                    value='TitleAndReview_Sentiment',
                                    inline=False,
                                    id='radio-buttons-final'
                                    ),
                        ]),
                    ], width=6),
                    
                    dbc.Col([
                             dcc.Graph(id='time-series-chart')
                                                  
                    ], width=6),
                ]),
                
                dbc.Row([
                    html.Br()  
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='splits-by-brand-chart')
                    ], width=6),
                    dbc.Col([
                        dcc.Graph(id='doughnut-chart')
                    ],width=3),
                    dbc.Col([
                        dcc.Graph(id='doughnut-chart2')
                    ],width=3),
                ]),
            ]),


            #Second tab for the Stars vs Sentiment Correlation
            dcc.Tab(label='Stars vs Sentiment', 
                    style={'backgroundColor': '#060606', 'color': 'white','height': '30px', 
                           'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 
                    selected_style={'backgroundColor': '#363636', 'color': 'white','height': '30px', 
                                    'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 
                    children=[
                        dbc.Row([
                            html.Br()  
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(figure={}, id='stars-vs-sentiment')  
                            ], width=6)
                            
                        ]),
                    ]
            ),

            #Third tab for the data
            dcc.Tab(label='Data', 
                    style={'backgroundColor': '#060606', 'color': 'white','height': '30px', 
                           'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 
                    selected_style={'backgroundColor': '#363636', 'color': 'white','height': '30px', 
                                    'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, 
                    children=[
                        dbc.Row([
                            html.Br()  
                        ]),
                        
                        dbc.Row([
                            dash_table.DataTable(
                            data=df2.to_dict('records'),
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_header={'backgroundColor': 'rgb(30, 30, 30)','color': 'white',},
                            style_cell={'backgroundColor': 'rgb(50, 50, 50)','color': 'white','textAlign': 'center',},
                            style_data={'width': '150px', 'overflow': 'hidden','textOverflow': 'ellipsis',},
                            style_data_conditional=[{'if': {'row_index': 'odd'},
                                                     'backgroundColor': 'rgb(50, 50, 50)'},
                                                    {'if': {'column_id': 'Review_Title'},
                                                     'textAlign': 'left','minWidth': '250px', 'width': '250px', 'maxWidth': '250px',},
                                                    {'if': {'column_id': 'Review_TitleAndText'},
                                                     'textAlign': 'left','minWidth': '1000px', 'width': '1000px', 'maxWidth': '1000px',}
                                                    ],
                        )
                        ]),
                    ]
            ),
        ]),
    ], fluid=True)
])



# Add controls to build the interaction
############################################

@callback(
    [Output(component_id='stars-vs-sentiment', component_property='figure'),
     Output(component_id='time-series-chart', component_property='figure'),
     Output(component_id='doughnut-chart', component_property='figure'),
     Output(component_id='doughnut-chart2', component_property='figure'),
     Output(component_id='splits-by-brand-chart', component_property='figure')],
    [Input(component_id='radio-buttons-final', component_property='value'),
     Input(component_id='brand-dropdown', component_property='value'),
     Input(component_id='competitors-dropdown', component_property='value')]
)

def update_graphs(col_chosen, primary_brand, competitor_brands):
    
    #Create the Stars vs Sentiment Chart (line chart plus confidence interval)
    ##########################################################################
    df_grouped = df.groupby('Review_Stars')[col_chosen].agg(['mean', 'count', 'std']).reset_index()
    df_grouped['yerr'] = df_grouped['std'] / df_grouped['count'].apply(np.sqrt) * stats.t.ppf(1-0.05/2, df_grouped['count'] - 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_grouped['Review_Stars'], y=df_grouped['mean'],
        mode='lines',
        line=dict(color='rgb(0,100,80)'),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df_grouped['Review_Stars'].tolist() + df_grouped['Review_Stars'].tolist()[::-1],
        y=(df_grouped['mean'] + df_grouped['yerr']).tolist() + (df_grouped['mean'] - df_grouped['yerr']).tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    ))
    fig.update_layout(template='plotly_dark',
                      title='TP Stars vs Vader Sentiment',
                      xaxis_title='Review Stars',
                      yaxis_title='Average Sentiment')
    
    # Create the time series chart
    ###############################
    if primary_brand and competitor_brands:
        filtered_df = df[df['Brand'].isin([primary_brand] + competitor_brands)]
    else:
        filtered_df = df

    filtered_df['Experience_Date'] = pd.to_datetime(filtered_df['Experience_Date'])
    df_sorted = filtered_df.sort_values('Experience_Date')
    df_sorted['14_day_avg'] = df_sorted.groupby('Brand')[col_chosen].transform(lambda x: x.rolling(window=14).mean())
    df_grouped_by_date = df_sorted.groupby(['Experience_Date', 'Brand'])['14_day_avg'].last().reset_index()
    time_series_chart = px.line(df_grouped_by_date, x='Experience_Date', y='14_day_avg', color='Brand')
    
    MinChartDte = df_grouped_by_date['Experience_Date'].max() - pd.DateOffset(months=6)  #Min Date in Default Chart View
    
    time_series_chart.update_layout(        #add styling elements
        template='plotly_dark',
        title='Sentiment by Experience Date (14-day Moving Average)',
        xaxis_title='Experience Date',
        yaxis_title='Average Sentiment',
        xaxis_range=[MinChartDte, df_grouped_by_date['Experience_Date'].max()], # Set default x-axis range
        height=320  
        )

    # Create the doughnut chart(s)
    ############################
    if primary_brand:
        prim_df = filtered_df[filtered_df['Brand'].isin([primary_brand])]
    else:
        prim_df = filtered_df

    if competitor_brands:
        comp_df = filtered_df[filtered_df['Brand'].isin(competitor_brands)]
    else:
        comp_df = filtered_df

    #create doughnut chart for primary brand
    df_grouped_by_stars = prim_df['Review_Stars'].value_counts().reset_index()
    df_grouped_by_stars.columns = ['Review_Stars', 'count']
    doughnut_chart = px.pie(df_grouped_by_stars, names='Review_Stars', values='count', hole=.4, 
                        category_orders={"Review_Stars": [5, 4, 3, 2, 1]})
    doughnut_chart.update_layout(template='plotly_dark',
                             title='Truspilot Stars: '+primary_brand)

    #create doughnut chart for competitors
    df_grouped_by_stars2 = comp_df['Review_Stars'].value_counts().reset_index()
    df_grouped_by_stars2.columns = ['Review_Stars', 'count']
    doughnut_chart2 = px.pie(df_grouped_by_stars2, names='Review_Stars', values='count', hole=.4, 
                         category_orders={"Review_Stars": [5, 4, 3, 2, 1]})
    doughnut_chart2.update_layout(template='plotly_dark',
                             title='Truspilot Stars: selected competitors')


    # Create the splits by brand chart
    ###################################
    grp_df = filtered_df.groupby('Brand').agg({'ReviewNum': 'count', col_chosen: 'mean'}).reset_index()

    # Create the bar chart
    bar_chart = go.Bar(
        x=grp_df['Brand'],
        y=grp_df['ReviewNum'],
        name='Review Count',
        yaxis='y1'
    )

    # Create the line chart
    line_chart = go.Scatter(
        x=grp_df['Brand'],
        y=grp_df[col_chosen],
        name='Average Sentiment',
        yaxis='y2'
    )

    # Create the layout
    lay_out = go.Layout(
        title='Review Count and Average Sentiment by Brand',
        yaxis=dict(
            title='Review Count'
        ),
        yaxis2=dict(
            title='Average Sentiment',
            overlaying='y',
            side='right',
            range=[-1,1]
        ),
        legend=dict(
            x=1.05,
            y=1.2,
            xanchor='auto',
            yanchor='auto'
    )
    )

    # Combine the charts
    splits_by_brand_chart = go.Figure(data=[bar_chart, line_chart], layout=lay_out)
    splits_by_brand_chart.update_layout(template='plotly_dark')  # Set theme to dark mode

    return fig, time_series_chart, doughnut_chart, doughnut_chart2, splits_by_brand_chart

    

@app.callback(
    Output('competitors-dropdown', 'options'),
    Input('brand-dropdown', 'value')
)
def update_competitors_dropdown(primary_brand):
    # Get all brands excluding the primary brand
    competitors = df[df['Brand'] != primary_brand]['Brand'].unique()
    # Create the options for the dropdown
    options = [{'label': i, 'value': i} for i in competitors]
    return options


# Run the app
############################################
if __name__ == '__main__':
    app.run(debug=True)