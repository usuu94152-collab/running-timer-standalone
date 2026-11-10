# 러닝 타이머 Standalone

로그인·Google Sheets 연결 없이 영상과 상황에 맞춰 달리는 독립 사이트입니다.
원본 `usuu94152-collab/running-timer`와 별도로 운영합니다.

## 포함된 기능

- 301번 버스 · 지그재그 · 이어달리기 · 장애물, 4개 탭
- 종목별 도입 영상과 성공·실패 영상, 배경 이미지, 상황 설명
- 현재 타이머, 랩, 리셋, 다시 도전, 영상 다시 재생
- 스페이스바와 사용자 지정 키·게임패드 부저

로그인, 학생명단, 교사 페이지, 반 선택, 평가, 최고기록·측정기록 저장,
Google Apps Script와 API 호출은 포함하지 않습니다.
부저 키 설정만 현재 브라우저에 저장합니다. 원본 사이트와 다른 저장 키를 사용합니다.

## 실행

사이트 파일은 모두 `site/` 안에 있습니다. 별도 설치·빌드·환경 변수·인증키가 필요하지 않습니다.

```sh
python3 -m http.server 8000 --directory site
```

브라우저에서 로컬 서버를 열면 됩니다.
오프라인 사용은 `site/` 전체를 컴퓨터에 복사한 뒤 위 명령으로 실행하세요.
영상·이미지를 모두 포함하므로 로컬 서버 실행에는 인터넷이 필요하지 않습니다.

## GitHub Pages 배포

독립 저장소 `usuu94152-collab/running-timer-standalone`에 올린 뒤
저장소 Settings → Pages → Build and deployment → Source에서 **GitHub Actions**를 선택합니다.
포함된 `.github/workflows/pages.yml`이 `main` 푸시 시 `site/`만 배포합니다.
처음에는 Actions → Deploy standalone timer → Run workflow로 실행할 수 있습니다.
원본 저장소와 기존 Apps Script 설정은 변경할 필요가 없습니다.

다른 정적 호스팅 서비스에서는 `site/`를 게시 디렉터리로 지정하세요.

## 검증

Python Playwright와 Chromium이 설치된 환경에서 실행합니다.

```sh
python3 tests/smoke.py
```

테스트는 임시 로컬 서버에서 PC·모바일 4종 탭, 영상 로딩, 타이머·랩·리셋,
성공·실패 결과, 키보드 부저와 서버 연결 없는 측정을 검증합니다.
외부 요청·API 호출이나 로그인 UI가 생기면 실패합니다.
