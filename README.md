# 러브러브샷

- 러브러브샷은 커플 딥페이크 ai 서비스입니다.
- 관련된 ppt url : https://mtvs.kr/user/project/view

<p>
<img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/8dd0fe2b-0aaf-4710-9040-5364f243aaf3" width="200" height="250"/>
<img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/ed3f3d42-90f2-47d8-8c45-ee86f3ffe537" width="200" height="250"/>
<br/>
<em>인채와 카*나를 합성한 커플 사진 1</em>  
</p>

<p>
<img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/7b02af2e-5bbf-426c-9057-5094004f00f4" width="50%" height="50%"/>
<br/>
<em>인채와 카*나를 합성한 커플 사진 2</em>  
</p>

<p>
<img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/0621d612-0db8-421a-bd64-bfb09875420e"  width="50%" height="50%"/>
<br/>
<em>서비스 UI 사진 1</em>  
</p>

<p>
<img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/d03009f1-30fb-4806-af36-dffc513aa0fb"  width="50%" height="50%"/>
<br/>
<em>서비스 UI 사진 2</em>  
</p>

## 아키텍처

<p>
<img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/abe085ee-af2e-4791-b727-ad660a2ea35b"  width="50%" height="50%"/>
<br/>
<em>이번 프로젝트는 fastapi 서버만 구성하였습니다.</em>  
</p>

- 이번 서비스는 도메인을 구매하고 서비스를 배포해서, 발표하는 동안 모든 청중자들이 사용할 수 있는 서비스를 만드는 것이 목표였습니다.
- 약 50명의 유저가 동시에 접속해도 문제없이 서비스가 유지될 수 있어야 했습니다.
- 문제는 한번 ai모델을 실행시킬 때마다 gpu vram 3기가를 사용하는 점이었습니다.
- 한번 점유한 gpu를 다른 유저에게 할당할 수가 없어서, redis 큐를 이용해서 사용자들의 요청을 하나하나 쌓아두었습니다.
- nginx로 트래픽을 나누고, 나눠진 리퀘스트는 레디스 큐에 쌓여 자신의 차례를 기다리는 스케쥴링 시스템을 구성했습니다.

## ai
### 배경 사진
- 합성 배경이 되는 사진은 초상권 때문에 함부로 다른 사람들의 사진을 사용할 수 없었습니다.
- 스테이블 디퓨전을 학습시켜서 배경사진을 생성하기로 했습니다.
- 기본 모델은 sd 1.5버전, lora 모델은 Japan Vibes - Film color를 이용했습니다.
- 프롬프팅을 공부해서 두명이 나올 수 있는 커플 사진을 생성했습니다.
- 예시 사진들
  <p>
  <img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/23b9f0b8-823e-4d72-a383-3e53815a93c3"  width="30%" height="30%"/>
  <img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/f4a60403-19d0-4aca-9248-78f5d4d6042b"  width="30%" height="30%"/>
  <img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/115bff44-5a2a-4196-9ac6-5b8fc9b1a571"  width="30%" height="30%"/>
  <br/>
  </p>
  
### 화질 개선
- 사용하는 모델이 기본적으로 512px를 바탕으로 실행이 되기 때문에, 화질 키우는 ai모델을 도입했습니다.
- gfpgan모델은 사진의 화질을 올릴 수 있는 모델입니다.
  <p>
    <img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/7ebacfea-2ceb-47f4-890b-4e5fbee6f22e"  width="20%" height="20%"/>
    <img src="https://github.com/lakecrimsonn/loveloveshot/assets/118543824/fede5f66-e171-4dcd-8a45-8c476ae27156"  width="20%" height="20%"/>
    <br/>
    <em>인채와 카*나 합성한 사진</em>  
  </p>

### 딥페이크 모델
- 유명한 모델 inswapper128은 상업적으로 이용이 불가합니다.
- 상업적으로 사용할 수 있는 모델이 필요했고, mobile face swap을 개선해서 사용하기로 했습니다.
- https://github.com/Seanseattle/MobileFaceSwap
  <p>
    <img src="https://github.com/Seanseattle/MobileFaceSwap/raw/master/docs/video.gif"  width="50%" height="50%"/>
    <br/>
  </p>
  

    
