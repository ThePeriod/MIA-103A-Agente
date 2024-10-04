# traffic_simulation.py

import numpy as np
from scipy.special import erfcinv
import time

MAX_WAIT_TIME = 60  # Tiempo máximo permitido de espera en una intersección (en segundos)

class TrafficAgent:
    def __init__(self, vehicles_per_intersection, num_intersections, levy_scale=1.0, timeout=10, strategy="levy"):
        self.vehicles_per_intersection = vehicles_per_intersection
        self.num_intersections = num_intersections
        self.levy_scale = levy_scale
        self.timeout = timeout
        self.strategy = strategy  # "levy" o "luby"
        self.luby_index = 1  # Inicialización para el algoritmo Luby
        self.luby_counter = 0  # Controla cuándo se incrementa el índice de Luby

    def levy_restart(self, scale):
        # Estrategia de reinicio Lévy-Smirnov
        return scale / (2.0 * np.power(erfcinv(np.random.uniform(0.0001, 0.9999)), 2))

    def luby_restart(self):
        # Estrategia de reinicio basada en la secuencia de Luby
        return self.luby_sequence(self.luby_index)

    def luby_sequence(self, k):
        # Implementación de la secuencia de Luby
        if k == 0:
            return 1
        i = 1
        while i <= k:
            i = i * 2
        if i - 1 == k:
            return i // 2
        return self.luby_sequence(k - i // 2 + 1)

    def simulate_traffic_flow(self, green_light_times):
        """
        Simula el flujo de tráfico en las intersecciones dadas las duraciones de las luces verdes.
        Retorna el tiempo máximo de espera, el tiempo total de tráfico y los tiempos de espera por intersección.
        """
        wait_times = [0] * len(self.vehicles_per_intersection)
        total_traffic_times = [0] * self.num_intersections  # Tiempo total de tráfico en cada intersección

        for i, vehicles in enumerate(self.vehicles_per_intersection):
            green_time = green_light_times[i]  # Tiempo de luz verde en la intersección i
            wait_times[i] = vehicles / green_time  # El tiempo de espera es inversamente proporcional al tiempo de luz verde
            total_traffic_times[i] = wait_times[i] + green_time  # Tiempo total de tráfico en la intersección

        max_wait_time = max(wait_times)
        return max_wait_time, sum(total_traffic_times), wait_times

    def optimize_traffic(self):
        """
        Optimiza la duración de las luces verdes en cada intersección con reinicios basados en Lévy o Luby.
        """
        start_time = time.time()
        restarts = 0

        while time.time() - start_time < self.timeout:
            # Inicialmente, asigna tiempos de luz verde aleatorios para cada intersección.
            green_light_times = np.random.uniform(10, 60, self.num_intersections)

            max_wait_time, total_traffic_time, wait_times = self.simulate_traffic_flow(green_light_times)

            if max_wait_time < MAX_WAIT_TIME:
                return {
                    'success': True,
                    'max_wait_time': max_wait_time,
                    'green_light_times': green_light_times.tolist(),
                    'total_traffic_time': total_traffic_time,
                    'wait_times': wait_times
                }

            # Si no es una buena solución, aplicar un reinicio basado en la estrategia seleccionada
            restarts += 1

            if self.strategy == "levy":
                wait_time = self.levy_restart(self.levy_scale)
            elif self.strategy == "luby":
                wait_time = self.luby_restart()
                self.luby_counter += 1
                if self.luby_counter >= wait_time:
                    self.luby_counter = 0
                    self.luby_index += 1

            # Verificar si el tiempo de espera excede el tiempo límite
            if time.time() - start_time + wait_time >= self.timeout:
                break

        return {'success': False, 'restarts': restarts}
