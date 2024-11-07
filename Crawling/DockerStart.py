import docker
import os 

def remove_all_containers():
    # Docker 클라이언트 생성
    client = docker.from_env()
    
    # 실행 중인 모든 컨테이너 가져오기
    containers = client.containers.list()
    
    for container in containers:
        print(f"컨테이너 중지 및 제거: {container.id}")
        container.stop()
        container.remove()

def makeSubtitle(path ='./resource'):

    # path = os.path.expanduser(path)
    path = os.path.abspath(path)
    
    # Docker 클라이언트 생성
    client = docker.from_env()

        # 1. Docker 이미지 풀
    print("Docker 이미지를 풀링하는 중입니다...")

    image = client.images.pull("mmcauliffe/montreal-forced-aligner:latest")
    print('Docker 이미지 풀링 완료')

    remove_all_containers()

    print("컨테이너를 실행하는 중입니다...")
    container = client.containers.run(
        "mmcauliffe/montreal-forced-aligner:latest",
        volumes={path: {'bind': '/data', 'mode': 'rw'}},  # 사용자 경로 수정 필요
        tty=True,
        detach=True  # 백그라운드에서 실행
    )
    print(f"실행 중인 컨테이너 ID: {container.id}")

    print(f'모델 설치 중입니다...')
    commands = [
            "mfa model download acoustic korean_mfa",
            "mfa model download dictionary korean_mfa",
            ]

    for command in commands:
        print(f"실행 중인 명령어: {command}")
        exit_code, output = container.exec_run(command, tty=True)
        print(output.decode("utf-8"))  # 명령어 결과 출력

    print('모델 설치 완료')

    print('자막 생성중입니다...')
    exit_code, output = container.exec_run("mfa align --clean --output_format json /data korean_mfa korean_mfa /data", tty=True)

    print('자막 생성 완료')

    container.stop()

if __name__== '__main__':
    makeSubtitle('./resource')