def print_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        print(content)

    except FileNotFoundError:
        print(f'오류: {file_path} 파일을 찾을 수 없습니다.')
    except PermissionError:
        print(f'오류: {file_path} 파일을 읽을 권한이 없습니다.')
    except UnicodeDecodeError:
        print(f'오류: {file_path} 파일의 인코딩을 UTF-8로 읽을 수 없습니다.')
    except OSError as error:
        print(f'오류: 파일 처리 중 문제가 발생했습니다. {error}')


def main():
    file_path = 'mission_computer_main.log'
    print_log_file(file_path)


if __name__ == '__main__':
    main()


def print_reverse_sorted_logs(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            print('로그 파일이 비어 있습니다.')
            return

        header = lines[0].strip()
        data_lines = lines[1:]
        logs = []

        for line in data_lines:
            parts = line.strip().split(',', 2)

            if len(parts) != 3:
                continue

            timestamp, event, message = parts
            logs.append((timestamp.strip(), event.strip(), message.strip()))

        logs.sort(reverse=True)

        print('\n=== 시간 역순 정렬 출력 ===')
        print(header)
        for timestamp, event, message in logs:
            print(f'{timestamp},{event},{message}')

    except FileNotFoundError:
        print(f'오류: {file_path} 파일을 찾을 수 없습니다.')
    except PermissionError:
        print(f'오류: {file_path} 파일을 읽을 권한이 없습니다.')
    except UnicodeDecodeError:
        print(f'오류: {file_path} 파일의 인코딩을 UTF-8로 읽을 수 없습니다.')
    except OSError as error:
        print(f'오류: 파일 처리 중 문제가 발생했습니다. {error}')


def save_problem_logs(file_path, output_file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write('문제가 되는 로그가 없습니다.\n')
            return

        data_lines = lines[1:]
        problem_keywords = ('unstable', 'explosion', 'error', 'failure')
        problem_logs = []

        for line in data_lines:
            parts = line.strip().split(',', 2)

            if len(parts) != 3:
                continue

            timestamp, event, message = parts
            message_lower = message.lower()

            for keyword in problem_keywords:
                if keyword in message_lower:
                    problem_logs.append(
                        f'{timestamp.strip()},{event.strip()},{message.strip()}'
                    )
                    break

        with open(output_file_path, 'w', encoding='utf-8') as file:
            if not problem_logs:
                file.write('문제가 되는 로그가 없습니다.\n')
            else:
                for log in problem_logs:
                    file.write(log + '\n')

        print(f'\n문제가 되는 로그를 {output_file_path} 파일로 저장했습니다.')

    except FileNotFoundError:
        print(f'오류: {file_path} 파일을 찾을 수 없습니다.')
    except PermissionError:
        print(f'오류: {file_path} 파일을 읽거나 쓸 권한이 없습니다.')
    except UnicodeDecodeError:
        print(f'오류: {file_path} 파일의 인코딩을 UTF-8로 읽을 수 없습니다.')
    except OSError as error:
        print(f'오류: 파일 처리 중 문제가 발생했습니다. {error}')


print_reverse_sorted_logs('mission_computer_main.log')
save_problem_logs('mission_computer_main.log', 'problem_logs.txt')