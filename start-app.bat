@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║               🚀 TODO LIST APPLICATION 🚀                   ║
echo ║                                                              ║
echo ║                 Iniciando aplicación...                     ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📦 Levantando contenedores...
docker compose up --build -d

echo.
echo ⏳ Esperando que los servicios se inicialicen...
timeout /t 10 /nobreak > nul

echo.
echo ╔══���═══════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║               ✅ ¡APLICACIÓN LISTA! ✅                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📱 ENLACES DE ACCESO:
echo.
echo 🌐 Aplicación Principal:
echo    ➜ http://localhost:8080
echo.
echo 🔧 Servicios Individuales:
echo    ➜ Frontend (React):     http://localhost:5173
echo    ➜ Backend API:          http://localhost:8080/api/
echo    ➜ Admin Django:         http://localhost:8080/admin/
echo    ➜ API Documentation:    http://localhost:8080/api/schema/swagger-ui/
echo.
echo 🗄️  Base de Datos:
echo    ➜ PostgreSQL:           localhost:5432
echo    ➜ Database: todo_database
echo    ➜ User: postgres
echo.
echo ⚡ COMANDOS ÚTILES:
echo.
echo 📊 Ver estado:           docker compose ps
echo 📋 Ver logs:             docker compose logs -f
echo 🛑 Detener:              docker compose down
echo 🔄 Reiniciar:            docker compose down -v ^&^& docker compose up --build
echo.
echo 🎉 ¡Abre tu navegador en: http://localhost:8080
echo.
echo 💡 Presiona cualquier tecla para abrir el navegador automáticamente...
pause > nul
start http://localhost:8080
echo.
echo ✨ ¡Disfruta usando la aplicación!
echo.
pause