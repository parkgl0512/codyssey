import csv
import os
import wave
from datetime import datetime

import pyaudio
import speech_recognition as sr


RECORD_DIR = 'records'
CHANNELS = 1
RATE = 44100
CHUNK = 1024
FORMAT = pyaudio.paInt16
DATE_FORMAT = '%Y%m%d'
STT_CHUNK_SECONDS = 5


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
            device_name = device_info.get('name')
            print(f'{index}: {device_name}')


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


def get_record_files():
    create_records_dir()

    record_files = []

    for filename in os.listdir(RECORD_DIR):
        if filename.endswith('.wav'):
            record_files.append(filename)

    record_files.sort()
    return record_files


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


def get_audio_duration(audio_path):
    with wave.open(audio_path, 'rb') as wave_file:
        frames = wave_file.getnframes()
        frame_rate = wave_file.getframerate()

    return frames / float(frame_rate)


def select_record_file():
    record_files = get_record_files()

    if len(record_files) == 0:
        print('녹음 파일이 없습니다.')
        return None

    print('녹음 파일 목록')

    for index, filename in enumerate(record_files, start=1):
        print(f'{index}. {filename}')

    try:
        selected = int(input('텍스트로 변환할 파일 번호를 입력하세요: '))
    except ValueError:
        print('숫자만 입력해야 합니다.')
        return None

    if selected < 1 or selected > len(record_files):
        print('올바른 파일 번호를 입력하세요.')
        return None

    return os.path.join(RECORD_DIR, record_files[selected - 1])


def transcribe_audio_file(audio_path):
    recognizer = sr.Recognizer()
    duration = get_audio_duration(audio_path)
    results = []
    offset = 0

    while offset < duration:
        remain_time = duration - offset
        record_time = min(STT_CHUNK_SECONDS, remain_time)

        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(
                source,
                duration=record_time,
                offset=offset
            )

        start_time = int(offset)
        end_time = int(offset + record_time)
        time_text = f'{start_time:04d}-{end_time:04d}초'

        try:
            text = recognizer.recognize_google(
                audio_data,
                language='ko-KR'
            )
        except sr.UnknownValueError:
            text = ''
        except sr.RequestError:
            text = 'STT 서비스 요청 실패'

        results.append((time_text, text))
        offset += STT_CHUNK_SECONDS

    return results


def save_transcript_csv(audio_path, transcript_results):
    csv_path = os.path.splitext(audio_path)[0] + '.csv'

    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['음성 파일내에서의 시간', '인식된 텍스트'])

        for time_text, text in transcript_results:
            writer.writerow([time_text, text])

    print(f'CSV 저장 완료: {csv_path}')


def convert_record_to_text():
    audio_path = select_record_file()

    if audio_path is None:
        return

    print('STT 변환을 시작합니다.')

    transcript_results = transcribe_audio_file(audio_path)

    for time_text, text in transcript_results:
        print(f'{time_text}: {text}')

    save_transcript_csv(audio_path, transcript_results)


def search_keyword_in_csv():
    create_records_dir()

    keyword = input('검색할 키워드를 입력하세요: ').strip()

    if keyword == '':
        print('키워드를 입력해야 합니다.')
        return

    found = False
    result_count = 0

    for filename in sorted(os.listdir(RECORD_DIR)):
        if not filename.endswith('.csv'):
            continue

        csv_path = os.path.join(RECORD_DIR, filename)

        try:
            with open(
                csv_path,
                'r',
                encoding='utf-8-sig'
            ) as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)

                for row in reader:
                    if len(row) < 2:
                        continue

                    time_text = row[0]
                    recognized_text = row[1]

                    if keyword.lower() in recognized_text.lower():
                        found = True
                        result_count += 1

                        print()
                        print(f'파일명: {filename}')
                        print(f'시간: {time_text}')
                        print(f'내용: {recognized_text}')

        except OSError:
            print(f'파일을 읽을 수 없습니다: {filename}')

    if found:
        print()
        print(f'총 {result_count}건 검색되었습니다.')
    else:
        print('검색 결과가 없습니다.')


def show_menu():
    print()
    print('1. 음성 녹음하기')
    print('2. 날짜 범위로 녹음 파일 조회하기')
    print('3. 녹음 파일 텍스트 변환하기')
    print('4. 키워드 검색하기')
    print('5. 종료')


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
            convert_record_to_text()
        elif menu == '4':
            search_keyword_in_csv()
        elif menu == '5':
            print('프로그램을 종료합니다.')
            break
        else:
            print('올바른 메뉴 번호를 입력하세요.')


if __name__ == '__main__':
    main()