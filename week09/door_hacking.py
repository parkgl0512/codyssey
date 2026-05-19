import itertools
import time
import zipfile
import zlib


def save_password(password):
    try:
        with open('password.txt', 'w', encoding='utf-8') as password_file:
            password_file.write(password)

        print('password.txt 파일 저장 완료')

    except OSError:
        print('password.txt 저장 중 오류가 발생했습니다.')


def try_zip_password(zip_file, password):
    try:
        for file_name in zip_file.namelist():
            zip_file.read(file_name, pwd=password.encode('utf-8'))

        return True

    except RuntimeError:
        return False

    except zlib.error:
        return False

    except zipfile.BadZipFile:
        return False

    except OSError:
        return False


def unlock_zip():
    charset = '0123456789abcdefghijklmnopqrstuvwxyz'
    zip_file_name = 'emergency_storage_key.zip'
    password_length = 6

    start_time = time.time()
    count = 0

    print('암호 해독을 시작합니다.')
    print(f'시작 시간: {time.ctime(start_time)}')
    print('-' * 50)

    try:
        with zipfile.ZipFile(zip_file_name, 'r') as zip_file:
            for password_tuple in itertools.product(
                charset,
                repeat=password_length
            ):
                count += 1
                password = ''.join(password_tuple)

                if count % 10000 == 0:
                    elapsed_time = time.time() - start_time
                    print(
                        f'반복 회수: {count}, '
                        f'현재 암호: {password}, '
                        f'진행 시간: {elapsed_time:.2f}초'
                    )

                if try_zip_password(zip_file, password):
                    elapsed_time = time.time() - start_time

                    print('-' * 50)
                    print('암호 해독 성공')
                    print(f'암호: {password}')
                    print(f'총 반복 회수: {count}')
                    print(f'총 진행 시간: {elapsed_time:.2f}초')

                    save_password(password)
                    return password

    except FileNotFoundError:
        print('emergency_storage_key.zip 파일이 존재하지 않습니다.')

    except zipfile.BadZipFile:
        print('정상적인 ZIP 파일이 아닙니다.')

    except PermissionError:
        print('ZIP 파일 접근 권한이 없습니다.')

    except OSError:
        print('ZIP 파일 처리 중 오류가 발생했습니다.')

    print('암호 해독 실패')
    return None


if __name__ == '__main__':
    unlock_zip()