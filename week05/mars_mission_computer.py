import os
import platform
import json

# 시스템 정보용 라이브러리 (허용)
try:
    import psutil
except ImportError:
    psutil = None


class MissionComputer:
    def __init__(self):
        self.env_values = {}

    def _load_settings(self):
        """
        setting.txt 기준으로 출력 항목 결정
        (파일에 있는 항목만 True)
        """
        settings = {
            'os': False,
            'os_version': False,
            'cpu_type': False,
            'cpu_core': False,
            'memory_total': False,
            'cpu_usage': False,
            'memory_usage': False
        }

        try:
            if os.path.exists('setting.txt'):
                with open('setting.txt', 'r') as file:
                    lines = file.readlines()

                for line in lines:
                    key = line.strip()
                    if key in settings:
                        settings[key] = True

        except Exception as e:
            print(f'[ERROR] setting 파일 읽기 실패: {e}')

        return settings

    def get_mission_computer_info(self):
        """
        시스템 기본 정보 출력 (JSON)
        """
        info = {}
        settings = self._load_settings()

        try:
            if settings['os']:
                info['operating_system'] = platform.system()

            if settings['os_version']:
                info['os_version'] = platform.version()

            if settings['cpu_type']:
                info['cpu_type'] = platform.processor()

            if settings['cpu_core']:
                info['cpu_core'] = os.cpu_count()

            if settings['memory_total']:
                if psutil:
                    memory = psutil.virtual_memory()
                    info['memory_total'] = memory.total
                else:
                    info['memory_total'] = 'psutil not installed'

        except Exception as e:
            info['error'] = f'시스템 정보 조회 실패: {e}'

        print(json.dumps(info, indent = 4))

    def get_mission_computer_load(self):
        """
        실시간 부하 정보 출력 (JSON)
        """
        load = {}
        settings = self._load_settings()

        try:
            if psutil:
                if settings['cpu_usage']:
                    load['cpu_usage'] = psutil.cpu_percent(interval = 1)

                if settings['memory_usage']:
                    memory = psutil.virtual_memory()
                    load['memory_usage'] = memory.percent
            else:
                load['error'] = 'psutil 라이브러리가 없습니다.'

        except Exception as e:
            load['error'] = f'부하 정보 조회 실패: {e}'

        print(json.dumps(load, indent = 4))


# 실행
if __name__ == '__main__':
    runComputer = MissionComputer()

    print('=== Mission Computer Info ===')
    runComputer.get_mission_computer_info()

    print('\n=== Mission Computer Load ===')
    runComputer.get_mission_computer_load()