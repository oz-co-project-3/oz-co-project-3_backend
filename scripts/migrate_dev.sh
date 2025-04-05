#!/bin/bash

echo "🚀 [MIGRATE] 환경변수 로딩 중..."

# 환경파일 경로 설정 (prod 환경 기준)
ENV_FILE=".envs/.dev.env"

if [ -f "$ENV_FILE" ]; then
  export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
  echo ".env 로딩 완료: $ENV_FILE"
else
  echo ".env 파일이 존재하지 않습니다: $ENV_FILE"
  exit 1
fi

echo "aerich 마이그레이션 시작..."

# 마이그레이션 실행
poetry run aerich upgrade

echo "🎉 마이그레이션 완료!"