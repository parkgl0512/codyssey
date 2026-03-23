def read_csv_file(file_path):
    '''
    CSV 파일을 읽어서 헤더와 데이터 행을 반환한다.
    '''
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            print('파일이 비어 있습니다.')
            return [], []

        headers = lines[0].strip().split(',')
        rows = []

        for line in lines[1:]:
            stripped_line = line.strip()

            if stripped_line == '':
                continue

            row = stripped_line.split(',')
            rows.append(row)

        return headers, rows

    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {file_path}')
    except PermissionError:
        print(f'파일 접근 권한이 없습니다: {file_path}')
    except OSError as error:
        print(f'파일 처리 중 오류가 발생했습니다: {error}')

    return [], []


def print_csv_data(title, headers, rows):
    '''
    제목과 함께 표 형식으로 데이터를 출력한다.
    '''
    print('\n' + '=' * 60)
    print(title)
    print('=' * 60)

    if not headers:
        print('출력할 헤더가 없습니다.')
        return

    print(', '.join(headers))

    if not rows:
        print('출력할 데이터가 없습니다.')
        return

    for row in rows:
        print(', '.join(row))


def convert_to_list(headers, rows):
    '''
    CSV 데이터를 Python 리스트 객체로 변환한다.
    각 행은 딕셔너리 형태로 저장한다.
    '''
    inventory_list = []

    for row in rows:
        item = {}

        for index in range(len(headers)):
            if index < len(row):
                item[headers[index]] = row[index]
            else:
                item[headers[index]] = ''

        inventory_list.append(item)

    return inventory_list


def find_flammability_index(headers):
    '''
    인화성 지수 컬럼의 인덱스를 찾는다.
    '''
    candidates = [
        'flammability',
        'flammability_index',
        'fire_risk',
        'fire_risk_index'
    ]

    for index in range(len(headers)):
        header = headers[index].strip().lower()
        if header in candidates:
            return index

    return -1


def to_float(value):
    '''
    문자열 값을 실수로 변환한다.
    변환 실패 시 0.0을 반환한다.
    '''
    try:
        return float(value.strip())
    except ValueError:
        return 0.0
    except AttributeError:
        return 0.0


def sort_by_flammability(rows, flammability_index):
    '''
    인화성 지수를 기준으로 내림차순 정렬한다.
    '''
    return sorted(
        rows,
        key=lambda row: to_float(row[flammability_index]),
        reverse=True
    )


def filter_dangerous_items(rows, flammability_index, threshold):
    '''
    인화성 지수가 threshold 이상인 항목만 추출한다.
    '''
    dangerous_rows = []

    for row in rows:
        if len(row) > flammability_index:
            flammability_value = to_float(row[flammability_index])
            if flammability_value >= threshold:
                dangerous_rows.append(row)

    return dangerous_rows


def save_csv_file(file_path, headers, rows):
    '''
    데이터를 CSV 파일로 저장한다.
    '''
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(','.join(headers) + '\n')

            for row in rows:
                file.write(','.join(row) + '\n')

        print('\n위험 물질 목록이 CSV 파일로 저장되었습니다.')
        print(f'저장 경로: {file_path}')

    except PermissionError:
        print(f'파일 저장 권한이 없습니다: {file_path}')
    except OSError as error:
        print(f'파일 저장 중 오류가 발생했습니다: {error}')


def save_binary_file(file_path, headers, rows):
    '''
    정렬된 목록을 이진 파일로 저장한다.
    헤더와 각 행을 줄 단위 텍스트로 만든 뒤 UTF-8 바이트로 변환하여 저장한다.
    '''
    try:
        with open(file_path, 'wb') as file:
            header_line = ','.join(headers) + '\n'
            file.write(header_line.encode('utf-8'))

            for row in rows:
                row_line = ','.join(row) + '\n'
                file.write(row_line.encode('utf-8'))

        print('\n정렬된 전체 목록이 이진 파일로 저장되었습니다.')
        print(f'저장 경로: {file_path}')

    except PermissionError:
        print(f'이진 파일 저장 권한이 없습니다: {file_path}')
    except OSError as error:
        print(f'이진 파일 저장 중 오류가 발생했습니다: {error}')


def read_binary_file(file_path):
    '''
    이진 파일을 읽어 UTF-8 문자열로 복원한 뒤 헤더와 데이터 행으로 반환한다.
    '''
    try:
        with open(file_path, 'rb') as file:
            binary_data = file.read()

        if not binary_data:
            print('이진 파일이 비어 있습니다.')
            return [], []

        text_data = binary_data.decode('utf-8')
        lines = text_data.splitlines()

        if not lines:
            print('이진 파일에 읽을 내용이 없습니다.')
            return [], []

        headers = lines[0].strip().split(',')
        rows = []

        for line in lines[1:]:
            stripped_line = line.strip()

            if stripped_line == '':
                continue

            row = stripped_line.split(',')
            rows.append(row)

        return headers, rows

    except FileNotFoundError:
        print(f'이진 파일을 찾을 수 없습니다: {file_path}')
    except PermissionError:
        print(f'이진 파일 접근 권한이 없습니다: {file_path}')
    except UnicodeDecodeError:
        print('이진 파일 디코딩 중 오류가 발생했습니다.')
    except OSError as error:
        print(f'이진 파일 처리 중 오류가 발생했습니다: {error}')

    return [], []


def main():
    input_file = 'Mars_Base_Inventory_List.csv'
    danger_file = 'Mars_Base_Inventory_danger.csv'
    binary_file = 'Mars_Base_Inventory_List.bin'
    threshold = 0.7

    headers, rows = read_csv_file(input_file)

    if not headers:
        print('CSV 파일을 읽지 못하여 프로그램을 종료합니다.')
        return

    print_csv_data('1. Mars_Base_Inventory_List.csv 원본 내용', headers, rows)

    inventory_list = convert_to_list(headers, rows)
    print('\n' + '=' * 60)
    print('2. Python 리스트(List) 객체로 변환한 결과')
    print('=' * 60)
    print(inventory_list)

    flammability_index = find_flammability_index(headers)

    if flammability_index == -1:
        print('\n인화성 지수 컬럼을 찾을 수 없습니다.')
        print('확인된 헤더:', headers)
        return

    sorted_rows = sort_by_flammability(rows, flammability_index)
    print_csv_data('3. 인화성이 높은 순으로 정렬한 목록', headers, sorted_rows)

    dangerous_rows = filter_dangerous_items(
        sorted_rows,
        flammability_index,
        threshold
    )
    print_csv_data(
        '4. 인화성 지수 0.7 이상 목록',
        headers,
        dangerous_rows
    )

    save_csv_file(danger_file, headers, dangerous_rows)
    save_binary_file(binary_file, headers, sorted_rows)

    binary_headers, binary_rows = read_binary_file(binary_file)
    print_csv_data(
        '5. Mars_Base_Inventory_List.bin 파일을 다시 읽어 출력한 내용',
        binary_headers,
        binary_rows
    )


if __name__ == '__main__':
    main()