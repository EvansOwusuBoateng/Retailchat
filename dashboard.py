from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from data_preprocessing import wrangle


def calculate_duplicates_and_nulls(data):
    null_values = data.isnull().sum()
    duplicate_rows = data.duplicated().sum()
    return null_values, duplicate_rows


def create_histogram(data, x_col, title):
    fig = px.histogram(data, x=x_col, title=title)
    return dcc.Graph(figure=fig)


def create_box_plot(data, x_col, y_col, title):
    fig = px.box(data, x=x_col, y=y_col, title=title)
    return dcc.Graph(figure=fig)


def create_line_chart(data, x_col, y_col, title):
    fig = px.line(data, x=x_col, y=y_col, title=title)
    return dcc.Graph(figure=fig)


def create_pie_chart(data, feature_col, title):
    fig = px.pie(data, names=feature_col, title=title)
    return dcc.Graph(figure=fig)


def create_data_overview_table(data, num_rows):
    if not data.empty:
        # Prepare null values
        null_values = data.isnull().sum()
        null_data = [{"Column": col, "Null Values": null_values[col]} for col in data.columns]

        # Prepare summary statistics
        summary_stats = data.describe().T.reset_index()
        summary_data = summary_stats.to_dict('records')

        # Prepare data observations
        observations = data.head(num_rows).reset_index().to_dict('records')

        # Create DataTable for null values
        null_values_table = dash_table.DataTable(
            id='null-values-table',
            columns=[{'name': 'Column', 'id': 'Column'}, {'name': 'Null Values', 'id': 'Null Values'}],
            data=null_data,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
        )

        # Create DataTable for summary statistics
        summary_table = dash_table.DataTable(
            id='summary-table',
            columns=[{'name': i, 'id': i} for i in summary_stats.columns],
            data=summary_data,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
        )

        # Create DataTable for data observations
        data_table = dash_table.DataTable(
            id='observations-table',
            columns=[{'name': col, 'id': col} for col in data.columns],
            data=observations,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
        )

        return html.Div([
            dbc.Row([
                dbc.Col(html.Div([html.H5("Null Values"), null_values_table]), width=2),
                dbc.Col(html.Div([html.H5("Summary Statistics"), summary_table]), width=5),
                dbc.Col(html.Div([html.H5("Data Observations"), data_table]), width=5)
            ])
        ])
    else:
        return html.Div("No data available", style={'textAlign': 'center'})


def create_dash_app(flask_app):
    app = Dash(__name__, server=flask_app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dbc.Row([dbc.Col([html.H2("Summarized data analysis by AnalytiCore", style={'text-align': 'center'})], width=12)]),
        dbc.Row([
            dbc.Col([html.H6(id='duplicate-rows-text')], width=6, style={'text-align': 'left', 'margin-top': '20px'}),
            dbc.Col([html.H6("Number of Rows to Display:")], width=3,
                    style={'text-align': 'right', 'margin-top': '20px', 'padding-right': '10px'}),
            dbc.Col([dcc.Dropdown(id='num-rows-dropdown', options=[{'label': i, 'value': i} for i in range(20)],
                                  value=5, style={'width': '200px'})], width=3,
                    style={'margin-top': '20px', 'padding-left': '10px'}),
        ]),
        dbc.Row([dbc.Col([html.Div(id='data-overview')], width=12)]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Correlation Graph"),
                    dcc.Graph(id='correlation-graph'),
                    dbc.Row([
                        dbc.Col([html.Label("X-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='correlation-x-axis', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    dbc.Row([
                        dbc.Col([html.Label("Y-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='correlation-y-axis', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Bar Chart"),
                    dcc.Dropdown(id='bar-chart-dropdown', multi=True),
                    dcc.Graph(id='bar-chart'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Histogram"),
                    dcc.Dropdown(id='histogram-dropdown'),
                    html.Div(id='histogram-container'),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Box Plot"),
                    dbc.Row([
                        dbc.Col([html.Label("X-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='box-plot-x-dropdown', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    dbc.Row([
                        dbc.Col([html.Label("Y-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='box-plot-y-dropdown', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    html.Div(id='box-plot-container'),
                ], className='chart-container'),
            ], width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Line Chart"),
                    dbc.Row([
                        dbc.Col([html.Label("X-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='line-chart-x-dropdown', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    dbc.Row([
                        dbc.Col([html.Label("Y-axis:")], width=2),
                        dbc.Col([dcc.Dropdown(id='line-chart-y-dropdown', style={'width': '200px'})], width=10),
                    ], className='radio-button-row', style={'margin-bottom': '10px'}),
                    html.Div(id='line-chart-container'),
                ], className='chart-container'),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H2("Pie Chart"),
                    dcc.Dropdown(id='pie-chart-dropdown'),
                    html.Div(id='pie-chart-container'),
                ], className='chart-container'),
            ], width=6),
        ]),
    ], className='container-fluid')

    @app.callback(
        Output('duplicate-rows-text', 'children'),
        [Input('url', 'search'), Input('num-rows-dropdown', 'value')])
    def update_duplicate_text(search, num_rows):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            null_values, duplicate_rows = calculate_duplicates_and_nulls(data)
            _, _, _ = wrangle(file_path)
            return f"Number of Duplicate Rows: {duplicate_rows}, Displaying {num_rows} rows."
        else:
            return "No file uploaded"

    @app.callback(
        Output('data-overview', 'children'),
        [Input('url', 'search'), Input('num-rows-dropdown', 'value')])
    def update_data_overview(search, num_rows):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            null_values, duplicate_rows = calculate_duplicates_and_nulls(data)
            data, _, _ = wrangle(file_path)
            return create_data_overview_table(data, num_rows)
        else:
            return html.Div("No data available")

    @app.callback(
        Output('correlation-graph', 'figure'),
        [Input('url', 'search'), Input('correlation-x-axis', 'value'), Input('correlation-y-axis', 'value')])
    def update_correlation_graph(search, x_axis, y_axis):
        if search and '=' in search and x_axis and y_axis:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            fig = px.scatter(data, x=x_axis, y=y_axis, title=f"Correlation between {x_axis} and {y_axis}")
            return fig
        else:
            return {}

    @app.callback(
        Output('bar-chart', 'figure'),
        [Input('url', 'search'), Input('bar-chart-dropdown', 'value')])
    def update_bar_chart(search, selected_columns):
        if search and '=' in search and selected_columns:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            fig = px.bar(data, x=data.index, y=selected_columns, title="Bar Chart")
            return fig
        else:
            return {}

    @app.callback(
        Output('histogram-container', 'children'),
        [Input('url', 'search'), Input('histogram-dropdown', 'value')])
    def update_histogram(search, selected_column):
        if search and '=' in search and selected_column:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            return create_histogram(data, selected_column, f"Histogram of {selected_column}")
        else:
            return html.Div("Select a column to display histogram")

    @app.callback(
        Output('box-plot-container', 'children'),
        [Input('url', 'search'), Input('box-plot-x-dropdown', 'value'), Input('box-plot-y-dropdown', 'value')])
    def update_box_plot(search, x_axis, y_axis):
        if search and '=' in search and x_axis and y_axis:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            return create_box_plot(data, x_axis, y_axis, f"Box Plot of {x_axis} by {y_axis}")
        else:
            return html.Div("Select x and y axes to display box plot")

    @app.callback(
        Output('line-chart-container', 'children'),
        [Input('url', 'search'), Input('line-chart-x-dropdown', 'value'), Input('line-chart-y-dropdown', 'value')])
    def update_line_chart(search, x_axis, y_axis):
        if search and '=' in search and x_axis and y_axis:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            return create_line_chart(data, x_axis, y_axis, f"Line Chart of {y_axis} over {x_axis}")
        else:
            return html.Div("Select x and y axes to display line chart")

    @app.callback(
        Output('pie-chart-container', 'children'),
        [Input('url', 'search'), Input('pie-chart-dropdown', 'value')])
    def update_pie_chart(search, feature_column):
        if search and '=' in search and feature_column:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            return create_pie_chart(data, feature_column, f"Pie Chart of {feature_column}")
        else:
            return html.Div("Select a column to display pie chart")

    @app.callback(
        [Output('correlation-x-axis', 'options'),
         Output('correlation-y-axis', 'options'),
         Output('bar-chart-dropdown', 'options'),
         Output('histogram-dropdown', 'options'),
         Output('box-plot-x-dropdown', 'options'),
         Output('box-plot-y-dropdown', 'options'),
         Output('line-chart-x-dropdown', 'options'),
         Output('line-chart-y-dropdown', 'options'),
         Output('pie-chart-dropdown', 'options')],
        [Input('url', 'search')])
    def update_dropdown_options(search):
        if search and '=' in search:
            file_path = search.split('=')[1]
            data = pd.read_csv(file_path)
            _, _, _ = wrangle(file_path)
            dropdown_options = [{'label': col, 'value': col} for col in data.columns]
            return dropdown_options, dropdown_options, dropdown_options, dropdown_options, dropdown_options, dropdown_options, dropdown_options, dropdown_options, dropdown_options
        else:
            return [], [], [], [], [], [], [], [], []

    return app
