@echo off
echo Stopping LLMPress AI services...
cd %~dp0
docker-compose down
echo Services stopped.