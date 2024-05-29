from dash import Dash, html, dcc, callback, Output, Input, State,callback_context
from plotly.subplots import make_subplots
from plotly import graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash
import json
import os
import warnings

global BASE
global STRATEGY
global SIMTEST
global BACKTEST
global PLOT
global TREND_TYPE
global TREND_ID
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
TREND_TYPE = None
TREND_ID = None

strategies = os.listdir(BASE)

app = dash.Dash(__name__,suppress_callback_exceptions=True, title="SimTest Dashboard")
app.config.prevent_initial_callbacks='initial_duplicate'

@callback(
    Output('progress-bar-container', 'children'),
    Input('performance', 'data'),
    Input('trend-performance', 'data'),
    Input('trend-id-performance', 'data'),
)
def update_progress_bar(performance, trend_performance, trend_id_performance):
    # if no data is available, return dash.no_update
    # use ctx to decide whichever is triggered
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        if len(ctx.triggered) > 1:
            return dash.no_update
        #assign progress 
        elif ctx.triggered[0]['prop_id'] == 'performance.data':
            progress = performance
        elif ctx.triggered[0]['prop_id'] == 'trend-performance.data':
            progress = trend_performance
        elif ctx.triggered[0]['prop_id'] == 'trend-id-performance.data':
            progress = trend_id_performance
        else:
            print("else",ctx.triggered[0])
            progress = 0
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = progress,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Strategy Performance", 'font': {'size': 24,'color':'White'}},
        delta = {'reference': 60, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            # choose bar color something very classy and elite
            'bar': {'color': 'black'},
            'bgcolor': "white",
            'borderwidth': 1.5,
            'bordercolor': "gray",
            'steps': [
                # available 
                {'range': [0, 20], 'color': '#F96167'},       # Reddish
                {'range': [20, 60], 'color': '#F9E795'},    # Orange
                {'range': [60, 90], 'color': '#317773'},      # Greenish
                {'range': [90, 100], 'color': '#E2D1F9'}    # Purple
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': progress}}))

    fig.update_layout(    paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                    font = {'color': "white", 'family': "Arial", 'size': 14})

    return dcc.Graph(figure=fig,
                     # %50 move to up
                     style={'margin-top': '-25%', 'margin-left': '-15%'},responsive=True)


# create callback that updates the available options based on the strategy selected
@callback(
    Output("simtest-selection", "options"),
    Input("strategy-selection", "value")
)
def update_simtest_dropdown(strategy):
    global STRATEGY
    STRATEGY = strategy
    try:
        simtests = os.listdir(os.path.join(BASE, STRATEGY))
    except:
        simtests = []
    return simtests

# create callback that updates the options based on the simtest selected
@callback(
    Output("backtest-selection", "options"),
    Input("simtest-selection", "value")
)
def update_backtest_dropdown(simtest):
    global SIMTEST, STRATEGY
    SIMTEST = simtest
    try:
        backtests = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST))
        # filter backtests 
        backtests = [backtest for backtest in backtests]
    except:
        backtests = []
    return backtests

# create callback that updates the available plots based on the backtest selected
@callback(
    Output("plot-selection", "options"),
    Input("backtest-selection", "value"),
    prevent_initial_call=True
)
def update_plot_dropdown(backtest):
    global BACKTEST, STRATEGY, SIMTEST
    BACKTEST = backtest
    try:
        if BACKTEST[:8] == "backtest":
            plots = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST))
            # filter plots if they are all csv files
            plots = [plot[:-4] for plot in plots if plot[-4:] == '.csv' and plot != 'price.csv']
        else:
            return os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST))
    except:
        plots = []
    return plots

# create callback that updates the dataset information div
@callback(Output("dataset-info", "children"),
          Input("backtest-selection", "value"))
def update_dataset_info(backtest):
    # will return a div with the dataset information
    global BACKTEST, STRATEGY, SIMTEST
    BACKTEST = backtest
    try:
        if BACKTEST[:8] == "backtest":
            backtest_info = BACKTEST.split("_")
            # will return a text with the dataset information
            info = f"This dataset is a {backtest_info[0]} dataset with {backtest_info[1]} \
    tick data from {backtest_info[2]} to {backtest_info[3]}."
            return html.P(info, style={"font-weight": "bold"}),
        elif BACKTEST[:10] == "simulation":
            trendtypes = list(filter(lambda x: x != "cumulative_results.json", os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST))))
            n = 0
            for trendtype in trendtypes:
                n += len(os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, trendtype)))
            # will return a text with the dataset information
            info = f"This dataset is a {BACKTEST[:10]} dataset. There are {len(trendtypes)} trend types with total number of {n} Monte Carlo simulations.Please select the trendtype from the dropdown below."
            return html.Div([
                html.P(info, style={"font-weight": "bold"}),
                # dropdown for selecting among the path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST)
                html.Div([
                    dcc.Dropdown(trendtypes, "trend-type", id="trend-type-selection",
                                style={"width":"100%",
                                        "margin-bottom":"10px",
                                        "margin-top":"10px",
                                        "margin-left":"auto",
                                        "margin-right":"auto",
                                        "text-align":"center",                                
                                        }, placeholder="Select a trend type"),
                    dcc.Dropdown([], "trend-id", id="trend-id-selection",
                                style={"width":"100%",
                                        "margin-bottom":"10px",
                                        "margin-top":"10px",
                                        "margin-left":"auto",
                                        "margin-right":"auto",
                                        "text-align":"center",                                
                                        }, placeholder="Select a trend id")
                ],id="wrapper")
            ])        
    except Exception as e:
        return html.P("The dataset information will be loaded after the desired backtest/simulation is selected.", style={"font-weight": "bold"})


# create a callback that updates dropdown of trend-id based on the selected trend-type
@callback(Output("trend-id-selection", "options"),
          Input("trend-type-selection", "value"))
def update_trend_id_dropdown(trendtype):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE
    TREND_TYPE = trendtype
    try:
        if BACKTEST[:10] == "simulation":
            trend_ids = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, trendtype))
            # filter trend_ids if they are all csv files
            trend_ids = [trend_id for trend_id in trend_ids]
            trend_ids.append("All trend ids.")
    except:
        trend_ids = []
    return trend_ids

#create a callback that updates the plot-selection dropdown based on the selected trend-id
@callback(Output("plot-selection", "options",allow_duplicate=True),
            Input("trend-id-selection", "value"),
            prevent_initial_call=True)
def update_plot_dropdown(trend_id):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE, TREND_ID
    TREND_ID = trend_id
    try:
        if BACKTEST[:10] == "simulation":
            if TREND_ID == "All trend ids.":
                first_folder = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE))[0]
                plots = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE, first_folder))
            else:
                plots = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE, TREND_ID))
            # filter plots if they are all csv files
            plots = [plot[:-4] for plot in plots if plot[-4:] == '.csv' and plot != 'price.csv']
    except:
        plots = []
    return plots


def concat_metrics(path):
    if os.path.exists(os.path.join(path,"_dash.csv")):
        return pd.read_csv(os.path.join(path,"_dash.csv"))
    csv_list = os.listdir(path)
    csv_list.remove('price.csv')
    csv_list.remove('result.json')
    df = pd.read_csv(os.path.join(path, "price.csv"))

    for metric_csv in csv_list:
        metric_name = metric_csv.split(".")[0]
        metric_df = pd.read_csv(os.path.join(path, metric_csv))

        metric_list = [np.NaN for x in range(df.shape[0])]
        last_value = 0.0
        index = 0
        for price_t in df["timestamp"]:
            for metric_t, value in zip(metric_df["timestamp"], metric_df["data"]):
                if price_t == metric_t:
                    metric_list[index] = value
                    last_value = value
                else:
                    metric_list[index] = last_value
            index += 1

        extended_metric_df = pd.DataFrame({f"{metric_name}":metric_list})

        df = pd.concat([df, extended_metric_df], axis=1)
    df.to_csv(os.path.join(path,"_dash.csv"), index=False)

    return df

# create callback that updates the graph based on the plot selected
@callback(
    Output("graph-content", "figure"),
    Input("plot-selection", "value")
)
def update_graph(plot):
    global BACKTEST, STRATEGY, SIMTEST, PLOT, TREND_TYPE, TREND_ID
    PLOT = plot
    try:
        metric = plot.split(".")[0]
        warnings.filterwarnings("ignore", category=DeprecationWarning) 
        if BACKTEST[:8] == "backtest":
            path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST)
            df = concat_metrics(path)
            fig = make_subplots(specs=[[{"secondary_y":True}]])
            fig.add_trace(
                go.Line(x=df["timestamp"], y=df["data"], name="Price"),
                secondary_y=False,
            )
            fig.add_trace(
                go.Line(x=df["timestamp"], y=df[f"{metric}"], name=metric),
                secondary_y=True,
            )
            fig.update_layout(title_text=metric, title_x=0.5, title_font_size=18, template="plotly_dark", width=1000, height=500)
        elif BACKTEST[:10] == "simulation":
            path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE, TREND_ID)
            id_list = [TREND_ID]
            if TREND_ID == "All trend ids.":
                id_list = os.listdir(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE))
            fig = make_subplots(specs=[[{"secondary_y":True}]])
            for trend_id in id_list:
                path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE, trend_id)
                df = concat_metrics(path)
                fig.add_trace(
                    go.Line(x=df["timestamp"], y=df["data"], name=f"Price_{trend_id}"),
                    secondary_y=False,
                )
                fig.add_trace( 
                    go.Line(x=df["timestamp"], y=df[f"{metric}"], name=f"{metric.capitalize()}_{trend_id}"),
                    secondary_y=True,
                )
                fig.update_layout(title_text=metric, title_x=0.5, title_font_size=18, template="plotly_dark", width=1000, height=500)
        
    except Exception as e:

        fig = px.line(template="plotly_dark", width=1000, height=500)

    # add "SimTest" title to the graph
    fig.update_layout(title_text="SimTest", title_x=0.5, title_font_size=18)
    
    return fig

# create callback that updates the result.json to be read based on the backtest selected
@callback(
    Output("performance", "data"),
    Input("backtest-selection", "value"),
)
def update_result_json(backtest):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE
    BACKTEST = backtest
    perf = 0
    try:
        if BACKTEST[:10] == "simulation":
            path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, 'cumulative_results.json')
            with open(path) as f:
                data = json.load(f)
            for type, value in data.items():
                perf += value['Performance']

            perf /= len(data)
        elif BACKTEST[:8] == "backtest":
            path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, 'result.json')
            with open(path) as f:
                data = json.load(f)
            perf = data['Performance']

        return perf
    except Exception as e:
        pass

    return perf

@callback(
    Output("trend-performance", "data"),
    Input("trend-type-selection", "value"),
)
def update_result_json_trend_type(trend_type):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE
    TREND_TYPE = trend_type
    try:
        with open(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST,"cumulative_results.json"), 'r') as f:
            data = json.load(f)

        return data[trend_type]['Performance']
    except Exception as e:

        pass
    return 0

@callback(
    Output("trend-id-performance", "data"),
    Input("trend-id-selection", "value"),
)
def update_result_json_trend_id(trend_id):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE, TREND_ID
    TREND_ID = trend_id
    try:
        with open(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE, TREND_ID, "result.json"), 'r') as f:
            data = json.load(f)

        return data['Performance']
    except Exception as e:
        try:
            with open(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST,"cumulative_results.json"), 'r') as f:
                data = json.load(f)
            return data[TREND_TYPE]['Performance']
        except:
            pass
    return 0


###################################

# create callback that updates the result.json to be read based on the backtest selected
@callback(
    Output("metrics", "data"),
    Input("backtest-selection", "value"),
)
def update_result_json(backtest):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE
    BACKTEST = backtest
    data_dict = {}
    try:
        if BACKTEST[:10] == "simulation":
            path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, 'cumulative_results.json')
            with open(path) as f:
                data = json.load(f)
            for type, value in data.items():
                for metric,value in value.items():
                    if metric not in data_dict:
                        data_dict[metric] = value
                    else:
                        data_dict[metric] += value
            for metric,value in data_dict.items():
                data_dict[metric] /= len(data)
        elif BACKTEST[:8] == "backtest":
            path = os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, 'result.json')
            with open(path) as f:
                data_dict = json.load(f)
            

        return data_dict
    except Exception as e:
        pass

    return {}

@callback(
    Output("trend-metrics", "data"),
    Input("trend-type-selection", "value"),
)
def update_result_json_trend_type(trend_type):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE
    TREND_TYPE = trend_type
    try:
        with open(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST,"cumulative_results.json"), 'r') as f:
            data = json.load(f)

        return data[trend_type]
    except Exception as e:

        pass
    return {}

@callback(
    Output("trend-id-metrics", "data"),
    Input("trend-id-selection", "value"),
)
def update_result_json_trend_id(trend_id):
    global BACKTEST, STRATEGY, SIMTEST, TREND_TYPE, TREND_ID
    TREND_ID = trend_id
    try:
        with open(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST, TREND_TYPE, TREND_ID, "result.json"), 'r') as f:
            data = json.load(f)

        return data
    except Exception as e:
        try:
            with open(os.path.join(BASE, STRATEGY, SIMTEST, BACKTEST,"cumulative_results.json"), 'r') as f:
                data = json.load(f)
            return data[TREND_TYPE]
        except:
            pass
    return {}

@callback(
    Output('metrics-container', 'children'),
    Output('critical-container', 'children'),
    Input('metrics', 'data'),
    Input('trend-metrics', 'data'),
    Input('trend-id-metrics', 'data'),

)
def update_metrics_json(metrics, trend_metrics, trend_id_metrics):
    # if no data is available, return dash.no_update
    # use ctx to decide whichever is triggered
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        if len(ctx.triggered) > 1:
            return dash.no_update
        #assign progress 
        elif ctx.triggered[0]['prop_id'] == 'metrics.data':
            metrics_data = metrics
        elif ctx.triggered[0]['prop_id'] == 'trend-metrics.data':
            metrics_data = trend_metrics
        elif ctx.triggered[0]['prop_id'] == 'trend-id-metrics.data':
            metrics_data = trend_id_metrics
        else:
            print("else",ctx.triggered[0])
            metrics = {}

        # create a list of divs that contain the metrics
        critical_metrics = ["Win Rate","Profit Factor", "Average PnL", "RRR", "Max. DD","Total Win", "Total Loss","Sugg. Leverage"]

        metrics_list = []
        critical_list = []
        for metric, value in metrics_data.items():
            # "Profit Factor":profit_factor,
            # "Average PnL":average_pnl,
            # "RRR":rrr,
            # "Max. DD":max_dd, -> cont.
            if metric == "Performance":
                continue
            # check if value is int and float, if float round to 5 digits , if integer display integer
            if isinstance(value, float):
                value = round(value, 2)
            elif isinstance(value, int):
                value = int(value)


            condition = metric in critical_metrics
            # make it fit into to the returned div
            #<div class="card">
            #	<div class="right">
            #		<h2 class="name">metric</h2>
            #		<p class="title">Backtest/simulation</p>
            #		<p class="location">Date/Trend</p>
            #		<div class="interests">
            #			<span class="interests_item">value</span>
            #		</div>
            #	</div>
            #</div>
            if BACKTEST[:8] == "backtest": 
                if condition:
                    critical_list.append(
                        html.Div(
                            className="card",
                            children=[
                                html.Div(
                                    className="right",
                                    children=[
                                        html.H2(className="name", children=metric, style={"font-size":"12px", "font-weight":"bold"}),
                                        html.P(className="title", children="Backtest", style={"font-size":"9px"}),
                                        html.Div(
                                        className="interests",
                                        children=[
                                            html.Span(className="interests_item", children=value, style={"font-size":"12px","font-weight":"bold"}),
                                        ],
                                    ),
                                    ],
                                ),
                            ],
                        )
                    )
                else:
                    metrics_list.append(
                        html.Div(
                            className="card",
                            children=[
                                html.Div(
                                    className="right",
                                    children=[
                                        html.H2(className="name", children=metric, style={"font-size":"12px", "font-weight":"bold"}),
                                            html.P(className="title", children="Backtest", style={"font-size":"9px"}),
                                            html.Div(
                                            className="interests",
                                            children=[
                                                html.Span(className="interests_item", children=value, style={"font-size":"12px","font-weight":"bold"}),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    )
            elif BACKTEST[:10] == "simulation":
                if condition:
                    critical_list.append(
                        html.Div(
                            className="card",
                            children=[
                                html.Div(
                                    className="right",
                                    children=[
                                        html.H2(className="name", children=metric, style={"font-size":"12px", "font-weight":"bold"}),
                                        html.P(className="title", children="Sim.", style={"font-size":"9px"}),
                                        html.Div(
                                        className="interests",
                                        children=[
                                            html.Span(className="interests_item", children=value, style={"font-size":"12px","font-weight":"bold"}),
                                        ],
                                    ),
                                    ],
                                ),
                            ],
                        )
                    )
                else:
                    metrics_list.append(
                        html.Div(
                                className="card",
                                children=[
                                    html.Div(
                                        className="right",
                                        children=[
                                        html.H2(className="name", children=metric, style={"font-size":"12px", "font-weight":"bold"}),
                                            html.P(className="title", children="Sim.", style={"font-size":"9px"}),
                                                html.Div(
                                                className="interests",
                                                children=[
                                                    html.Span(className="interests_item", children=value, style={"font-size":"12px","font-weight":"bold"}),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            )
                        )

        return metrics_list, critical_list
    






######### HISTOGRAM
def concat_all_results(strategy_name, simtest_name) -> pd.DataFrame:
    backtest_list = os.listdir(os.path.join("results", strategy_name, simtest_name))
    df = pd.DataFrame()
    for backtest_name in backtest_list:
        if backtest_name.startswith("backtest"):
            #with open(f"results/{strategy_name}/{simtest_name}/{backtest_name}/result.json", encoding="utf-8") as file:
            with open(os.path.join("results", strategy_name, simtest_name, backtest_name, "result.json"), encoding="utf-8") as file:
                data = json.load(file)
            win_rate = round(data["Win Rate"],3) if isinstance(data["Win Rate"],float) else int(data["Win Rate"])
            profit_factor = round(data["Profit Factor"],3) if isinstance(data["Profit Factor"],float) else int(data["Profit Factor"])
            average_pnl = round(data["Average PnL"],3) if isinstance(data["Average PnL"],float) else int(data["Average PnL"])
            rrr = round(data["RRR"],3) if isinstance(data["RRR"],float) else int(data["RRR"])
            max_dd = round(data["Max. DD"],3) if isinstance(data["Max. DD"],float) else int(data["Max. DD"])
            total_trades = round(data["Total Trades"],3) if isinstance(data["Total Trades"],float) else int(data["Total Trades"])
            winning_trades = round(data["Winning Trades"],3) if isinstance(data["Winning Trades"],float) else int(data["Winning Trades"])
            losing_trades = round(data["Losing Trades"],3) if isinstance(data["Losing Trades"],float) else int(data["Losing Trades"])
            best_win = round(data["Best Win"],3) if isinstance(data["Best Win"],float) else int(data["Best Win"])
            worst_loss = round(data["Worst Loss"],3) if isinstance(data["Worst Loss"],float) else int(data["Worst Loss"])

            df1 = pd.DataFrame([{
                "Backtest Name":backtest_name,
                "Win Rate":win_rate,
                "Profit Factor":profit_factor,
                "Average PnL":average_pnl,
                "RRR":rrr,
                "Max. DD":max_dd,
                "Total Trades":total_trades,
                "Winning Trades":winning_trades,
                "Losing Trades":losing_trades,
                "Best Win":best_win,
                "Worst Loss":worst_loss
            }])
            df = pd.concat([df, df1], axis=0)

        if backtest_name.startswith("simulation"):
            with open(os.path.join("results", strategy_name, simtest_name, backtest_name, "cumulative_results.json"), encoding="utf-8") as file:
                cum_data = json.load(file)

            for trend, data in cum_data.items():
                win_rate = round(data["Win Rate"],3) if isinstance(data["Win Rate"],float) else int(data["Win Rate"])
                profit_factor = round(data["Profit Factor"],3) if isinstance(data["Profit Factor"],float) else int(data["Profit Factor"])
                average_pnl = round(data["Average PnL"],3) if isinstance(data["Average PnL"],float) else int(data["Average PnL"])
                rrr = round(data["RRR"],3) if isinstance(data["RRR"],float) else int(data["RRR"])
                max_dd = round(data["Max. DD"],3) if isinstance(data["Max. DD"],float) else int(data["Max. DD"])
                total_trades = round(data["Total Trades"],3) if isinstance(data["Total Trades"],float) else int(data["Total Trades"])
                winning_trades = round(data["Winning Trades"],3) if isinstance(data["Winning Trades"],float) else int(data["Winning Trades"])
                losing_trades = round(data["Losing Trades"],3) if isinstance(data["Losing Trades"],float) else int(data["Losing Trades"])
                best_win = round(data["Best Win"],3) if isinstance(data["Best Win"],float) else int(data["Best Win"])
                worst_loss = round(data["Worst Loss"],3) if isinstance(data["Worst Loss"],float) else int(data["Worst Loss"])

                df1 = pd.DataFrame([{
                    "Backtest Name":f"sim_{trend}_{'-'.join(backtest_name.split('-')[1:])}",
                    "Win Rate":win_rate,
                    "Profit Factor":profit_factor,
                    "Average PnL":average_pnl,
                    "RRR":rrr,
                    "Max. DD":max_dd,
                    "Total Trades":total_trades,
                    "Winning Trades":winning_trades,
                    "Losing Trades":losing_trades,
                    "Best Win":best_win,
                    "Worst Loss":worst_loss
                }])
                df = pd.concat([df, df1], axis=0)
        else:
            pass
    return df

@callback(
    # Output is a div
    Output("histogram-controller", "children"),
    # Input is a dropdown
    Input("simtest-selection", "value"),
)
def update_histogram(simtest):
    global BASE, STRATEGY, SIMTEST
    SIMTEST = simtest
    try:
        from dash.dash_table import DataTable 
        df = concat_all_results(strategy_name=STRATEGY, simtest_name=SIMTEST)
        div = html.Div([
            dcc.RadioItems(options=df.columns[1:], value=df.columns[1], id='controls-and-radio-item', labelStyle={'display': 'inline-block'},
                           style={'width': '100%','font-size': '11px','text-align': 'center'}),
            DataTable(data=df.to_dict('records'), page_size=3,
                                    columns=[
                {'id': c, 'name': c,}
                for c in df.columns
            ],
            style_data_conditional=[{
                'if': {'column_editable': False},
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            
            }],
            style_header_conditional=[{
                'if': {'column_editable': False},
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            }],
            fixed_columns={'headers': True, 'data': 1},
            style_table={'minWidth': '100%'}
            ),
        ])
    except:
        div = html.Div([
            dcc.RadioItems(options=[], value="Options", id='controls-and-radio-item', labelStyle={'display': 'inline-block'},
                           style={'width': '100%','font-size': '11px','text-align': 'center'}),
            DataTable(data=[], page_size=3,
                                    columns=[
                {'id': c, 'name': c,}
                for c in []
            ],
            style_data_conditional=[{
                'if': {'column_editable': False},
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            
            }],
            style_header_conditional=[{
                'if': {'column_editable': False},
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'
            }],
            fixed_columns={'headers': True, 'data': 1},
            style_table={'minWidth': '100%'}
            ),
        ],)
    return div


# Add controls to build the interaction
@callback(
    Output(component_id='histogram', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_hist(col_chosen):
    fig = px.histogram(pd.DataFrame())
    try:
        df = concat_all_results(strategy_name=STRATEGY, simtest_name=SIMTEST)
        fig = px.histogram(df, x='Backtest Name', y=col_chosen, histfunc='avg',text_auto=True,
                           # make every histogram different color 
                            color='Backtest Name',
                            # make each bar different color
                            color_discrete_sequence=px.colors.qualitative.Plotly,
                           )
        fig.update_layout(title_text=f"{col_chosen} Comparison", title_x=0.5, title_font_size=18, template="plotly_dark", width=1000,height=500)
    except:
        fig.update_layout(title_text="Comparison", title_x=0.5, title_font_size=18, template="plotly_dark", width=1000,height=500)
    return fig
