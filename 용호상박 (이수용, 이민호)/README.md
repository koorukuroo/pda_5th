# AWS AMI 및 인스턴스 성능 비교
## 1. 실험 개요
이 실험에서는 **Amazon Linux 2023 AMI**와 **Ubuntu 24.04 LTS**에서 "식사하는 철학자 문제"를 해결하는 소스코드를 실행하며 성능을 비교합니다. 이 문제는 여러 프로세스 또는 스레드가 동시에 동작할 때 발생하는 **교착 상태**를 설명하는 데 유용합니다. 또한, **세마포어**를 사용해 교착 상태를 해결하는 방법과 그에 따른 성능 차이를 확인했습니다.

<div align="center">
  <img src="https://github.com/user-attachments/assets/6b8faec0-d03f-4723-9b0c-27d88d9ac325">
</div>

실험은 AWS 인스턴스 패밀리별로 진행되었으며, 각 인스턴스에서 소스코드를 10회 실행한 후, 실행 시간을 측정하고 평균값을 계산하여 비교했습니다. **time 명령어**를 사용해 다음과 같은 실행 시간을 측정했습니다:
- **real**: 실제 경과 시간
- **user**: CPU 연산 수행 시간
- **sys**: 시스템 콜 처리 시간
### AMI 및 아키텍처 설정
- **AMI**: Amazon Linux 2023, Ubuntu 24.04 LTS
- **아키텍처**: 64비트(x86)
- **테스트 환경**: AWS m-family, c-family, t2-family 인스턴스 사용
## 2. 실험 방법
각 AMI에서 동일한 소스코드를 사용하여 "식사하는 철학자 문제"를 해결하는 프로그램을 작성한 후, 10회 실행하여 눅스에서 프로그램이 실행된 시간을 측정할 때 사용하는 세 가지 주요 개념인 real, user, sys를 time 명령어를 이용해 구함.
### 실행시간 측정
- **real**: 프로그램이 실행된 실제 경과 시간
- **user**: CPU에서 실제로 연산을 수행한 시간
- **sys**: 시스템 콜 처리에 소요된 시간
<div align="center">
  <h1>Amazon Linux</h1>
  <img src="https://github.com/user-attachments/assets/eef423c3-c8ef-41cf-ac19-d54bcc94e2c0">
  <img src="https://github.com/user-attachments/assets/9609283c-f91b-4bff-8058-3a36160e083b">
  <img src="https://github.com/user-attachments/assets/9411cc04-f6f0-4b4f-8646-351c4c45a66a">
</div></br>

<div align="center">
  <h1>Ubuntu</h1>
  <img src="https://github.com/user-attachments/assets/c3b6d542-acdd-4098-b954-3004f45dd58e">
  <img src="https://github.com/user-attachments/assets/8453a870-fbe5-4540-979f-6a84ca4fec38">
  <img src="https://github.com/user-attachments/assets/1898ed4d-45c9-4d8f-a071-8c18a5040028">
</div>


## 3. 결론
user시간과 sys시간은 인스턴스 크기가 커질 수록, 대체로 길어지는 경향이 있으며 그에따라, 코드를 실행하는 Real time이 길어짐. (성능이 떨어짐)
AMI같은 경우에는 m-family, c-family같은 경우는 Ubuntu의 성능이 대체로 더 좋게 나왔음(실행시간 감소)
t2-family에서는 비슷한 속도를 보였다.
<br>
## AMI 및 인스턴스 CPU 최대 사용량 분석
<div align="center">
  <h2>Amazon Linux</h2>
  <img src="https://github.com/user-attachments/assets/a8e55be1-3449-4e0d-a8fa-2038598d7723">
</div></br>
<div align="center">
  <h2>Ubuntu</h2>
  <img src="https://github.com/user-attachments/assets/af433f4f-3f6d-4de1-8a4a-25baa5a250e6">
</div>

### 분석결과
인스턴스 크기가 커질 수록 부하의 분산이 잘 되어서 CPU 사용률이 줄어들 것으로 예상 되었으나, 관련이 없는 결과가 나타남.

## 예시 코드
```
#include <stdio.h>
#include <time.h>
#include <pthread.h>
#include <semaphore.h>

#define NUM 5
#define SIMULATIONS 10

sem_t forks[NUM]; // forks
sem_t once;

void *philosopher(void *);

void run_simulation(int run_number, double *duration) {
    pthread_t threads[NUM];
    
    // 세마포어 초기화
    for (int i = 0; i < NUM; i++)
        sem_init(&forks[i], 0, 1);
    sem_init(&once, 0, 1);
    
    int start_time, end_time;
    start_time = clock(); // time start!
    
    // 철학자 스레드 생성
    for (unsigned long i = 0; i < NUM; i++)
        pthread_create(&threads[i], NULL, philosopher, (void*)i);
    
    // 철학자 스레드 종료 대기
    for (int i = 0; i < NUM; i++)
        pthread_join(threads[i], NULL);
    
    end_time = clock(); // time end!
    
    // 결과 출력
    *duration = (double)(end_time - start_time) / CLOCKS_PER_SEC;
    printf("Simulation %d - NO DEADLOCK\n", run_number + 1);
    printf("Duration: %.5f seconds\n\n", *duration);
    
    // 세마포어 정리
    for (int i = 0; i < NUM; i++)
        sem_destroy(&forks[i]);
    sem_destroy(&once);
}

void pickup(int philosopher_num) {
    sem_wait(&forks[philosopher_num % NUM]);
}

void putdown(int philosopher_num) {
    sem_post(&forks[philosopher_num % NUM]);
}

void thinking(int philosopher_num) {
    printf("philosopher %d is thinking\n", philosopher_num);
}

void eating(int philosopher_num) {
    printf("philosopher %d is eating\n", philosopher_num);
}

void *philosopher(void *arg) {
    int philosopher_num = (int)(unsigned long)arg;
    int eating_count = 100; // 적당한 반복 횟수
    while (eating_count > 0) {
        // 좌우 포크 잡는 순서 결정
        if (philosopher_num % 2 == 0) {
            pickup(philosopher_num);
            printf("philosopher %d picks up the fork %d.\n", philosopher_num, philosopher_num);
            pickup((philosopher_num + 1) % NUM);
            printf("philosopher %d picks up the fork %d.\n", philosopher_num, (philosopher_num + 1) % NUM);
        } else {
            pickup((philosopher_num + 1) % NUM);
            printf("philosopher %d picks up the fork %d.\n", philosopher_num, (philosopher_num + 1) % NUM);
            pickup(philosopher_num);
            printf("philosopher %d picks up the fork %d.\n", philosopher_num, philosopher_num);
        }
        eating(philosopher_num);
        eating_count--;
        putdown((philosopher_num + 1) % NUM);
        printf("philosopher %d puts down the fork %d.\n", philosopher_num, (philosopher_num + 1) % NUM);
        putdown(philosopher_num);
        printf("philosopher %d puts down the fork %d.\n", philosopher_num, philosopher_num);
        thinking(philosopher_num);
    }
    return NULL;
}

int main() {
    double total_duration = 0.0;
    double duration;
    
    // 시뮬레이션 10번 실행
    for (int i = 0; i < SIMULATIONS; i++) {
        printf("========== Simulation %d ==========\n", i + 1);
        run_simulation(i, &duration);
        total_duration += duration;
    }
    
    // 평균 시간 계산
    double average_duration = total_duration / SIMULATIONS;
    printf("========== AVERAGE TIME ==========\n");
    printf("Average Duration: %.5f seconds\n", average_duration);
    
    return 0;
}

```

### 향후 계획
Amazon Linux 2023과 Ubuntu 24.04 LTS에서 인스턴스 패밀리인 m5, c5, t2에서 인스턴스의 크기를 늘릴 수록 "식사하는 철학자 코드"의 실행 시간이 대체적으로 늘어나는 것을 알 수 있었습니다. 하지만 인스턴스 크기가 커질 수록 CPU 사용량은 상관관계를 보이지 않았습니다. 이를 위해 추후 이에 영향을 미치는 요인들을 파악할 계획입니다. 
->

