from dash import Dash, html, dcc, callback, Output, Input, dash_table
from plotly.subplots import make_subplots
import plotly.express as px
from plotly import graph_objs as go
import pandas as pd
from collections import OrderedDict
import os
import dash
import warnings


from _callbacks import *
#@TODO update strategies = os.listdir() such that it is a callback so it loads constantly and updates when new strategies are added


app.layout = html.Div([
    html.Div([
        # Top left side: Strategy name and important information

        html.Div([], className='top-left-div', id='progress-bar-container'),

        html.Div([
            html.Div([
                html.Div(id='critical-container'),
            ], className='info-container'),
        ], className='top-right-div'),
        # define bottom-left and bottom right divs and set placeholder text in them
        html.Div([
            html.H1(children="SimTest selection", style={"text-align":"center","color":"white",'margin-top':'10px'}),
            html.Div([
                dcc.Dropdown(strategies, "strategies", id="strategy-selection", 
                            className="div-for-dropdown", placeholder="Select a strategy"),
                dcc.Dropdown([], "simtests", id="simtest-selection", 
                            className="div-for-dropdown", placeholder="Select a simtest"),
                dcc.Dropdown([], "backtests", id="backtest-selection", 
                            className="div-for-dropdown", placeholder="Select a backtest"),
                dcc.Dropdown([], "plots", id="plot-selection",
                            className="div-for-dropdown", placeholder="Select a plot"),
            ],id='wrapper'),
            dcc.Store(id='performance'),
            dcc.Store(id="trend-performance"),
            dcc.Store(id="trend-id-performance"),
            dcc.Store(id="metrics"),
            dcc.Store(id="trend-metrics"),
            dcc.Store(id="trend-id-metrics"),
        ], className='bottom-left-div'),
        html.Div([
            html.H1('Dataset Information'),
            html.Div(id='dataset-info'),
        ], className='bottom-right-div'),
    ], className='top-left-div'),

    html.Div([
        # Top right side: Detailed numerical results
        html.Div([
            html.Div(id='metrics-container'),
        ], className='info-container'),
        html.Div([
            html.Div(id='histogram-controller'),
        ], className='info-container'),
    ], className='top-right-div'),

    html.Div([
        # Bottom left side: Backtesting plots
        html.Div([
            dcc.Graph(id="graph-content",responsive=True,),
        ], className='plot-container')
    ], className='bottom-left-div'),

    html.Div([
        # Bottom right side: Dataset 
        html.Div([
            dcc.Graph(id="histogram",responsive=True,),
        ], className='plot-container')
    ], className='bottom-right-div')
], className='dashboard-container')



if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=DeprecationWarning) 
    app.run(debug=True)