# app.py

from flask import Flask, render_template, request, jsonify
from traffic_simulation import TrafficAgent
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    num_intersections = int(data.get('num_intersections', 5))
    timeout = float(data.get('timeout', 15))
    strategy = data.get('strategy', 'levy')
    levy_scale = float(data.get('levy_scale', 1.0))
    max_wait_time = float(data.get('max_wait_time', 60))

    # Generar número de vehículos aleatorios para cada intersección
    num_vehicles = np.random.randint(10, 100, num_intersections)

    # Crear instancia del agente de tráfico
    agent = TrafficAgent(
        vehicles_per_intersection=num_vehicles,
        num_intersections=num_intersections,
        levy_scale=levy_scale,
        timeout=timeout,
        strategy=strategy
    )

    # Ejecutar la optimización
    result = agent.optimize_traffic()

    if result['success']:
        response = {
            'success': True,
            'max_wait_time': result['max_wait_time'],
            'green_light_times': result['green_light_times'],
            'total_traffic_time': result['total_traffic_time'],
            'wait_times': result['wait_times'],
            'num_vehicles': num_vehicles.tolist()
        }
    else:
        response = {
            'success': False,
            'message': 'No se encontró una solución óptima dentro del tiempo límite.'
        }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
