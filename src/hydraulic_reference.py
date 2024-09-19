import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import math

# Initialize the app with a Bootstrap stylesheet for styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the server variable for deployment
server = app.server

# Landing page layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Liquid Hydraulic Reference Tool", className="text-center my-4"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Pipeline Volume", id="pipeline-volume-btn", color="primary", className="m-2", size='lg'),
            dbc.Button("Reynolds Number & Velocity", id="reynolds-number-btn", color="secondary", className="m-2", size='lg'),
            dbc.Button("Friction Factor", id="friction-factor-btn", color="success", className="m-2", size='lg'),
            dbc.Button("Energy Needs", id="energy-needs-btn", color="warning", className="m-2", size='lg'),
            dbc.Button("Unit Conversions", id="unit-conversions-btn", color="info", className="m-2", size='lg'),
        ], className="text-center")
    ]),
    html.Hr(),
    html.Div(id='page-content')
], fluid=True)

# Callback to update the page content based on button clicks
@app.callback(
    Output('page-content', 'children'),
    [Input('pipeline-volume-btn', 'n_clicks'),
     Input('reynolds-number-btn', 'n_clicks'),
     Input('friction-factor-btn', 'n_clicks'),
     Input('energy-needs-btn', 'n_clicks'),
     Input('unit-conversions-btn', 'n_clicks')]
)
def display_page(pv_clicks, rn_clicks, ff_clicks, en_clicks, uc_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return html.Div()
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'pipeline-volume-btn':
        return pipeline_volume_layout()
    elif button_id == 'reynolds-number-btn':
        return reynolds_number_layout()
    elif button_id == 'friction-factor-btn':
        return friction_factor_layout()
    elif button_id == 'energy-needs-btn':
        return energy_needs_layout()
    elif button_id == 'unit-conversions-btn':
        return unit_conversions_layout()
    else:
        return html.Div()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

def pipeline_volume_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Pipeline Volume Calculator", className="text-center my-4"))),
        dbc.Row([
            dbc.Col([
                dbc.Label("Diameter (inches):"),
                dbc.Input(id='pv-diameter', type='number', value=24),
            ], width=4),
            dbc.Col([
                dbc.Label("Wall Thickness (inches):"),
                dbc.Input(id='pv-wall-thickness', type='number', value=0.5),
            ], width=4),
            dbc.Col([
                dbc.Label("Distance (miles):"),
                dbc.Input(id='pv-distance', type='number', value=10),
            ], width=4),
        ], className="mb-3"),
        dbc.Button('Calculate', id='pv-calculate-btn', color='primary'),
        html.Hr(),
        html.Div(id='pv-output')
    ], fluid=True)

@app.callback(
    Output('pv-output', 'children'),
    Input('pv-calculate-btn', 'n_clicks'),
    State('pv-diameter', 'value'),
    State('pv-wall-thickness', 'value'),
    State('pv-distance', 'value')
)
def calculate_pipeline_volume(n_clicks, diameter, wall_thickness, distance):
    if n_clicks:
        # Calculations
        inner_diameter = diameter - 2 * wall_thickness  # inches
        radius = inner_diameter / 2  # inches
        area = math.pi * (radius ** 2)  # square inches
        area_sqft = area / 144  # square feet
        length_ft = distance * 5280  # feet
        volume_cuft = area_sqft * length_ft  # cubic feet
        volume_bbl = volume_cuft / 5.614583  # barrels (1 bbl = 5.614583 cubic feet)

        # Output
        return html.Div([
            html.H4("Results:"),
            html.P(f"Pipeline Volume: {volume_cuft:.2f} cubic feet"),
            html.P(f"Pipeline Volume: {volume_bbl:.2f} barrels")
        ])
    return ''

def reynolds_number_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Reynolds Number & Pipeline Velocity Calculator", className="text-center my-4"))),
        dbc.Row([
            dbc.Col([
                dbc.Label("Diameter (inches):"),
                dbc.Input(id='rn-diameter', type='number', value=24),
            ], width=4),
            dbc.Col([
                dbc.Label("Flow Rate (barrels per day):"),
                dbc.Input(id='rn-flow-rate', type='number', value=100000),
            ], width=4),
            dbc.Col([
                dbc.Label("Kinematic Viscosity (cSt):"),
                dbc.Input(id='rn-viscosity', type='number', value=1),
            ], width=4),
        ], className="mb-3"),
        dbc.Button('Calculate', id='rn-calculate-btn', color='primary'),
        html.Hr(),
        html.Div(id='rn-output')
    ], fluid=True)

@app.callback(
    Output('rn-output', 'children'),
    Input('rn-calculate-btn', 'n_clicks'),
    State('rn-diameter', 'value'),
    State('rn-flow-rate', 'value'),
    State('rn-viscosity', 'value')
)
def calculate_reynolds_number(n_clicks, diameter, flow_rate, viscosity):
    if n_clicks:
        # Calculations
        diameter_ft = diameter / 12  # feet
        area_sqft = math.pi * (diameter_ft / 2) ** 2  # square feet
        flow_rate_cfs = (flow_rate * 0.0238095) / 86400  # bbl/day to cubic feet per second
        velocity_fps = flow_rate_cfs / area_sqft  # feet per second
        diameter_m = diameter_ft * 0.3048  # meters
        velocity_mps = velocity_fps * 0.3048  # meters per second
        viscosity_m2s = viscosity * 1e-6  # cSt to m²/s
        reynolds_number = (velocity_mps * diameter_m) / viscosity_m2s

        # Output
        return html.Div([
            html.H4("Results:"),
            html.P(f"Pipeline Velocity: {velocity_fps:.2f} ft/s"),
            html.P(f"Reynolds Number: {reynolds_number:.2f}")
        ])
    return ''

def energy_needs_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Energy Needs Calculator", className="text-center my-4"))),
        dbc.Row([
            dbc.Col([
                dbc.Label("Pump Horsepower (HP):"),
                dbc.Input(id='en-horsepower', type='number', value=100),
            ], width=6),
        ], className="mb-3"),
        dbc.Button('Calculate', id='en-calculate-btn', color='primary'),
        html.Hr(),
        html.Div(id='en-output')
    ], fluid=True)

@app.callback(
    Output('en-output', 'children'),
    Input('en-calculate-btn', 'n_clicks'),
    State('en-horsepower', 'value')
)
def calculate_energy_needs(n_clicks, horsepower):
    if n_clicks:
        # Conversion
        kilowatts = horsepower * 0.7457  # 1 HP = 0.7457 kW

        # Output
        return html.Div([
            html.H4("Results:"),
            html.P(f"Energy Needed: {kilowatts:.2f} kW")
        ])
    return ''

def unit_conversions_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Unit Conversions", className="text-center my-4"))),
        dbc.Tabs([
            dbc.Tab(label='Degrees API to Specific Gravity', tab_id='tab-api-sg'),
            dbc.Tab(label='Pressure to Head (ft)', tab_id='tab-pressure-head'),
            dbc.Tab(label='Dynamic to Kinematic Viscosity', tab_id='tab-viscosity'),
        ], id='unit-tabs', active_tab='tab-api-sg'),
        html.Div(id='tab-content')
    ], fluid=True)

@app.callback(
    Output('tab-content', 'children'),
    Input('unit-tabs', 'active_tab')
)
def render_tab_content(active_tab):
    if active_tab == 'tab-api-sg':
        return api_to_sg_layout()
    elif active_tab == 'tab-pressure-head':
        return pressure_to_head_layout()
    elif active_tab == 'tab-viscosity':
        return viscosity_conversion_layout()
    return ''

@app.callback(
    Output('tab-content', 'children'),
    Input('unit-tabs', 'active_tab')
)
def render_tab_content(active_tab):
    if active_tab == 'tab-api-sg':
        return api_to_sg_layout()
    elif active_tab == 'tab-pressure-head':
        return pressure_to_head_layout()
    elif active_tab == 'tab-viscosity':
        return viscosity_conversion_layout()
    return ''

def pressure_to_head_layout():
    return html.Div([
        dbc.Label("Pressure (psi):"),
        dbc.Input(id='pressure-value', type='number', value=100),
        dbc.Label("Specific Gravity:", className='mt-2'),
        dbc.Input(id='pressure-sg', type='number', value=1),
        dbc.Button('Convert', id='pressure-convert-btn', color='primary', className='mt-2'),
        html.Div(id='pressure-output', className='mt-2')
    ])

@app.callback(
    Output('pressure-output', 'children'),
    Input('pressure-convert-btn', 'n_clicks'),
    State('pressure-value', 'value'),
    State('pressure-sg', 'value')
)
def convert_pressure_to_head(n_clicks, pressure, sg):
    if n_clicks:
        head_ft = (pressure * 2.31) / sg  # 1 psi = 2.31 ft head for water (SG=1)
        return html.P(f"Head: {head_ft:.2f} ft")
    return ''

def viscosity_conversion_layout():
    return html.Div([
        dbc.Label("Dynamic Viscosity (cP):"),
        dbc.Input(id='dynamic-viscosity', type='number', value=1),
        dbc.Label("Density (kg/m³):", className='mt-2'),
        dbc.Input(id='fluid-density', type='number', value=1000),
        dbc.Button('Convert', id='viscosity-convert-btn', color='primary', className='mt-2'),
        html.Div(id='viscosity-output', className='mt-2')
    ])

@app.callback(
    Output('viscosity-output', 'children'),
    Input('viscosity-convert-btn', 'n_clicks'),
    State('dynamic-viscosity', 'value'),
    State('fluid-density', 'value')
)
def convert_dynamic_to_kinematic(n_clicks, dynamic_viscosity, density):
    if n_clicks:
        kinematic_viscosity = (dynamic_viscosity / density) * 1e6  # cSt
        return html.P(f"Kinematic Viscosity: {kinematic_viscosity:.2f} cSt")
    return ''

def friction_factor_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Friction Factor Calculator", className="text-center my-4"))),
        # Input fields for friction factor calculation
        # Replace with actual inputs needed for your formulas
        html.P("Friction factor calculation inputs go here."),
        # Output placeholder
        html.Div(id='ff-output')
    ], fluid=True)
