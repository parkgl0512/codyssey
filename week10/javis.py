import os
import wave
from datetime import datetime

import pyaudio


RECORD_DIR = 'records'
CHANNELS = 1
RATE = 44100
CHUNK = 1024
FORMAT = pyaudio.paInt16
DATE_FORMAT = '%Y%m%d'


def create_records_dir():
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)


def get_record_filename():
    now = datetime.now()
    filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    return os.path.join(RECORD_DIR, filename)


def list_microphones(audio):
    print('사용 가능한 마이크 목록')

    for index in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(index)

        if device_info.get('maxInputChannels') > 0:
            print(f'{index}: {device_info.get("name")}')


def record_audio(seconds):
    create_records_dir()

    audio = pyaudio.PyAudio()
    list_microphones(audio)

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print('녹음을 시작합니다.')

    frames = []

    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print('녹음이 종료되었습니다.')

    stream.stop_stream()
    stream.close()

    filename = get_record_filename()

    with wave.open(filename, 'wb') as wave_file:
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))

    audio.terminate()

    print(f'파일 저장 완료: {filename}')


def get_record_date(filename):
    try:
        date_text = filename[:8]
        return datetime.strptime(date_text, DATE_FORMAT).date()
    except ValueError:
        return None


def show_records_by_date_range():
    create_records_dir()

    start_text = input('시작 날짜를 입력하세요. 예: 20260501: ')
    end_text = input('종료 날짜를 입력하세요. 예: 20260525: ')

    try:
        start_date = datetime.strptime(start_text, DATE_FORMAT).date()
        end_date = datetime.strptime(end_text, DATE_FORMAT).date()
    except ValueError:
        print('날짜 형식이 올바르지 않습니다. 예: 20260525')
        return

    if start_date > end_date:
        print('시작 날짜는 종료 날짜보다 늦을 수 없습니다.')
        return

    record_files = []

    for filename in os.listdir(RECORD_DIR):
        if not filename.endswith('.wav'):
            continue

        record_date = get_record_date(filename)

        if record_date is None:
            continue

        if start_date <= record_date <= end_date:
            record_files.append(filename)

    record_files.sort()

    if len(record_files) == 0:
        print('해당 날짜 범위의 녹음 파일이 없습니다.')
        return

    print('조회된 녹음 파일 목록')

    for record_file in record_files:
        print(os.path.join(RECORD_DIR, record_file))


def show_menu():
    print()
    print('1. 음성 녹음하기')
    print('2. 날짜 범위로 녹음 파일 조회하기')
    print('3. 종료')


def main():
    while True:
        show_menu()
        menu = input('메뉴를 선택하세요: ')

        if menu == '1':
            try:
                seconds = int(input('녹음할 시간을 초 단위로 입력하세요: '))
                record_audio(seconds)
            except ValueError:
                print('숫자만 입력해야 합니다.')
        elif menu == '2':
            show_records_by_date_range()
        elif menu == '3':
            print('프로그램을 종료합니다.')
            break
        else:
            print('올바른 메뉴 번호를 입력하세요.')


if __name__ == '__main__':
    main()