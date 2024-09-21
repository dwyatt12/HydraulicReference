# Import necessary libraries
import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import math
from scipy.optimize import fsolve
from math import log, sqrt
import plotly.graph_objs as go

# Initialize the app with a dark Bootstrap stylesheet for styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)

# Define the server variable for deployment
server = app.server

# Landing page layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("💧 Liquid Hydraulic Reference Tool", className="text-center my-4 text-light"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Pipeline Volume", id="pipeline-volume-btn", color="primary", className="m-2", size='lg'),
            dbc.Button("Fluid Flow", id="friction-factor-btn", color="success", className="m-2", size='lg'),
            dbc.Button("Power & Energy", id="energy-needs-btn", color="warning", className="m-2", size='lg'),
            dbc.Button("Unit Conversions", id="unit-conversions-btn", color="info", className="m-2", size='lg'),
        ], className="text-center")
    ]),
    html.Hr(className="my-4"),
    html.Div(id='page-content')
], fluid=True, className="bg-dark")

# Callback to update the page content based on button clicks
@app.callback(
    Output('page-content', 'children'),
    [Input('pipeline-volume-btn', 'n_clicks'),
     Input('friction-factor-btn', 'n_clicks'),
     Input('energy-needs-btn', 'n_clicks'),
     Input('unit-conversions-btn', 'n_clicks')]
)
def display_page(pv_clicks, ff_clicks, en_clicks, uc_clicks):
    ctx = callback_context

    if not ctx.triggered:
        return html.Div()
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'pipeline-volume-btn':
        return pipeline_volume_layout()
    elif button_id == 'friction-factor-btn':
        return friction_factor_layout()
    elif button_id == 'energy-needs-btn':
        return energy_needs_layout()
    elif button_id == 'unit-conversions-btn':
        return unit_conversions_layout()
    else:
        return html.Div()

# Pipeline Volume Calculator Layout and Callback
def pipeline_volume_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Pipeline Volume Calculator", className="text-center my-4 text-light"))),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Diameter:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='pv-diameter', type='text', value="{:,}".format(24), className="mb-2"),
                            dbc.InputGroupText("inches")
                        ]),
                        dbc.Label("Wall Thickness:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='pv-wall-thickness', type='text', value="{:,}".format(0.5), className="mb-2"),
                            dbc.InputGroupText("inches")
                        ]),
                        dbc.Label("Distance:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='pv-distance', type='text', value="{:,}".format(10), className="mb-2"),
                            dbc.InputGroupText("miles")
                        ]),
                        dbc.Button('Calculate', id='pv-calculate-btn', color='primary', className="mt-3"),
                    ])
                ], className="mb-4"),
                width=6
            )
        ], justify='center'),
        html.Hr(className="my-4"),
        html.Div(id='pv-output', className="text-light")
    ], fluid=True, className="bg-dark")

@app.callback(
    Output('pv-output', 'children'),
    Input('pv-calculate-btn', 'n_clicks'),
    State('pv-diameter', 'value'),
    State('pv-wall-thickness', 'value'),
    State('pv-distance', 'value')
)
def calculate_pipeline_volume(n_clicks, diameter, wall_thickness, distance):
    if n_clicks:
        # Remove commas and convert to float
        diameter = float(diameter.replace(',', ''))
        wall_thickness = float(wall_thickness.replace(',', ''))
        distance = float(distance.replace(',', ''))

        # Calculations
        inner_diameter = diameter - 2 * wall_thickness  # inches
        radius = inner_diameter / 2  # inches
        area = math.pi * (radius ** 2)  # square inches
        area_sqft = area / 144  # square feet
        length_ft = distance * 5280  # feet
        volume_cuft = area_sqft * length_ft  # cubic feet
        volume_bbl = volume_cuft / 5.614583  # barrels (1 bbl = 5.614583 cubic feet)

        # Format outputs with commas
        volume_cuft_formatted = "{:,}".format(round(volume_cuft, 2))
        volume_bbl_formatted = "{:,}".format(round(volume_bbl, 2))

        # Output
        return html.Div([
            html.H4("Results:", className="text-light"),
            html.P(f"Pipeline Volume: {volume_cuft_formatted} cubic feet"),
            html.P(f"Pipeline Volume: {volume_bbl_formatted} barrels")
        ])
    return ''

def determine_flow_regime(reynolds_number):
    if reynolds_number > 4000:
        return 'Turbulent'
    elif 2000 <= reynolds_number <= 4000:
        return 'Transition'
    else:
        return 'Laminar'

# Friction Factor Calculator Layout and Callback
def friction_factor_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Friction Factor Calculator", className="text-center my-4 text-light"))),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Diameter:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='ff-diameter', type='text', value="{:,}".format(12), className="mb-2"),
                            dbc.InputGroupText("inches")
                        ]),
                        dbc.Label("Flow Rate:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='ff-flow-rate', type='text', value="{:,}".format(100000), className="mb-2"),
                            dbc.InputGroupText("barrels per day")
                        ]),
                        dbc.Label("Roughness:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='ff-roughness-ft', type='text', value="{:,.5f}".format(0.00015), className="mb-2"),
                            dbc.InputGroupText("feet")
                        ]),
                        dbc.Label("Kinematic Viscosity:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='ff-viscosity', type='text', value="{:,}".format(3.6), className="mb-2"),
                            dbc.InputGroupText("cSt")
                        ]),
                        dbc.Label("Specific Gravity:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='ff-specific-gravity', type='text', value="{:,}".format(0.84), className="mb-2"),
                        ]),
                        dbc.Label("Drag Reduction:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='ff-drag-reduction', type='', value="0%", className="mb-2"),
                            dbc.InputGroupText("%")
                        ]),
                        dbc.Button('Calculate', id='ff-calculate-btn', color='primary', className="mt-3"),
                    ])
                ], className="mb-4"),
                width=6
            )
        ], justify='center'),
        html.Hr(className="my-4"),
        html.Div(id='ff-output', className="text-light")
    ], fluid=True, className="bg-dark")

@app.callback(
    Output('ff-output', 'children'),
    Input('ff-calculate-btn', 'n_clicks'),
    State('ff-diameter', 'value'),
    State('ff-flow-rate', 'value'),
    State('ff-roughness-ft', 'value'),
    State('ff-specific-gravity', 'value'),
    State('ff-viscosity', 'value'),
    State('ff-drag-reduction', 'value')
)
def calculate_friction_factor(n_clicks, diameter_in, flow_rate_bpd, roughness_ft, specific_gravity, viscosity_cst, drag_reduction):
    if n_clicks:
        # Remove commas and convert to float
        diameter_in = float(diameter_in.replace(',', ''))
        flow_rate_bpd = float(flow_rate_bpd.replace(',', ''))
        roughness_ft = float(roughness_ft.replace(',', ''))
        specific_gravity = float(specific_gravity.replace(',', ''))
        viscosity_cst = float(viscosity_cst.replace(',', ''))
        drag_reduction = float(drag_reduction.replace('%',''))/100

        # Convert inputs to consistent units
        diameter_ft = diameter_in / 12  # Convert diameter to feet
        diameter_m = diameter_ft * 0.3048  # Convert diameter to meters
        area_sqft = math.pi * (diameter_ft / 2) ** 2  # Cross-sectional area in square feet
        flow_rate_cfs = (flow_rate_bpd * 5.614583) / (24 * 3600)  # Convert flow rate to cubic feet per second
        velocity_fps = flow_rate_cfs / area_sqft  # Velocity in feet per second
        velocity_mps = velocity_fps * 0.3048  # Velocity in meters per second
        viscosity_m2s = viscosity_cst * 1e-6  # Kinematic viscosity in m²/s
        reynolds_number = (velocity_mps * diameter_m) / viscosity_m2s

        # Friction Factor Calculations
        methods = {}
        # Colebrook-White equation using fsolve
        def colebrook(f):
            return 1.0 / math.sqrt(f) + 2.0 * math.log10(roughness_ft / 3.7 + 2.51 / (reynolds_number * math.sqrt(f)))
        initial_guess = 0.02
        friction_factor_cw = fsolve(colebrook, initial_guess)[0]
        methods['Colebrook-White'] = friction_factor_cw

        # Swamee-Jain equation
        friction_factor_sj = 0.25 / (math.log10(roughness_ft / 3.7 + 5.74 / (reynolds_number ** 0.9))) ** 2
        methods['Swamee-Jain'] = friction_factor_sj

        # Alternate Method (Using Swamee-Jain again for demonstration)
        methods['Alternate Method'] = friction_factor_sj

        # Pressure Loss Calculations (Darcy-Weisbach equation)
        # Pressure loss per mile in psi
        pressure_losses = {}
        for method, f in methods.items():
            # Darcy-Weisbach equation: ΔP = f * (L/D) * (ρ * v^2 / 2)
            # For pressure loss per mile, L = 5280 ft
            # ρ (density) of water at room temperature = 62.4 lb/ft³
            # Convert pressure loss from lb/ft² to psi (1 psi = 144 lb/ft²)
            L = 5280  # Length in feet (1 mile)
            D = diameter_ft  # Diameter in feet
            v = velocity_fps  # Velocity in ft/s
            g = 32.17405 # Gravitational acceleration in ft/s^2
            head_loss = L * f * (v ** 2) / (D * 2 * g)
            delta_p_psi = head_loss * specific_gravity / 2.31
            pressure_losses[method] = delta_p_psi * (1 - drag_reduction)

        # Create Bar Chart
        fig = go.Figure(data=[
            go.Bar(
                name=method,
                x=[method],
                y=[pressure_losses[method]],
                text=[f"{pressure_losses[method]:,.1f} psi"],
                textposition='auto'
            )
            for method in methods.keys()
        ])

        fig.update_layout(
            title='Friction Factor Comparison',
            xaxis_title='Method',
            yaxis_title='Pressure Loss (psi)',
            template='plotly_dark',
            showlegend=False
        )

        # Output
        return html.Div([
            html.H4(f"Flow Details", className="text-white"),
            html.Ul([
                html.Li(f"Velocity: {velocity_fps:,.1f} ft/s"),
                html.Li(f"Reynolds Number: {reynolds_number:,.0f}"),
                html.Li(f"Flow Regime: {determine_flow_regime(reynolds_number)}")
            ]),
            html.Hr(),
            html.H4("Friction Factors", className="text-white"),
            html.Ul([html.Li(f"{method}: {f:.6f}") for method, f in methods.items()]),
            html.Hr(),
            html.H4(f"Pressure Loss per Mile (at {drag_reduction:.0%} DR)", className="text-white"),
            dcc.Graph(figure=fig)
        ])
    return ''

# Energy Needs Calculator Layout and Callback
def current_ideal(P, V, phase=3, PF=1):
    if phase not in (1, 3):
        raise ValueError('Only 1 and 3 phase power supported')
    if phase == 3:
        return (P * 1000) / (V * sqrt(3) * PF)
    else:
        return (P * 1000) / (V * PF)

def energy_needs_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Power & Energy", className="text-center my-4 text-light"))),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Power (kW):", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='en-power', type='number', value=750, className="mb-2"),
                            dbc.InputGroupText("kW")
                        ]),
                        dbc.Label("Voltage (Volts):", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='en-voltage', type='number', value=220, className="mb-2"),
                            dbc.InputGroupText("V")
                        ]),
                        dbc.Label("Phase:", className="text-white"),
                        dcc.Dropdown(
                            id='en-phase',
                            options=[
                                {'label': 'Single-phase', 'value': 1},
                                {'label': 'Three-phase', 'value': 3},
                            ],
                            value=3,  # Default to three-phase
                            className="mb-2"
                        ),
                        dbc.Label("Power Factor:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='en-pf', type='number', value=.98, className="mb-2"),
                            dbc.InputGroupText("")
                        ]),
                        dbc.Button('Calculate', id='en-calculate-btn', color='primary', className="mt-3"),
                    ])
                ], className="mb-4"),
                width=6
            )
        ], justify='center'),
        html.Hr(className="my-4"),
        html.Div(id='en-output', className="text-light")
    ], fluid=True, className="bg-dark")

@app.callback(
    Output('en-output', 'children'),
    Input('en-calculate-btn', 'n_clicks'),
    State('en-power', 'value'),
    State('en-voltage', 'value'),
    State('en-phase', 'value'),
    State('en-pf', 'value')
)
def calculate_energy_needs(n_clicks, power, voltage, phase, power_factor):
    if n_clicks:
        # Perform the current calculation using the provided current_ideal function
        current = current_ideal(P=power, V=voltage, phase=phase, PF=power_factor)

        # Format output
        current_formatted = "{:.2f}".format(current)

        # Output the calculated current
        return html.Div([
            html.H4("Results:", className="text-light"),
            html.P(f"Calculated Current: {current_formatted} A"),
            html.P("Does not include power used by the motor’s fan, or starter, or internal losses.")
        ])
    return ''

# Unit Conversions Layout and Callbacks
def unit_conversions_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Unit Conversions", className="text-center my-4 text-light"))),
        dbc.Tabs([
            dbc.Tab(label='Degrees API to Specific Gravity', tab_id='tab-api-sg'),
            dbc.Tab(label='Pressure to Head (ft)', tab_id='tab-pressure-head'),
            dbc.Tab(label='Dynamic to Kinematic Viscosity', tab_id='tab-viscosity'),
        ], id='unit-tabs', active_tab='tab-api-sg', className="mb-3"),
        html.Div(id='tab-content')
    ], fluid=True, className="bg-dark")

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

# Degrees API to Specific Gravity Layout
def api_to_sg_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Degrees API:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='api-value', type='number', value=30, className="mb-2"),
                            dbc.InputGroupText("°API")
                        ]),
                        dbc.Label("Specific Gravity:", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='sg-value', type='number', value=0.876, className="mb-2"),
                            dbc.InputGroupText("")
                        ]),
                        dbc.Alert(id='api-error-message', color='danger', dismissable=True, is_open=False, className='mt-2'),
                    ])
                ], className="mb-4"),
                width=4
            )
        ], justify='center')
    ], fluid=True, className="bg-dark")

# Bidirectional conversion between API and SG with error handling
@app.callback(
    [Output('api-value', 'value'),
     Output('sg-value', 'value'),
     Output('api-error-message', 'children'),
     Output('api-error-message', 'is_open')],
    [Input('api-value', 'value'),
     Input('sg-value', 'value')]
)
def convert_api_to_sg(api, sg):
    ctx = callback_context
    error_message = ''
    is_open = False
    if not ctx.triggered:
        return api, sg, error_message, is_open
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            if input_id == 'api-value':
                if api is None:
                    error_message = 'Please enter a valid API value.'
                    is_open = True
                    return api, sg, error_message, is_open
                # Convert from API to SG
                sg = 141.5 / (131.5 + api)
                return api, round(sg, 4), error_message, is_open
            elif input_id == 'sg-value':
                if sg is None or sg == 0:
                    error_message = 'Specific Gravity cannot be zero.'
                    is_open = True
                    return api, sg, error_message, is_open
                # Convert from SG to API
                api = 141.5 / sg - 131.5
                return round(api, 2), sg, error_message, is_open
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            is_open = True
            return api, sg, error_message, is_open
    return api, sg, error_message, is_open

# Pressure to Head Layout
def pressure_to_head_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Pressure (psi):", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='pressure-value', type='number', value=100, className="mb-2"),
                            dbc.InputGroupText("psi")
                        ]),
                        dbc.Label("Head (ft):", className='text-white'),
                        dbc.InputGroup([
                            dbc.Input(id='head-value', type='number', value=231, className="mb-2"),
                            dbc.InputGroupText("ft")
                        ]),
                        dbc.Label("Specific Gravity:", className='mt-2 text-white'),
                        dbc.InputGroup([
                            dbc.Input(id='pressure-sg', type='number', value=1, className="mb-2"),
                        ]),
                        dbc.Alert(id='pressure-error-message', color='danger', dismissable=True, is_open=False, className='mt-2'),
                    ])
                ], className="mb-4"),
                width=4
            )
        ], justify='center')
    ], fluid=True, className="bg-dark")

# Bidirectional conversion between Pressure and Head with error handling
@app.callback(
    [Output('pressure-value', 'value'),
     Output('head-value', 'value'),
     Output('pressure-error-message', 'children'),
     Output('pressure-error-message', 'is_open')],
    [Input('pressure-value', 'value'),
     Input('head-value', 'value'),
     Input('pressure-sg', 'value')]
)
def convert_pressure_to_head(pressure, head, sg):
    ctx = callback_context
    error_message = ''
    is_open = False
    if not ctx.triggered:
        return pressure, head, error_message, is_open
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            if sg is None or sg == 0:
                error_message = 'Specific Gravity cannot be zero.'
                is_open = True
                return pressure, head, error_message, is_open
            if input_id == 'pressure-value':
                if pressure is None:
                    error_message = 'Please enter a valid pressure value.'
                    is_open = True
                    return pressure, head, error_message, is_open
                # Convert pressure to head
                head = (pressure * 2.31) / sg
                return pressure, round(head, 2), error_message, is_open
            elif input_id == 'head-value':
                if head is None:
                    error_message = 'Please enter a valid head value.'
                    is_open = True
                    return pressure, head, error_message, is_open
                # Convert head to pressure
                pressure = (head * sg) / 2.31
                return round(pressure, 2), head, error_message, is_open
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            is_open = True
            return pressure, head, error_message, is_open
    return pressure, head, error_message, is_open

# Dynamic to Kinematic Viscosity Layout
def viscosity_conversion_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Dynamic Viscosity (cP):", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='dynamic-viscosity', type='number', value=1, className="mb-2"),
                            dbc.InputGroupText("cP")
                        ]),
                        dbc.Label("Kinematic Viscosity (cSt):", className="text-white"),
                        dbc.InputGroup([
                            dbc.Input(id='kinematic-viscosity', type='number', value=1, className="mb-2"),
                            dbc.InputGroupText("cSt")
                        ]),
                        dbc.Label("Density (kg/m³):", className='mt-2 text-white'),
                        dbc.InputGroup([
                            dbc.Input(id='fluid-density', type='number', value=1000, className="mb-2"),
                        ]),
                        dbc.Alert(id='viscosity-error-message', color='danger', dismissable=True, is_open=False, className='mt-2'),
                    ])
                ], className="mb-4"),
                width=4
            )
        ], justify='center')
    ], fluid=True, className="bg-dark")

# Bidirectional conversion between Dynamic and Kinematic Viscosity with error handling
@app.callback(
    [Output('dynamic-viscosity', 'value'),
     Output('kinematic-viscosity', 'value'),
     Output('viscosity-error-message', 'children'),
     Output('viscosity-error-message', 'is_open')],
    [Input('dynamic-viscosity', 'value'),
     Input('kinematic-viscosity', 'value'),
     Input('fluid-density', 'value')]
)
def convert_dynamic_to_kinematic(dynamic_viscosity, kinematic_viscosity, density):
    ctx = callback_context
    error_message = ''
    is_open = False
    if not ctx.triggered:
        return dynamic_viscosity, kinematic_viscosity, error_message, is_open
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        try:
            if density is None or density == 0:
                error_message = 'Density cannot be zero.'
                is_open = True
                return dynamic_viscosity, kinematic_viscosity, error_message, is_open
            if input_id == 'dynamic-viscosity':
                if dynamic_viscosity is None:
                    error_message = 'Please enter a valid dynamic viscosity.'
                    is_open = True
                    return dynamic_viscosity, kinematic_viscosity, error_message, is_open
                # Convert dynamic to kinematic viscosity
                kinematic_viscosity = (dynamic_viscosity / density) * 1e6
                return dynamic_viscosity, round(kinematic_viscosity, 2), error_message, is_open
            elif input_id == 'kinematic-viscosity':
                if kinematic_viscosity is None:
                    error_message = 'Please enter a valid kinematic viscosity.'
                    is_open = True
                    return dynamic_viscosity, kinematic_viscosity, error_message, is_open
                # Convert kinematic to dynamic viscosity
                dynamic_viscosity = (kinematic_viscosity * density) / 1e6
                return round(dynamic_viscosity, 2), kinematic_viscosity, error_message, is_open
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            is_open = True
            return dynamic_viscosity, kinematic_viscosity, error_message, is_open
    return dynamic_viscosity, kinematic_viscosity, error_message, is_open

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
