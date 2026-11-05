Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c timeout /t 20 /nobreak >nul && cd /d C:\Projetos\home_mini_automator && python main.py", 0