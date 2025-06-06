n#!/bin/bash

# Colores para el output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Función para mostrar el banner inicial
show_initial_banner() {
    clear
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║               🚀 TODO LIST APPLICATION 🚀                   ║"
    echo "║                                                              ║"
    echo "║                 Iniciando aplicación...                     ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Función para mostrar el banner final
show_final_banner() {
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║               ✅ ¡APLICACIÓN LISTA! ✅                      ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Función para verificar servicios
check_services() {
    echo -e "${BOLD}${BLUE}🔍 VERIFICANDO SERVICIOS...${NC}"
    echo ""
    
    # Verificar frontend
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Frontend: Funcionando${NC}"
    else
        echo -e "   ${YELLOW}⏳ Frontend: Iniciando...${NC}"
    fi
    
    # Verificar backend API
    if curl -s http://localhost:8080/api/ > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Backend API: Funcionando${NC}"
    else
        echo -e "   ${YELLOW}⏳ Backend API: Iniciando...${NC}"
    fi
    
    echo ""
}

# Función para mostrar los enlaces
show_links() {
    echo -e "${BOLD}${BLUE}📱 ENLACES DE ACCESO:${NC}"
    echo ""
    echo -e "${GREEN}🌐 Aplicación Principal:${NC}"
    echo -e "   ${YELLOW}➜${NC} http://localhost:8080"
    echo ""
    echo -e "${GREEN}🔧 Servicios Individuales:${NC}"
    echo -e "   ${YELLOW}➜${NC} Frontend (React):     http://localhost:5173"
    echo -e "   ${YELLOW}➜${NC} Backend API:          http://localhost:8080/api/"
    echo -e "   ${YELLOW}➜${NC} Admin Django:         http://localhost:8080/admin/"
    echo -e "   ${YELLOW}➜${NC} API Documentation:    http://localhost:8080/api/schema/swagger-ui/"
    echo ""
    echo -e "${GREEN}🗄️  Base de Datos:${NC}"
    echo -e "   ${YELLOW}➜${NC} PostgreSQL:           localhost:5432"
    echo -e "   ${YELLOW}➜${NC} Database: todo_database"
    echo -e "   ${YELLOW}➜${NC} User: postgres"
    echo ""
}

# Función para mostrar comandos útiles
show_commands() {
    echo -e "${BOLD}${BLUE}⚡ COMANDOS ÚTILES:${NC}"
    echo ""
    echo -e "${GREEN}📊 Ver estado:${NC}           ${YELLOW}docker compose ps${NC}"
    echo -e "${GREEN}📋 Ver logs:${NC}             ${YELLOW}docker compose logs -f${NC}"
    echo -e "${GREEN}🛑 Detener:${NC}              ${YELLOW}docker compose down${NC}"
    echo -e "${GREEN}🔄 Reiniciar:${NC}            ${YELLOW}docker compose down -v && docker compose up --build${NC}"
    echo ""
}

# Función para abrir navegador
open_browser() {
    echo -e "${YELLOW}🌐 Abriendo navegador...${NC}"
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:8080
    elif command -v open > /dev/null; then
        open http://localhost:8080
    else
        echo -e "${YELLOW}No se pudo abrir el navegador automáticamente${NC}"
    fi
}

# Función principal
main() {
    show_initial_banner
    
    echo -e "${BLUE}📦 Levantando contenedores...${NC}"
    docker compose up --build -d
    
    echo ""
    echo -e "${YELLOW}⏳ Esperando que los servicios se inicialicen...${NC}"
    sleep 10
    
    show_final_banner
    check_services
    show_links
    show_commands
    
    echo -e "${BOLD}${GREEN}🎉 ¡Abre tu navegador en: ${YELLOW}http://localhost:8080${NC}"
    echo ""
    
    # Preguntar si quiere abrir el navegador
    read -p "$(echo -e ${YELLOW}¿Quieres abrir el navegador automáticamente? [y/N]: ${NC})" -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[YySs]$ ]]; then
        open_browser
    fi
    
    echo ""
    echo -e "${BOLD}${GREEN}✨ ¡Disfruta usando la aplicación!${NC}"
    echo ""
    echo -e "${YELLOW}Para detener la aplicación, ejecuta: ${BOLD}docker compose down${NC}"
    echo ""
}

# Ejecutar función principal
main