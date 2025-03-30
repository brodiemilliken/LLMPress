@echo off
echo Building LLMPress AI services...
cd %~dp0

REM Build the services defined in docker-compose.yml
docker-compose build

echo.
echo Build process completed.
echo To start the services, run llmpress-start.bat