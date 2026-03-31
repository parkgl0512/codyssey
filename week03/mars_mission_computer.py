"""Mars mission computer dummy sensor module with logging."""

import random
from datetime import datetime


class DummySensor:
    """Generate random environment values for testing."""

    def __init__(self):
        """Initialize environment values."""
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0,
        }

    def set_env(self):
        """Set random values within the required ranges."""
        self.env_values['mars_base_internal_temperature'] = round(
            random.uniform(18, 30), 2
        )
        self.env_values['mars_base_external_temperature'] = round(
            random.uniform(0, 21), 2
        )
        self.env_values['mars_base_internal_humidity'] = round(
            random.uniform(50, 60), 2
        )
        self.env_values['mars_base_external_illuminance'] = round(
            random.uniform(500, 715), 2
        )
        self.env_values['mars_base_internal_co2'] = round(
            random.uniform(0.02, 0.1), 4
        )
        self.env_values['mars_base_internal_oxygen'] = round(
            random.uniform(4, 7), 2
        )

    def get_env(self):
        """Return environment values and log them to a file."""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        log_line = (
            f'{current_time} | '
            f'Internal Temp: {self.env_values["mars_base_internal_temperature"]}, '
            f'External Temp: {self.env_values["mars_base_external_temperature"]}, '
            f'Internal Humidity: {self.env_values["mars_base_internal_humidity"]}, '
            f'External Illuminance: {self.env_values["mars_base_external_illuminance"]}, '
            f'CO2: {self.env_values["mars_base_internal_co2"]}, '
            f'Oxygen: {self.env_values["mars_base_internal_oxygen"]}\n'
        )

        with open('mars_env_log.txt', 'a') as log_file:
            log_file.write(log_line)

        return self.env_values


def main():
    """Create a dummy sensor and print generated values."""
    ds = DummySensor()
    ds.set_env()

    env_values = ds.get_env()
    for key, value in env_values.items():
        print(f'{key}: {value}')


if __name__ == '__main__':
    main()