# 로그 분석 보고서

## 1. 개요
본 보고서는 `mission_computer_main.log` 파일의 로그 데이터를 분석하여
로켓 임무 수행 과정에서 발생한 사고의 원인을 분석하고 정리한 문서이다.

## 2. 분석 대상
- 파일명: mission_computer_main.log
- 데이터 형식: CSV
- 인코딩: UTF-8
- 분석 도구: Python 3.x
- 실행 파일: main.py

## 3. 분석 방법

로그 데이터를 시간 순서대로 분석하여 다음 항목을 확인하였다.

1. 정상 동작 이벤트
2. 시스템 상태 메시지
3. 이상 징후 발생 시점
4. 사고 발생 로그

또한 로그의 timestamp 기준으로 이벤트 흐름을 정리하여
사고 발생 전후의 시스템 상태를 분석하였다.

## 4. 로그 흐름 분석

### 4.1 발사 준비 단계

10:00 ~ 10:23

주요 이벤트

- Rocket initialization process started
- Power systems online
- Communication established
- Pre-launch checklist initiated
- Propulsion check completed

이 단계에서는 모든 시스템이 정상 상태로 확인된다.

---

### 4.2 발사 및 상승 단계

10:25 ~ 10:57

주요 이벤트

- Engine ignition sequence started
- Liftoff
- Max-Q passed
- Stage separation
- Second stage ignition

로켓 발사 및 상승 과정에서 이상 로그는 발견되지 않았다.

---

### 4.3 궤도 진입 단계

10:57 ~ 11:05

주요 이벤트

- Entering planned orbit
- Orbital operations initiated
- Satellite deployment successful

위 로그로부터 임무 목표였던 **위성 배치가 정상적으로 수행**되었음을 확인할 수 있다.

---

### 4.4 재진입 및 착륙 단계

11:10 ~ 11:28

주요 이벤트

- Deorbit maneuvers initiated
- Reentry sequence started
- Heat shield performing as expected
- Main parachutes deployed
- Rocket safely landed

재진입 및 착륙 과정 또한 정상적으로 수행되었다.

---

### 4.5 임무 종료

11:30
Mission completed successfully.
Recovery team dispatched.


로그 기준으로 임무는 성공적으로 종료되었다.

---

## 5. 사고 발생 로그

이후 다음과 같은 이상 이벤트가 발생하였다.

2023-08-27 11:35:00 Oxygen tank unstable.
2023-08-27 11:40:00 Oxygen tank explosion.


이 로그는 다음과 같은 순서를 보여준다.

1. 산소 탱크 상태 불안정 감지
2. 약 5분 후 산소 탱크 폭발 발생

따라서 **직접적인 사고 원인은 산소 탱크의 불안정 상태로 인한 폭발**로 판단된다.

---

## 6. 사고 원인 분석

로그 데이터를 기반으로 분석한 사고 진행 과정은 다음과 같다.

1. 임무 종료 후 로켓은 착륙 상태에 있었다.
2. 11:35에 산소 탱크 상태가 불안정해졌다는 로그가 발생하였다.
3. 5분 후 산소 탱크 폭발 로그가 발생하였다.

이는 다음과 같은 가능성을 시사한다.

- 산소 탱크 압력 상승
- 산소 탱크 구조적 손상
- 연료 및 산소 잔류 가스 반응

로그 데이터상 **폭발 직전 이벤트는 산소 탱크 불안정 상태**이므로  
이 이벤트가 사고의 직접적인 원인으로 판단된다.

---

## 7. 결론

로그 분석 결과 로켓 발사, 궤도 진입, 위성 배치, 재진입 및 착륙 과정은 모두 정상적으로 수행되었다.

그러나 임무 종료 이후 **산소 탱크의 불안정 상태가 발생하였고**
약 5분 후 **산소 탱크 폭발 사고가 발생하였다.**

따라서 본 사고의 원인은 다음과 같이 정리할 수 있다.

**산소 탱크 불안정 상태로 인한 폭발**

---

## 8. 향후 개선 방안

유사 사고 방지를 위해 다음과 같은 조치가 필요하다.

1. 산소 탱크 압력 모니터링 강화
2. 착륙 후 연료 및 산소 시스템 안정화 절차 강화
3. 산소 탱크 상태 자동 진단 시스템 도입
4. 이상 상태 발생 시 즉시 안전 배출 시스템 적용

---

## 9. 코드 설명

`main.py`는 Python 기본 파일 입출력 기능을 사용하여 다음 기능을 수행한다.

- `mission_computer_main.log` 파일을 UTF-8 인코딩으로 연다.
- 파일 전체 내용을 읽어 화면에 출력한다.
- 파일이 없거나 권한이 없거나 인코딩 문제가 발생할 경우 예외 처리를 수행한다.

