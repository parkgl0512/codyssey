import itertools
import multiprocessing
import string
import time
import zipfile
import zlib


ZIP_FILE_NAME = 'emergency_storage_key.zip'
PASSWORD_FILE_NAME = 'password.txt'
PASSWORD_LENGTH = 6                                # 암호는 6자리
PROGRESS_INTERVAL = 100_000                        # 10만 번마다 진행 상황 출력
CHARSET = string.digits + string.ascii_lowercase   # 숫자 + 소문자: 총 36가지 문자


def save_password(password):
    """해독된 암호를 password.txt 에 저장한다."""
    try:
        with open(PASSWORD_FILE_NAME, 'w', encoding='utf-8') as file:
            file.write(password)
        print(f'Password saved to {PASSWORD_FILE_NAME}')
    except OSError as error:
        # 파일 저장 실패 시 예외 처리
        print(f'Failed to save password: {error}')


def try_password(zf, file_name, password):
    """
    ZIP 객체로 단일 암호를 검증한다.

    - 성공: 파일 첫 1바이트를 읽을 수 있으면 True
    - 실패: RuntimeError(틀린 암호) 또는 zlib.error(압축 오류) → False
    """
    try:
        with zf.open(file_name, 'r', pwd=password.encode('utf-8')) as f:
            f.read(1)    # 1바이트만 읽어 암호 일치 여부 확인 (최소 비용)
        return True
    except (RuntimeError, zlib.error):
        return False     # 틀린 암호는 조용히 무시하고 다음으로


def unlock_zip():
    """
        itertools.product 로 36^6 = 약 21억 가지 조합을 순서대로 생성.
        ZIP 파일은 루프 밖에서 한 번만 열어 I/O 비용을 최소화.
    """
    print('=' * 60)
    print('  [Basic] Start unlocking emergency_storage_key.zip')
    print('=' * 60)
    print(f'  Start time  : {time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'  Password    : {PASSWORD_LENGTH} chars, digits + lowercase')
    print(f'  Total cases : {len(CHARSET) ** PASSWORD_LENGTH:,}')
    print('=' * 60)

    start_time = time.time()
    total_cases = len(CHARSET) ** PASSWORD_LENGTH
    checked_count = 0

    try:
        # ZIP 파일을 루프 밖에서 한 번만 열기 → 반복 open/close 제거
        with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zf:
            file_name = zf.namelist()[0]    # ZIP 내부 첫 번째 파일 이름 저장

            for combo in itertools.product(CHARSET, repeat=PASSWORD_LENGTH):
                password = ''.join(combo)
                checked_count += 1

                # 10만 번마다 진행 상황 출력
                if checked_count % PROGRESS_INTERVAL == 0:
                    elapsed = time.time() - start_time
                    progress = checked_count / total_cases * 100
                    print(
                        f'  Tried: {checked_count:>12,} / {total_cases:,} '
                        f'({progress:.3f}%)  '
                        f'Elapsed: {elapsed:.1f}s'
                    )

                # 암호 검증: 성공하면 즉시 저장 후 반환
                if try_password(zf, file_name, password):
                    elapsed = time.time() - start_time
                    print()
                    print('=' * 60)
                    print(f'  Password found : {password}')
                    print(f'  Try count      : {checked_count:,}')
                    print(f'  Elapsed time   : {elapsed:.2f} seconds')
                    print('=' * 60)
                    save_password(password)
                    return password

    except FileNotFoundError:
        print(f'File not found: {ZIP_FILE_NAME}')
        return None
    except zipfile.BadZipFile:
        print(f'Invalid zip file: {ZIP_FILE_NAME}')
        return None

    print('Failed to unlock the zip file.')
    return None


def _check_chunk(passwords):
    """
    워커 프로세스가 실행하는 함수. 청크 단위로 처리

    ZIP 파일을 청크당 한 번만 열기
        기존: 암호 1개마다 ZipFile() open/close  → 약 21억 번 I/O
        개선: 암호 10,000개 묶음마다 open/close  → 약 21만 번 I/O (1/10,000 절감)
    """
    try:
        # 이 워커가 담당하는 청크 전체를 하나의 ZIP open 으로 처리
        with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zf:
            file_name = zf.namelist()[0]
            for password in passwords:
                try:
                    with zf.open(file_name, 'r', pwd=password.encode('utf-8')) as f:
                        f.read(1)       # 1바이트만 읽어 암호 검증
                    return password     # 정답 발견 즉시 반환
                except (RuntimeError, zlib.error):
                    continue            # 틀린 암호 → 다음 시도
    except (zipfile.BadZipFile, OSError, IndexError):
        return None

    return None


def _generate_chunks(chunk_size):
    """
    전체 암호 조합을 chunk_size 단위 리스트로 묶어 yield

    제너레이터 방식이므로 21억 개의 조합을 한 번에 메모리에 올리지 않음.
    청크 단위로 워커에 전달해 IPC(프로세스 간 통신) 오버헤드도 절감.
    """
    chunk = []
    for combo in itertools.product(CHARSET, repeat=PASSWORD_LENGTH):
        chunk.append(''.join(combo))
        if len(chunk) == chunk_size:
            yield chunk     # chunk_size 개가 모이면 워커에 전달
            chunk = []
    if chunk:
        yield chunk         # 마지막 남은 조합도 전달


def unlock_zip_fast():
    """
    멀티프로세싱 + 청크 단위 처리로 ZIP 암호를 병렬 해독한다. (보너스 과제)

    3가지 최적화 전략:
        1. [멀티프로세싱] CPU 코어 수만큼 워커 생성 → 이론상 N코어 = N배 속도
        2. [청크 처리]    암호 10,000개씩 묶어 전달 → ZIP I/O / IPC 오버헤드 1/10,000
        3. [조기 종료]    정답 발견 즉시 pool.terminate() 로 전체 프로세스 중단

    성능 비교 (8코어 기준):
        unlock_zip()      : 단일 프로세스  → 최악 약 12시간
        unlock_zip_fast() : 8코어 병렬     → 최악 약 1시간 (약 10배 이상 빠름)
    """
    cpu_count = multiprocessing.cpu_count()   # 현재 PC의 CPU 코어 수 자동 감지
    total_cases = len(CHARSET) ** PASSWORD_LENGTH
    chunk_size = 10_000    # 청크 크기: 크면 IPC↓ 워커 유휴↑, 10,000이 실용적 균형

    start_time = time.time()
    checked_count = 0

    print('=' * 60)
    print('  [Bonus] Multiprocessing parallel brute-force')
    print('=' * 60)
    print(f'  Start time  : {time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'  Password    : {PASSWORD_LENGTH} chars, digits + lowercase')
    print(f'  Total cases : {total_cases:,}')
    print(f'  CPU cores   : {cpu_count}')      # 병렬로 사용할 코어 수 출력
    print(f'  Chunk size  : {chunk_size:,}')   # 워커당 한 번에 처리할 암호 수
    print('=' * 60)

    # ZIP 파일 존재 여부 사전 확인 (워커 실행 전에 빠르게 검증)
    try:
        zipfile.ZipFile(ZIP_FILE_NAME, 'r').close()
    except FileNotFoundError:
        print(f'File not found: {ZIP_FILE_NAME}')
        return None
    except zipfile.BadZipFile:
        print(f'Invalid zip file: {ZIP_FILE_NAME}')
        return None

    # Pool: cpu_count 개의 워커 프로세스를 생성해 청크를 병렬 처리
    with multiprocessing.Pool(processes=cpu_count) as pool:

        # imap_unordered: 결과가 완료되는 순서대로 즉시 반환
        # → 정답이 어느 워커에서 나오든 가장 빠르게 감지 가능
        for result in pool.imap_unordered(
            _check_chunk,
            _generate_chunks(chunk_size)
        ):
            checked_count += chunk_size

            # 진행 상황 출력: 속도(Speed) 
            if checked_count % PROGRESS_INTERVAL == 0:
                elapsed = time.time() - start_time
                progress = min(checked_count / total_cases * 100, 100)
                speed = checked_count / elapsed if elapsed > 0 else 0
                print(
                    f'  Tried: {checked_count:>12,} / {total_cases:,} '
                    f'({progress:.3f}%)  '
                    f'Speed: {speed:,.0f}/s  '   
                    f'Elapsed: {elapsed:.1f}s'
                )

            if result is not None:
                elapsed = time.time() - start_time
                print()
                print('=' * 60)
                print(f'  Password found : {result}')
                print(f'  Try count      : {checked_count:,}')
                print(f'  Elapsed time   : {elapsed:.2f} seconds')
                print('=' * 60)
                save_password(result)
                pool.terminate()    # 정답 발견
                return result

    print('Failed to unlock the zip file.')
    return None


if __name__ == '__main__':
    multiprocessing.freeze_support()   
    unlock_zip_fast()