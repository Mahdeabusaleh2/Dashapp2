import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Radiation exposure data (in millisieverts, mSv)
radiation_sources = {
    "Background Radiation (Annual Avg)": 3.0,
    "Chest X-ray": 0.1,
    "Dental X-ray": 0.005,
    "Mammogram": 0.4,
    "CT Scan (Abdomen)": 8.0,
    "Flight (NYC to LA)": 0.04,
    "Smoking (1 pack/day, Annual)": 70.0,
    "Fukushima Evacuation Zone (Annual)": 12.0,
}

df = pd.DataFrame(list(radiation_sources.items()), columns=["Source", "Dose (mSv)"])

# Define dose values and models
dose_values = np.linspace(0, 100, 100)

# Mathematical models
def supra_linear_model(dose):
    return 0.015 * dose ** 1.5

def lnt_model(dose):
    return 0.01 * dose

def linear_quadratic_model(dose):
    return 0.005 * dose + 0.0001 * dose ** 2

def hormesis_model(dose):
    return np.where(dose < 20, -0.005 * dose + 0.0002 * dose ** 2, 0.01 * dose)

def linear_threshold_model(dose, threshold=50):
    return np.where(dose < threshold, 0, 0.01 * (dose - threshold))

# Generate risk values
supra_risk = supra_linear_model(dose_values)
lnt_risk = lnt_model(dose_values)
lq_risk = linear_quadratic_model(dose_values)
hormesis_risk = hormesis_model(dose_values)
threshold_risk = linear_threshold_model(dose_values)

# Layout for the app
app.layout = html.Div(
    style={'backgroundColor': 'white', 'padding': '20px'},
    children=[
        html.H1("Radiation Realities: Where does it come from and how does it affect me?", 
               style={'textAlign': 'center'}),
        html.H5("Mahde Abusaleh, David Capobianco, Kristin Cotton, Andrea Harper, Nickolas Schachtsick, Ryan Spartz", 
               style={'textAlign': 'center', 'marginBottom': 20, 'color': 'gray'}),

        # Navigation Bar
        html.Div([
            html.A('Exposure Sources | ', href='#exposure', style={'cursor': 'pointer', 'textDecoration': 'none'}),
            html.A('Dose-Response Model | ', href='#models', style={'cursor': 'pointer', 'textDecoration': 'none'}),
            html.A('Calculator | ', href='#calculator', style={'cursor': 'pointer', 'textDecoration': 'none'}),
            html.A('FAQ | ', href='#faq', style={'cursor': 'pointer', 'textDecoration': 'none'}),
            html.A('Conclusion', href='#conclusion', style={'cursor': 'pointer', 'textDecoration': 'none'})
        ], style={'textAlign': 'center', 'marginBottom': 20}),

        # Introduction Section
        html.Div(id="introduction", children=[
            html.H3("Introduction"),
            html.P("""
                Radiation – the word sounds scary. But what is it really? Would it surprise you to know that you experience radiation every day? 
                Radiation can be broadly defined as energy that travels in waves or particles. Radiation is typically broken down into two categories.
            """),
            html.P("""
                Non-Ionizing Radiation is low energy in nature, so it is generally safe. This type of radiation shows up in your everyday life 
                as microwaves, radio waves, and visible light.
            """),
            html.P("""
                The higher energy of Ionizing Radiation allows it to kick out electrons from an atom. X-rays and gamma rays (and some UV rays) 
                are examples of ionizing radiation. This type of radiation can be potentially harmful to a human. We experience these types of 
                radiation usually only in special situations.
            """),
            html.P("""
                Low-dose radiation is defined as exposure below 100 mSv (short-term) or 10 mSv/year (prolonged). 
                Supported by UNSCEAR and ICRP.
            """),
            html.P("""
                We are exposed to low levels of X-rays when we have an x-ray image of our bones. CAT scans and Mammograms also use X-rays to image our bodies.
            """),
        ]),

        # Radiation Exposure Section
        html.Div(id='exposure', children=[
            html.H3("Radiation Exposure from Common Sources"),
            dcc.Graph(
                figure={
                    "data": [go.Bar(x=df["Source"], y=df["Dose (mSv)"], marker_color='blue')],
                    "layout": go.Layout(title="Radiation Dose Comparison (mSv)", 
                                      xaxis_title="Source",
                                      yaxis_title="Dose (mSv)")
                }
            ),
            html.P("The chart above compares radiation doses from common sources, providing insight into relative exposure levels."),
        ]),

        # Dose-Response Model Section
        html.Div(id='models', children=[
            html.H3("Dose-Response Models"),
            dcc.Graph(
                figure={
                    "data": [
                        go.Scatter(x=dose_values, y=supra_risk, mode='lines', name='Supra-linear',
                                 line=dict(color='black', dash='dash')),
                        go.Scatter(x=dose_values, y=lnt_risk, mode='lines', name='Linear No-Threshold (LNT)',
                                 line=dict(color='green')),
                        go.Scatter(x=dose_values, y=lq_risk, mode='lines', name='Linear-Quadratic',
                                 line=dict(color='blue', dash='dash')),
                        go.Scatter(x=dose_values, y=hormesis_risk, mode='lines', name='Hormesis',
                                 line=dict(color='red', dash='dot')),
                        go.Scatter(x=dose_values, y=threshold_risk, mode='lines', name='Linear Threshold',
                                 line=dict(color='black')),
                    ],
                    "layout": go.Layout(
                        title="Radiation Dose-Response Models",
                        xaxis_title="Radiation Dose (mSv)",
                        yaxis_title="Relative Risk",
                        legend=dict(x=0.7, y=0.1)
                    )
                }
            ),
            html.Div([
                html.H4("Model Descriptions"),
                html.Ul([
                    html.Li(html.Strong("Supra-linear: "), "Risk increases more steeply at low doses."),
                    html.Li(html.Strong("LNT: "), "Risk is proportional to dose with no safe threshold."),
                    html.Li(html.Strong("Linear-Quadratic: "), "Linear at low doses, quadratic at high doses."),
                    html.Li(html.Strong("Hormesis: "), "Low doses may be beneficial."),
                    html.Li(html.Strong("Linear Threshold: "), "No risk below a threshold (e.g., 50 mSv)."),
                ]),
                html.P("""
                    Controversy: Low-dose effects are debated due to challenges in distinguishing risks from background radiation. 
                    Models vary based on dose, duration, and individual sensitivity. (Source: Seong et al., 2016)
                """, style={'color': 'gray', 'fontSize': 14}),
            ]),
        ]),

        # Calculator Section
        html.Div(id='calculator', children=[
            html.H3("Radiation Dose Calculator"),
            html.P("Number of cross-country flights (NYC-LA):"),
            dcc.Slider(id='flight-slider', min=0, max=50, value=0, marks={i: str(i) for i in range(0, 51, 5)}),
            html.P("Number of chest X-rays:"),
            dcc.Slider(id='xray-slider', min=0, max=20, value=0, marks={i: str(i) for i in range(0, 21, 5)}),
            html.Div(id='total-dose-output', style={'marginTop': 20})
        ]),

        # FAQ Section
        html.Div(id='faq', children=[
            html.H3("Frequently Asked Questions (FAQ)"),
            html.Details([
                html.Summary("Why are there different models for radiation risk?"),
                html.P("""
                    Multiple models exist because low-dose effects are hard to study and may vary based on 
                    individual sensitivity, dose rate, and biological factors. The LNT model is conservative and widely used, 
                    while others like Hormesis remain controversial.
                """),
            ]),
            html.Details([
                html.Summary("What are Sv and mSv?"),
                html.P("Sv = Sievert, which is 1 Joule per kilogram. This is the international system unit for dose equivalent. "
                       "mSv = millisievert, which is 1/1000 of a Sv."),
                html.P(["Source: U.S. NRC Glossary. ", 
                        html.A("Learn more", href="https://www.nrc.gov/reading-rm/basic-ref/glossary/sievert-sv.html", target="_blank")])
            ]),
            # ... (keep other existing FAQ items)
        ]),

        # References Section
        html.Div(id='references', children=[
            html.H3("References"),
            html.Ul([
                html.Li("Seong KM, et al. Is the Linear No-Threshold Dose-Response Paradigm Still Necessary?. J Korean Med Sci. 2016. ",
                       html.A("DOI:10.3346/jkms.2016.31.S1.S10", 
                              href="https://doi.org/10.3346/jkms.2016.31.S1.S10", target="_blank")),
                # ... (keep other existing references)
            ]),
        ]),

        # ... (keep existing Conclusion and Video sections)
    ]
)

# Callback for radiation dose calculator
@app.callback(
    Output("total-dose-output", "children"),
    [Input("flight-slider", "value"), Input("xray-slider", "value")]
)
def update_dose(flights, xrays):
    total_dose = (flights * 0.04) + (xrays * 0.1)
    return f"Your estimated annual radiation dose from selected activities: {total_dose:.2f} mSv"

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host="0.0.0.0", port=port)
