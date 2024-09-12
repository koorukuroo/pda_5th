from flask import Flask, render_template_string
import time
import psutil
import os
import threading

app = Flask(__name__)

def heavy_task():
    # CPU 자원 소비를 위한 무거운 계산 작업
    total = 0
    for i in range(100000):
        total += i ** 2
    return total

def multi_threading():
    # 멀티스레딩을 통한 CPU 사용률 증가
    threads = []
    start_time = time.time()

    # CPU 부하 증가 위해 여러 스레드 생성
    for _ in range(10):  # CPU 코어 수에 따라 스레드 수 조정 
        thread = threading.Thread(target=heavy_task)
        threads.append(thread)
        thread.start()

    # 스레드 완료 대기
    for thread in threads:
        thread.join()

    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time

def write_large_file():
    # 대용량 파일 쓰기 작업 - 디스크 쓰기 속도 측정
    file_name = "temp_large_file.txt"
    with open(file_name, "w") as file:
        file.write("a" * 10**8)
    os.sync()  # 모든 내부 버퍼를 디스크에 플러시
    os.remove(file_name)

def measure_performance():
    execution_times = []
    cpu_usages = []
    mem_usages = []
    disk_write_speeds = []

    for _ in range(5):
        cpu_start = psutil.cpu_percent(interval=1)
        mem_start = psutil.virtual_memory().used  # 메모리 사용 시작
        disk_io_start = psutil.disk_io_counters().write_bytes
        
        execution_time = multi_threading()
        execution_times.append(execution_time)
        
        write_large_file()  # 디스크 쓰기 속도 측정
        
        cpu_end = psutil.cpu_percent(interval=1)
        mem_end = psutil.virtual_memory().used
        disk_io_end = psutil.disk_io_counters().write_bytes
        
        cpu_usages.append(cpu_end - cpu_start)
        mem_usages.append((mem_end - mem_start) / (1024**2))  # MB 단위로 변환
        disk_write_speeds.append((disk_io_end - disk_io_start) / (1024**2))  # MB/s 단위로 변환

    avg_execution_time = sum(execution_times) / len(execution_times)
    avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)
    avg_mem_usage = sum(mem_usages) / len(mem_usages)
    avg_disk_write_speed = sum(disk_write_speeds) / len(disk_write_speeds)
    
    return avg_execution_time, avg_cpu_usage, avg_mem_usage, avg_disk_write_speed

@app.route('/')
def test_results():
    avg_execution_time, avg_cpu_usage, avg_mem_usage, avg_disk_write_speed = measure_performance()
    html = f"""
    <html>
        <head>
            <title>시스템 성능 테스트 결과</title>
        </head>
        <body>
            <h1>시스템 성능 테스트 결과</h1>
            <p><strong>평균 실행 시간 (5회 평균) :</strong> {avg_execution_time:.2f} 초</p>
            <p><strong>CPU 사용률 (5회 평균) :</strong> {avg_cpu_usage:.2f}%</p>
            <p><strong>메모리 사용량 (5회 평균) :</strong> {avg_mem_usage:.2f} MB</p>
            <p><strong>디스크 쓰기 속도 (5회 평균) :</strong> {avg_disk_write_speed:.2f} MB/s</p>
        </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
