![Python: Version](https://img.shields.io/badge/python-3.8.10-blue)
![Django: Version](https://img.shields.io/badge/Django-3.1.14-blue)
![MariaDB: Version](https://img.shields.io/badge/MariaDB-10.3.32-blue)
![Amazon S3](https://img.shields.io/badge/AmazonS3-569A31.svg?logo=amazon-s3&logoColor=white)

# kodeal backEnd
### 2022 컴퓨터공학부 종합설계 S2-1 백엔드

kodeal web page using django<br/>
<b>This Project service is to teach python language for coding beginner</b>

 최근 개발자 직업군에 대한 관심이 높아진 국내에서 대학에 진학한 학생, 코딩에 관심이 있어 학습을 시작하고자 하는 일반인 등 초보 공학도들이 늘어나고 있습니다. 시중에는 코딩에 입문하는 사람들을 위한 좋은 강의들이 많습니다. 하지만 강의로는 알 수 없는 내용들에 대해서는 직접 인터넷 검색을 통해 해답을 얻어야 하고, 전문 지식이 부족한 입문자들에게는 이러한 과정이 어렵게 다가올 수 있습니다. 
 저희는 코딩 입문자들도 쉽게 질문을 하고, 원하는 정보를 빠르게 얻어 자습 환경이 부족한 학생과 일반인 등에게 도움이 될 수 있도록 하는 서비스를 개발하고 있습니다. OpenAI Codex를 이용하여 사용자의 질문에 대해 의도가 무엇인지 분석한 결과를 받아 곧바로 보여줌으로써 사용자로 하여금 프로그래밍에 대한 진입장벽을 낮추는 것을 목표로 하고 있습니다. 

## Getting Started

### Pre-requisites
* 먼저 백엔드 개발에 필요한 Python 패키지를 다운로드 한다.

#### 1. 가상 환경 작업
  * 가상 환경을 만들 디렉터리로 이동한 뒤 **cmd 환경**에서 다음의 명령어로 Python 가상 환경을 실행한다.
  * 아래의 명령어는 가상 환경의 이름을 kodeal로 설정했을 때의 예시이다.
  
  ```cmd
  python -m venv kodeal
  cd kodeal/Scripts
  activate
  ```
  
#### 2. Django 설치
  * 가상 환경에 진입한 상태에서 `pip install django==3.1.14` 명령으로 Django를 설치한다.
  * 경고 메시지가 출력된다면 `python -m pip install --upgrade pip` 명령으로 pip를 최신 버전으로 한 후 다시 시도한다.

#### 3. Django 프로젝트 생성
  * 프로젝트를 생성할 위치로 이동하여 다음의 명령으로 Django 프로젝트를 생성한다.

  ```cmd
  django-admin startproject config .
  ```
  
#### 4. Pycharm으로 Django 프로젝트 실행
  * Pycharm으로 해당 Django 프로젝트를 연 뒤, **Python Interpreter 설정**을 **가상환경의 Python**으로 설정한다.

#### 5. GitHub Clone
  * 다음의 명령으로 본 프로젝트(백엔드)의 내용을 가져온다.

  ```git
  git clone https://github.com/yeseong31/backEnd.git
  ```
  
  * 프로젝트 내 config/my_settings.py 파일을 새로 생성하여 [다음의 Wiki 내용을 참고](https://github.com/yeseong31/Itrencotech-web-page/wiki/my_settings.py-%EC%84%A4%EC%A0%95)하여 설정값을 구성한다.

## 🏠 Home Page
<img width="1280" alt="image" src="https://user-images.githubusercontent.com/66625672/155848689-05d9ba0f-559b-4409-95d5-2a5f18905761.png">

## 🛠️ Built With
* ![Python](https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white)
* ![Django](https://img.shields.io/badge/Django-092E20.svg?style=flat-square&logo=Django&logoColor=white)
* ![MariaDB](https://img.shields.io/badge/MariaDB-003545.svg?style=flat-square&logo=MariaDB&logoColor=white)
* ![OpenAI](https://img.shields.io/badge/OpenAI-412991.svg?style=flat-square&logo=OpenAI&logoColor=white)
* ![Microsoft Azure](https://img.shields.io/badge/Microsoft_Azure-0078D4?style=flat-square&logo=Microsoft-azure&logoColor=white)  
  
</details>

## 🔧 Tools
* ![Visual Studio Code](https://img.shields.io/badge/Visual_Studio_Code-007ACC.svg?style=flat-square&logo=VisualStudioCode&logoColor=white) 
* ![PyCharm](https://img.shields.io/badge/PyCharm-000000.svg?style=flat-square&logo=PyCharm&logoColor=white) 
* [![Trello](https://img.shields.io/badge/Trello-0052cc?style=flat-square&logo=Trello&logoColor=white&link=https://trello.com/b/mrg8i2EQ/roadmap/)](https://trello.com/b/mrg8i2EQ/roadmap/)
* [![Slack](https://img.shields.io/badge/Slack-4a154b.svg?style=flat-square&logo=Slack&logoColor=white&link=https://w1627955690-ob9739492.slack.com/ssb/redirect)](https://w1627955690-ob9739492.slack.com/ssb/redirect)

## 🖋️ Basic Layout
![image](https://user-images.githubusercontent.com/66625672/161430320-a59ec796-0448-45ce-b3ae-b048ecff6dd6.png)
![image](https://user-images.githubusercontent.com/66625672/147870771-0853ea7c-57bd-48f9-b2a1-71ee739e7e36.png)

## ✨ Service Flow Chart
![image](https://user-images.githubusercontent.com/66625672/161430423-24ca87f0-f526-4441-a7b7-eb92199d6af8.png)

## 💾 Database
<img width="891" alt="image" src="https://user-images.githubusercontent.com/66625672/168822348-6a0cdac3-949f-48ba-99ea-d04f1b3b441f.png">

## License
이 문서는 **한국공학대학교 컴퓨터공학부**의 **"종합설계"** 교과목에서
프로젝트 "**Kodeal**(인공지능 코딩 Q&A 서비스)"을 수행하는
S2-1(김정현, 권종석, 한민, 한예성)에 의해 작성된 것으로,
본 프로젝트를 사용하기 위해서는 팀원들의 허락이 필요합니다.

## 🙋 Contributor
* [jongseok Kwon](https://github.com/himJJong) <br>
* [Min](https://github.com/Proals) <br>
* [yeseong31](https://github.com/yeseong31) [![Naver Badge](https://img.shields.io/badge/yeseong31@naver.com-04ce5c?style=flat-square&logo=Naver&logoColor=white&link=mailto:yeseong31@Naver.com)](mailto:yeseong31@naver.com)<br>

## 📫 Contacts
* [![Gmail Badge](https://img.shields.io/badge/kodealtest@gmail.com-d14836?style=flat-square&logo=Gmail&logoColor=white&link=mailto:kodealtest@gmail.com)](mailto:kodealtest@gmail.com)
