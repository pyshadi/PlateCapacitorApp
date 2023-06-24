# Import necessary libraries
from flask import Flask, render_template, request, jsonify
from bokeh.embed import components
import numpy as np

from bokeh.plotting import figure
from bokeh.models import HoverTool

from PlateCapacitor import PlateCapacitor


def dc_discharging_plot(capacitance, resistance, initial_voltage):
    # Discharging of a capacitor through a resistor follows an exponential decay
    t = np.linspace(0, 5, num=5000)  # Time values
    v = initial_voltage * np.exp(-t / (resistance * capacitance))  # Voltage values

    plot = figure(title='DC Discharging', x_axis_label='Time (s)', y_axis_label='Voltage (V)', plot_width=1200, plot_height=790)
    line = plot.line(t, v, legend_label='DC Discharging', line_width=2)

    # Add hover tool to display values
    hover = HoverTool(renderers=[line], tooltips=[('Time', '@x'), ('Voltage', '@y')])
    # Add the hover tool to the plot
    plot.add_tools(hover)
    return plot

def dc_charging_plot(capacitance):
    # Generate x and y values for the plot
    # This is where you would use the equations for your simulation
    x = list(range(100))
    y = [capacitance * val for val in x]

    # Create the plot
    plot = figure(title='DC Charging', x_axis_label='Time', y_axis_label='Charge', plot_width=1200, plot_height=790)
    line = plot.line(x, y, legend_label='DC Charging', line_width=2)

    # Add hover tool to display values
    hover = HoverTool(renderers=[line], tooltips=[('Time', '@x'), ('Charge', '@y')])

    # Add the hover tool to the plot
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
        'simulation_type': 'DC Charging'  # Set the default simulation type
    }

    plot_script = plot_div = None
    capacitance_output = None

    if request.method == 'POST':
        area = request.form.get('area')
        separation = request.form.get('separation')
        permittivity = request.form.get('permittivity')
        resistance = request.form.get('resistance')
        initial_voltage = request.form.get('initial_voltage')
        simulation_type = request.form.get('simulation_type')

        # Update the form values dictionary with the submitted values
        form_values.update({
            'area': area,
            'separation': separation,
            'permittivity': permittivity,
            'resistance': resistance,
            'initial_voltage': initial_voltage,
            'simulation_type': simulation_type
        })

        # Check that all form values are filled
        if not all([area, separation, permittivity, resistance, initial_voltage, simulation_type]):
            return 'Please fill all form fields', 400

        # Convert form values to floats
        area = float(area)
        separation = float(separation)
        permittivity = float(permittivity)
        resistance = float(resistance)
        initial_voltage = float(initial_voltage)

        capacitor = PlateCapacitor(area, separation)
        capacitance = capacitor.capacitance(permittivity)
        # Update the capacitance output
        capacitance_output = update_capacitance()

        # Depending on the simulation type, generate the corresponding plot
        if simulation_type == 'DC Charging':
            plot = dc_charging_plot(capacitance)
        elif simulation_type == 'DC Discharging':
            plot = dc_discharging_plot(capacitance, resistance, initial_voltage)
        else:
            raise ValueError(f'Unknown simulation type: {simulation_type}')

        # Embed plot into HTML
        plot_script, plot_div = components(plot)

        # Pass the form values dictionary to the template
    return render_template('index.html', plot_script=plot_script, plot_div=plot_div,
                           capacitance_output=capacitance_output, form_values=form_values)

@app.route('/update_capacitance', methods=['POST'])
def update_capacitance():
    area = float(request.form.get('area', '0'))
    separation = float(request.form.get('separation', '0'))
    permittivity = float(request.form.get('permittivity', '0'))

    capacitor = PlateCapacitor(area, separation)
    capacitance = capacitor.capacitance(permittivity)

    return jsonify(capacitance=format_capacitance(capacitance))


if __name__ == '__main__':
    app.run(debug=True)