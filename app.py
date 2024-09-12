from flask import Flask, render_template_string
import time
import psutil

app = Flask(__name__)

def perform_heavy_operations():
    # 특정 무거운 연산(인스턴스에 부하를 주는)을 수행하여 CPU, 메모리 사용량을 증가
    start_time = time.time()
    total = 0
    for i in range(1000000):
        total += i ** 2
    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time

def measure_performance():
    execution_times = []
    cpu_usages = []
    mem_usages = []
    disk_write_speeds = []

    for _ in range(5):
        # 성능 측정 전
        cpu_start = psutil.cpu_percent(interval=1)
        mem_start = psutil.virtual_memory().percent
        disk_io_start = psutil.disk_io_counters().write_bytes
        
        # 실행 시간 측정
        execution_time = perform_heavy_operations()
        execution_times.append(execution_time)
        
        # 성능 측정 후
        cpu_end = psutil.cpu_percent(interval=1)
        mem_end = psutil.virtual_memory().percent
        disk_io_end = psutil.disk_io_counters().write_bytes
        
        cpu_usages.append(cpu_end - cpu_start)
        mem_usages.append(mem_end - mem_start)
        disk_write_speeds.append(disk_io_end - disk_io_start)
        
    # 평균값 계산
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
            <title>멀티스레딩을 통한 성능 인스턴스 성능 테스트.</title>
        </head>
        <body>
            <h1>System Performance Test Results</h1>
            <p><strong>Execution Time (Avg in 5) :</strong> {avg_execution_time:.2f} seconds</p>
            <p><strong>CPU Usage (Avg in 5) :</strong> {avg_cpu_usage:.2f}%</p>
            <p><strong>Memory Usage (Avg in 5) :</strong> {avg_mem_usage:.2f}%</p>
            <p><strong>Disk Write Speed (Avg in 5) :</strong> {avg_disk_write_speed / (1024 * 1024):.2f} MB/s</p>
        </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
