@echo off
echo Starting LLMPress AI services...
cd %~dp0
docker-compose up -d
echo Services started! API is available at http://localhost:8000