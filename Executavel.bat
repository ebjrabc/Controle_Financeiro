@echo off
setlocal
cd /d "%USERPROFILE%\controle"
:: Verifica se o Python está instalado
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python não encontrado. Instalando...

    :: Executa o instalador silenciosamente
    python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    :: Aguarda alguns segundos para garantir que a instalação finalize
    timeout /t 10 >nul

    :: Verifica novamente
    where python >nul 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        echo Falha na instalação do Python.
        exit /b 1
    )
)

echo Python encontrado. Executando o script...
python app_inicio.py

endlocal
pause