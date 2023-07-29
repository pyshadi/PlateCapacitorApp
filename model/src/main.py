# Import necessary libraries
from flask import Flask, render_template, request, jsonify
from bokeh.embed import components
import numpy as np
from bokeh.plotting import figure
from bokeh.models import HoverTool
from PlateCapacitor import PlateCapacitor


def dc_discharging_plot(capacitance, resistance, initial_voltage, plot_type):
    t = np.linspace(0, 5, num=5000)  # Time values
    if plot_type == "Voltage/Time":
        y = initial_voltage * np.exp(-t / (resistance * capacitance))  # Voltage values
        y_label = 'Voltage (V)'
    elif plot_type == "Current/Time":
        # Current values follow an exponential decay
        y = (initial_voltage / resistance) * np.exp(-t / (resistance * capacitance))  # Current values
        y_label = 'Current (A)'
    elif plot_type == "Charge/Time":
        # The charge in the capacitor as a function of time during discharge
        y = initial_voltage * capacitance * np.exp(-t / (resistance * capacitance))  # Charge values
        y_label = 'Charge (C)'
    else:
        raise ValueError(f'Unknown plot type: {plot_type}')

    plot = figure(title='DC Discharging', x_axis_label='Time (s)', y_axis_label=y_label, plot_width=1200, plot_height=615)
    line = plot.line(t, y, legend_label='DC Discharging', line_width=2)

    # Add hover tool
    hover = HoverTool(renderers=[line], tooltips=[('Time', '@x'), (y_label, '@y')])
    plot.add_tools(hover)
    return plot

def dc_charging_plot(capacitance, resistance, initial_voltage, plot_type):

    x = list(range(100))
    if plot_type == "Charge/Time":
        y = [capacitance * val for val in x]
        y_label = 'Charge'
    elif plot_type == "Current/Time":
        # Calculate current values based on simulation
        y = [(initial_voltage / resistance) * np.exp(-val / (resistance * capacitance)) for val in x]
        y_label = 'Current'
    elif plot_type == "Voltage/Time":
        # Calculate voltage values based on simulation
        y = [initial_voltage * (1 - np.exp(-val / (resistance * capacitance))) for val in x]
        y_label = 'Voltage'
    else:
        raise ValueError(f'Unknown plot type: {plot_type}')

    # Create the plot
    plot = figure(title='DC Charging', x_axis_label='Time', y_axis_label=y_label, plot_width=1200, plot_height=615)
    line = plot.line(x, y, legend_label='DC Charging', line_width=2)

    # Add the hover tool
    hover = HoverTool(renderers=[line], tooltips=[('Time', '@x'), (y_label, '@y')])
    plot.add_tools(hover)
    return plot


def format_capacitance(capacitance):
    units = ['F', 'mF', 'uF', 'nF', 'pF']
    unit_index = 0
    while capacitance < 1 and unit_index < len(units) - 1:
        capacitance *= 1000
        unit_index += 1
    return f"Capacitance: {capacitance:.2f} {units[unit_index]}"

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Define a dictionary with default form values
    form_values = {
        'area': '',
        'separation': '',
        'permittivity': '',
        'resistance': '',
        'initial_voltage': '',
        'simulation_type': 'DC Charging',  # Set the default simulation type
        'plot_type': 'Current/Time'  # Set the default plot type
    }

    plot_script = plot_div = None
    capacitance_output = None

    if request.method == 'POST':
        # Process the form submission
        area = request.form.get('area')
        separation = request.form.get('separation')
        permittivity = request.form.get('permittivity')
        resistance = request.form.get('resistance')
        initial_voltage = request.form.get('initial_voltage')
        simulation_type = request.form.get('simulation_type')
        plot_type = request.form.get('plot_type')

        # Update the form values dictionary with the submitted values
        form_values.update({
            'area': area,
            'separation': separation,
            'permittivity': permittivity,
            'resistance': resistance,
            'initial_voltage': initial_voltage,
            'simulation_type': simulation_type,
            'plot_type': plot_type
        })

        # Check that all form values are filled
        if not all([area, separation, permittivity, resistance, initial_voltage, simulation_type, plot_type]):
            return 'Please fill all form fields', 400

        # Convert form values to appropriate types
        area = float(area)
        separation = float(separation)
        permittivity = float(permittivity)
        resistance = float(resistance)
        initial_voltage = float(initial_voltage)

        capacitor = PlateCapacitor(area, separation)
        capacitance = capacitor.capacitance(permittivity)
        capacitance_output = format_capacitance(capacitance)

        # Depending on the simulation type, generate the corresponding plot
        if simulation_type == 'DC Charging':
            plot = dc_charging_plot(capacitance, resistance, initial_voltage, plot_type)
        elif simulation_type == 'DC Discharging':
            plot = dc_discharging_plot(capacitance, resistance, initial_voltage, plot_type)
        else:
            raise ValueError(f'Unknown simulation type: {simulation_type}')

        # Embed plot into HTML
        plot_script, plot_div = components(plot)

    # Render the template with the updated values
    return render_template('index.html', plot_script=plot_script, plot_div=plot_div,
                           capacitance_output=capacitance_output, form_values=form_values)




@app.route('/update_capacitance', methods=['POST'])
def update_capacitance():
    area = float(request.form.get('area', '0'))
    separation = float(request.form.get('separation', '0'))
    permittivity = float(request.form.get('permittivity', '0'))

    capacitor = PlateCapacitor(area, separation)
    capacitance = capacitor.capacitance(permittivity)

    # Return only the capacitance value, not the entire response
    return jsonify(capacitance=format_capacitance(capacitance))



if __name__ == '__main__':
    app.run(debug=True)