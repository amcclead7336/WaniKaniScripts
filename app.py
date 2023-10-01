from dash import Dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import plotly as py
import plotly.express as px
import os
import sys
import json
import pandas as pd
import wk_progress_review

debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True


if os.environ.get("APIKEY"):
    apikey = os.environ["APIKEY"]
else:
    print("Need to set Environment Var APIKEY")
    sys.exit(1)

# debug = True
# with open("wk_apikey.txt") as f:
#     apikey=f.read().strip()

AUTH_HEADER = {"Authorization":f"Bearer {apikey}"}

wk_progress_review.create_dir("Store")

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

level_data, avg_level_time = wk_progress_review.collect_level_data(AUTH_HEADER)
progress_data, total_series = wk_progress_review.collect_progress_data(AUTH_HEADER)
vlines = wk_progress_review.create_level_lines()

level_fig = px.bar(x=level_data["Level"], y= level_data["Time_seconds"]/(60*60*24), title="Time Spent per Level", labels={"x":"Level","y":"Time in Days"})

progress_fig = px.line(progress_data, x="Date",y="CumSum",color="Subject", title="Progress per Subject", labels={"x":"Time","y":"Characters"})
progress_fig.add_trace(go.Line(x=total_series.index, y=total_series.values, name="Total"))
for vline in vlines:
    progress_fig.add_vline(x=vline, line_color="grey", line_dash="dash")


radical_df, kanji_df = wk_progress_review.create_gantt_data(AUTH_HEADER)
rad_gantt_fig = px.timeline(radical_df, x_start="Start",x_end="Finish",y="Resource", color="Color")
kanji_gantt_fig = px.timeline(kanji_df, x_start="Start",x_end="Finish",y="Resource", color="Color")

app.title = "WaniKani Analytics: Understand Your WaniKani!"

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
                    children=[ 
                        dcc.Graph(
                        id="level_fig",
                        config={"displayModeBar": False},
                        figure=level_fig,
                    ),
                        html.P(children=f"Average time to complete Level: {avg_level_time}"),
                        
                    ],
                    className="card",
                ),

                html.Div(
                    children=dcc.Graph(
                        id="progress_fig",
                        config={"displayModeBar": False},
                        figure=progress_fig,
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="Radical_Gantt",
                        config={"displayModeBar": False},
                        figure=rad_gantt_fig,
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="Kanji_Gantt",
                        config={"displayModeBar": False},
                        figure=kanji_gantt_fig,
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port="8050", debug=debug)