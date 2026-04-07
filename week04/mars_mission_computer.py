"""Mars mission computer module."""

import json
import time
import threading
import random


class DummySensor:
    """Generate random environment values."""

    def __init__(self):
        """Initialize sensor values."""
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0,
        }

    def set_env(self):
        """Set random values."""
        self.env_values['mars_base_internal_temperature'] = round(
            random.uniform(18, 30), 2
        )
        self.env_values['mars_base_external_temperature'] = round(
            random.uniform(-80, 0), 2
        )
        self.env_values['mars_base_internal_humidity'] = round(
            random.uniform(30, 70), 2
        )
        self.env_values['mars_base_external_illuminance'] = round(
            random.uniform(0, 1000), 2
        )
        self.env_values['mars_base_internal_co2'] = round(
            random.uniform(300, 2000), 2
        )
        self.env_values['mars_base_internal_oxygen'] = round(
            random.uniform(18, 23), 2
        )

        return self.env_values


class MissionComputer:
    """Mission computer for Mars base."""

    def __init__(self):
        """Initialize mission computer."""
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0,
        }
        self.ds = DummySensor()
        self.running = True
        self.history = []
        self.start_time = time.time()

    def stop_listener(self):
        """Listen for stop command."""
        while self.running:
            user_input = input()
            if user_input.strip().lower() == 'q':
                self.running = False
                print('System stopped....')

    def calculate_average(self):
        """Calculate 5-minute average."""
        if not self.history:
            return

        avg_values = {}
        keys = self.history[0].keys()

        for key in keys:
            avg_values[key] = round(
                sum(item[key] for item in self.history) / len(self.history),
                2
            )

        print('\n[5-minute average]')
        print(json.dumps(avg_values, indent=4))
        print()

        self.history.clear()

    def get_sensor_data(self):
        """Fetch and print sensor data."""
        listener_thread = threading.Thread(target=self.stop_listener)
        listener_thread.daemon = True
        listener_thread.start()

        while self.running:
            sensor_data = self.ds.set_env()
            self.env_values.update(sensor_data)

            print(json.dumps(self.env_values, indent=4))

            self.history.append(self.env_values.copy())

            # 5분(300초) 체크
            current_time = time.time()
            if current_time - self.start_time >= 300:
                self.calculate_average()
                self.start_time = current_time

            time.sleep(5)


if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()