# Import necessary libraries
from flask import Flask, render_template, request
from bokeh.embed import components
import numpy as np

from bokeh.plotting import figure
from PlateCapacitor import PlateCapacitor


def dc_discharging_plot(capacitance, resistance, initial_voltage):
    # Discharging of a capacitor through a resistor follows an exponential decay
    t = np.linspace(0, 5, num=500)  # Time values
    v = initial_voltage * np.exp(-t / (resistance * capacitance))  # Voltage values

    plot = figure(title='DC Discharging', x_axis_label='Time (s)', y_axis_label='Voltage (V)')
    plot.line(t, v, legend_label='DC Discharging', line_width=2)

    return plot

def impulse_response_plot(capacitance, resistance):
    # In a RC circuit, the impulse response is an exponential decay
    t = np.linspace(0, 5, num=500)  # Time values
    v = np.exp(-t / (resistance * capacitance))  # Voltage values

    plot = figure(title='Impulse Response', x_axis_label='Time (s)', y_axis_label='Voltage (V)')
    plot.line(t, v, legend_label='Impulse Response', line_width=2)

    return plot


def dc_charging_plot(capacitance):
    # Generate x and y values for the plot
    # This is where you would use the equations for your simulation
    x = list(range(100))
    y = [capacitance * val for val in x]

    # Create the plot
    plot = figure(title='DC Charging', x_axis_label='Time', y_axis_label='Charge')
    plot.line(x, y, legend_label='DC Charging', line_width=2)

    return plot



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_script = plot_div = None

    if request.method == 'POST':
        area = request.form.get('area')
        separation = request.form.get('separation')
        permittivity = request.form.get('permittivity')
        resistance = request.form.get('resistance')
        initial_voltage = request.form.get('initial_voltage')
        simulation_type = request.form.get('simulation_type')

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

        # Depending on the simulation type, generate the corresponding plot
        if simulation_type == 'DC Charging':
            plot = dc_charging_plot(capacitance)
        elif simulation_type == 'DC Discharging':
            plot = dc_discharging_plot(capacitance, resistance, initial_voltage)
        elif simulation_type == 'Impulse Response':
            plot = impulse_response_plot(capacitance, resistance)
        else:
            raise ValueError(f'Unknown simulation type: {simulation_type}')

        # Embed plot into HTML
        plot_script, plot_div = components(plot)

    return render_template('index.html', plot_script=plot_script, plot_div=plot_div)




if __name__ == '__main__':
    app.run(debug=True)