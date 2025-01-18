# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 14:31:04 2024

@author: Controls and Callbacks
https://dash.plotly.com/tutorial
"""

from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
import calendar


app = Dash(__name__)
df = pd.read_csv("./Electricity.csv")
df.year = df.year.astype(str)

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Singapore Electricity Consumption Dashboard",
                    style={
                        "textAlign": "center",
                        "color": "#2c3e50",
                        "marginBottom": 10,
                    },
                ),
                html.P(
                    "Analyze electricity consumption patterns across different regions and dwelling types in Singapore",
                    style={
                        "textAlign": "center",
                        "color": "#7f8c8d",
                        "marginBottom": 30,
                    },
                ),
            ],
            style={
                "backgroundColor": "#f8f9fa",
                "padding": "20px",
                "borderRadius": "10px",
                "marginBottom": "20px",
            },
        ),
        html.Div(
            [
                html.H3(
                    "Select Filters", style={"marginBottom": "15px", "color": "#2c3e50"}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    "Region Filter",
                                    style={"fontWeight": "bold", "color": "#34495e"},
                                ),
                                dcc.Dropdown(
                                    id="region-filter",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in df["Region"].unique()
                                    ],
                                    value=None,
                                    placeholder="All Regions",
                                    style={"backgroundColor": "#fff"},
                                ),
                            ],
                            style={
                                "width": "30%",
                                "display": "inline-block",
                                "marginRight": "2%",
                            },
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Year Filter",
                                    style={"fontWeight": "bold", "color": "#34495e"},
                                ),
                                dcc.Dropdown(
                                    id="year-filter",
                                    options=[
                                        {"label": f"Year {i}", "value": i}
                                        for i in df["year"].unique()
                                    ],
                                    value=df["year"].iloc[0],
                                    placeholder="Select Year",
                                    style={"backgroundColor": "#fff"},
                                ),
                            ],
                            style={
                                "width": "30%",
                                "display": "inline-block",
                                "marginRight": "2%",
                            },
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Dwelling Type",
                                    style={"fontWeight": "bold", "color": "#34495e"},
                                ),
                                dcc.Dropdown(
                                    id="dwelling-filter",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in df["dwelling_type"].unique()
                                    ],
                                    value=None,
                                    placeholder="All Dwelling Types",
                                    style={"backgroundColor": "#fff"},
                                ),
                            ],
                            style={"width": "30%", "display": "inline-block"},
                        ),
                    ]
                ),
            ],
            style={
                "backgroundColor": "#ffffff",
                "padding": "20px",
                "borderRadius": "10px",
                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
                "marginBottom": "20px",
            },
        ),
        # Visualizations
        html.Div(
            [
                # Regional Analysis Card
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Regional Consumption Analysis",
                                    style={"color": "#2c3e50"},
                                ),
                                html.P(
                                    "Average electricity consumption across different regions",
                                    style={"color": "#7f8c8d", "marginBottom": "15px"},
                                ),
                                dcc.Graph(id="region-bar-chart"),
                            ],
                            style={
                                "backgroundColor": "#ffffff",
                                "padding": "20px",
                                "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
                            },
                        )
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "marginRight": "2%",
                    },
                ),
                # Monthly Trends Card
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Monthly Consumption Trends",
                                    style={"color": "#2c3e50"},
                                ),
                                html.P(
                                    "Track how electricity consumption changes over months",
                                    style={"color": "#7f8c8d", "marginBottom": "15px"},
                                ),
                                dcc.Graph(id="consumption-line-chart"),
                            ],
                            style={
                                "backgroundColor": "#ffffff",
                                "padding": "20px",
                                "borderRadius": "10px",
                                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
                            },
                        )
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        # Area Comparison Section
        html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Area-wise Monthly Consumption Comparison",
                            style={"color": "#2c3e50"},
                        ),
                        html.P(
                            "Compare electricity consumption patterns across different areas by month",
                            style={"color": "#7f8c8d", "marginBottom": "15px"},
                        ),
                        dcc.Graph(id="area-comparison-chart"),
                    ],
                    style={
                        "backgroundColor": "#ffffff",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
                    },
                )
            ],
            style={"marginBottom": "20px"},
        ),
        # Table Section
        html.Div(
            [
                html.H3("Detailed Statistics", style={"color": "#2c3e50"}),
                html.P(
                    "Comprehensive statistics breakdown by dwelling type",
                    style={"color": "#7f8c8d", "marginBottom": "15px"},
                ),
                dash_table.DataTable(
                    id="stats-table",
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "15px",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "fontSize": "14px",
                        "fontFamily": "Arial",
                    },
                    style_header={
                        "backgroundColor": "#f8f9fa",
                        "fontWeight": "bold",
                        "color": "#2c3e50",
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"}
                    ],
                    page_size=5,
                ),
            ],
            style={
                "backgroundColor": "#ffffff",
                "padding": "20px",
                "borderRadius": "10px",
                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)",
            },
        ),
    ],
    style={"padding": "20px", "backgroundColor": "#f0f2f5", "fontFamily": "Arial"},
)


def get_month_name(month_num):
    """To convert month number to names"""
    return calendar.month_abbr[int(month_num)]


@callback(Output("region-bar-chart", "figure"), [Input("year-filter", "value")])
def update_region_chart(selected_year):
    filtered_df = df[df["year"] == selected_year] if selected_year else df
    avg_by_region = filtered_df.groupby("Region")["kwh_per_acc"].mean().reset_index()

    fig = go.Figure(
        data=[
            go.Bar(
                x=avg_by_region["Region"],
                y=avg_by_region["kwh_per_acc"],
                marker_color="#3498db",
                hovertemplate="<b>Region:</b> %{x}<br>"
                + "<b>Consumption:</b> %{y:.1f} kWh<br><extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title={
            "text": f"Average Consumption by Region ({selected_year})",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Region",
        yaxis_title="Average kWh per Account",
        template="plotly_white",
        hoverlabel={"bgcolor": "white"},
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
    )

    return fig


@callback(
    Output("consumption-line-chart", "figure"),
    [Input("region-filter", "value"), Input("year-filter", "value")],
)
def update_line_chart(selected_region, selected_year):
    filtered_df = df.copy()
    if selected_region:
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]
    if selected_year:
        filtered_df = filtered_df[filtered_df["year"] == selected_year]

    # Convert month numbers to names and calculate averages
    monthly_avg = filtered_df.groupby("month")["kwh_per_acc"].mean().reset_index()
    monthly_avg["month_name"] = monthly_avg["month"].apply(get_month_name)

    # Check if we have data for all months
    available_months = set(monthly_avg["month"])
    all_months = set(range(1, 13))
    missing_months = all_months - available_months

    fig = go.Figure(
        data=[
            go.Scatter(
                x=monthly_avg["month_name"],
                y=monthly_avg["kwh_per_acc"],
                mode="lines+markers",
                line={"color": "#2ecc71", "width": 3},
                marker={"size": 8},
                hovertemplate="<b>Month:</b> %{x}<br>"
                + "<b>Consumption:</b> %{y:.1f} kWh<br><extra></extra>",
            )
        ]
    )

    title = "Monthly Consumption Trends"
    if selected_region:
        title += f" - {selected_region}"
    if selected_year:
        title += f" ({selected_year})"

    if missing_months:
        missing_months_names = [get_month_name(m) for m in sorted(missing_months)]
        title += f'<br><span style="font-size: 12px; color: #7f8c8d">No data available for: {", ".join(missing_months_names)}</span>'

    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Month",
        yaxis_title="Average kWh per Account",
        template="plotly_white",
        hoverlabel={"bgcolor": "white"},
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
    )

    return fig


@callback(
    Output("area-comparison-chart", "figure"),
    [
        Input("region-filter", "value"),
        Input("year-filter", "value"),
        Input("dwelling-filter", "value"),
    ],
)
def update_area_comparison(selected_region, selected_year, selected_dwelling):
    filtered_df = df.copy()

    if selected_region:
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]
    if selected_year:
        filtered_df = filtered_df[filtered_df["year"] == selected_year]
    if selected_dwelling:
        filtered_df = filtered_df[filtered_df["dwelling_type"] == selected_dwelling]

    fig = go.Figure()
    colors = px.colors.qualitative.Set3
    all_available_months = set()
    areas = filtered_df["dwelling_type"].unique()
    for area in areas:
        area_data = filtered_df[filtered_df["dwelling_type"] == area]
        months_in_area = set(area_data["month"])
        all_available_months.update(months_in_area)

    all_months = set(range(1, 13))
    missing_months = all_months - all_available_months

    for i, area in enumerate(areas):
        area_data = filtered_df[filtered_df["dwelling_type"] == area]
        monthly_avg = area_data.groupby("month")["kwh_per_acc"].mean().reset_index()
        monthly_avg["month_name"] = monthly_avg["month"].apply(get_month_name)

        fig.add_trace(
            go.Scatter(
                x=monthly_avg["month_name"],
                y=monthly_avg["kwh_per_acc"],
                name=area,
                mode="lines+markers",
                line={"width": 3},
                marker={"size": 8},
                hovertemplate="<b>Area:</b> "
                + area
                + "<br>"
                + "<b>Month:</b> %{x}<br>"
                + "<b>Consumption:</b> %{y:.1f} kWh<br><extra></extra>",
                line_color=colors[i % len(colors)],
            )
        )

    title = "Monthly Consumption Comparison by Area"
    if selected_region:
        title += f" - {selected_region}"
    if selected_year:
        title += f" ({selected_year})"

    if missing_months:
        missing_months_names = [get_month_name(m) for m in sorted(missing_months)]
        title += f'<br><span style="font-size: 12px; color: #7f8c8d">No data available for: {", ".join(missing_months_names)}</span>'

    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Month",
        yaxis_title="Average kWh per Account",
        template="plotly_white",
        height=500,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.3,
            "xanchor": "center",
            "x": 0.5,
        },
        showlegend=True,
        hoverlabel={"bgcolor": "white"},
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@callback(
    Output("stats-table", "data"),
    [
        Input("region-filter", "value"),
        Input("year-filter", "value"),
        Input("dwelling-filter", "value"),
    ],
)
def update_stats_table(selected_region, selected_year, selected_dwelling):
    filtered_df = df.copy()
    if selected_region:
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]
    if selected_year:
        filtered_df = filtered_df[filtered_df["year"] == selected_year]
    if selected_dwelling:
        filtered_df = filtered_df[filtered_df["dwelling_type"] == selected_dwelling]

    stats = (
        filtered_df.groupby("dwelling_type")
        .agg({"kwh_per_acc": ["mean", "min", "max", "count"]})
        .reset_index()
    )

    stats.columns = [
        "Dwelling Type",
        "Average kWh",
        "Min kWh",
        "Max kWh",
        "Number of Records",
    ]
    stats = stats.round(2)

    return stats.to_dict("records")


if __name__ == "__main__":
    app.run(debug=True)
