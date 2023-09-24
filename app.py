from dash import Dash
from dash import dcc
from dash import html
import os
import sys
import pandas as pd
import wk_progress_review

debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True


if os.environ.get("APIKEY"):
    apikey = os.environ["APIKEY"]
else:
    print("Need to set Environment Var APIKEY")
    sys.exit(1)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

wk_progress_review.main(apikey)

level_data = pd.read_csv("Data/level_data.csv")

progress_data = pd.read_csv("Data/progress_data.csv")
graph_data = []

for i,subject_type in enumerate(("radical","kanji","vocab")):
    fig_data = []

    for time in ("Unlock_times","Start_times","Passed_times"):
        tmp_data = progress_data.query(f"Subject == '{subject_type}' and Des == '{time}'")
        fig_data.append({
            "x": tmp_data["Date"],
            "y": tmp_data["CumSum"],
            "type": "lines",
            "name": time
        })

    tmp_graph = dcc.Graph(
                        id=f"{subject_type}",
                        config={"displayModeBar": False},
                        figure={
                            "data": fig_data[:],
                            "layout": {
                                "title": {
                                    "text": f"{subject_type}",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                            },
                        },
                    )
    
    graph_data.append(tmp_graph)
        

app.title = "Avocado Analytics: Understand Your Avocados!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🐢", className="header-emoji"),
                html.H1(
                    children="WaniKani Analytics", className="header-title"
                ),
                html.P(
                    children="Analysis of WaniKani data. See how you've progressed in level and how much you've learned",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="level-data",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": level_data["Level"],
                                    "y": level_data["Time_seconds"]/(60*60*24),
                                    "type": "bar",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Time Per Level",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True, 'title':'Level'},
                                "yaxis": {"fixedrange": True, 'title':'Days'},
                                "colorway": ["#17B897"],
                            },
                        },
                    ),
                    className="card",
                ),
                html.Div(
                    children=graph_data,
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port="8050",debug=debug)
