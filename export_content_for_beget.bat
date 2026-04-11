@echo off
echo =========================================================================
echo EXPORTING CONTENT FOR BEGET (USERS AND ORDERS ARE SAFE!)
echo =========================================================================
echo This tool exports site settings, news, portfolio, services, and 
echo knowledge base. Users, reviews, and tickets/orders are NOT exported
echo to ensure your live data on the server is preserved!
echo.
echo Please wait...

cd mysite
set PYTHONUTF8=1
..\.venv\Scripts\python.exe manage.py dumpdata main news portfolio services knowledge_base --natural-primary --natural-foreign -e contenttypes -e auth.Permission --indent 4 -o ..\content_for_beget.json

echo.
echo DONE! 
echo 'content_for_beget.json' created in the project root.
echo =========================================================================
echo UPLOAD THE JSON FILE TO BEGET AND FOLLOW import_on_beget.txt INSTRUCTIONS
echo =========================================================================
pause
