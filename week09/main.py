def decode_text(target_text, shift):
    decoded_text = ''
    alphabet_count = 26

    for char in target_text:

        # 대문자를 이동 값만큼 복호화
        if 'A' <= char <= 'Z':
            decoded_char = chr(
                (ord(char) - ord('A') - shift) % alphabet_count
                + ord('A')
            )
            decoded_text += decoded_char

        # 소문자를 이동 값만큼 복호화
        elif 'a' <= char <= 'z':
            decoded_char = chr(
                (ord(char) - ord('a') - shift) % alphabet_count
                + ord('a')
            )
            decoded_text += decoded_char

        # 알파벳이 아니면 그대로 유지
        else:
            decoded_text += char

    return decoded_text


def save_result(decoded_text):
    try:
        # 최종 복호화 결과를 result.txt에 저장
        with open(
            'result.txt',
            'w',
            encoding='utf-8'
        ) as file:
            file.write(decoded_text)

        print()
        print('===== 최종 복호화 결과 =====')
        print(decoded_text)
        print()
        print('result.txt 파일 저장 완료')

    except OSError:
        print('result.txt 저장 중 오류가 발생했습니다.')


def caesar_cipher_decode(target_text):
    # 복호화 성공 여부를 판단할 단어 사전
    dictionary_words = [
        'hello',
        'world',
        'love',
        'mars',
        'door',
        'open'
    ]

    alphabet_count = 26

    print('===== 카이사르 암호 해독 결과 =====')
    print()

    # 이동 값을 0 ~ 25까지 변경하며 반복
    for shift in range(alphabet_count):

        decoded_result = decode_text(target_text, shift)

        print(f'[이동 값 : {shift}]')
        print(decoded_result)
        print()

        lower_result = decoded_result.lower()

        for word in dictionary_words:

            # 사전 단어 발견 시 반복 종료
            if word in lower_result:
                print('사전 단어 발견!')
                print(f'발견된 단어 : {word}')
                print(f'이동 값 : {shift}')

                save_result(decoded_result)
                return

    print('사전에 등록된 단어를 찾지 못했습니다.')


def main():
    try:
        # password.txt 파일에서 암호문 읽기
        with open(
            'password.txt',
            'r',
            encoding='utf-8'
        ) as file:
            encrypted_text = file.read().strip()

        if encrypted_text == '':
            print('password.txt 파일이 비어 있습니다.')
            return

        caesar_cipher_decode(encrypted_text)

    except FileNotFoundError:
        print('password.txt 파일을 찾을 수 없습니다.')

    except OSError:
        print('파일을 읽는 중 오류가 발생했습니다.')


if __name__ == '__main__':
    main()