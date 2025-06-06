#!/bin/bash

# Colores para el output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Función para mostrar el banner
show_banner() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║               🚀 TODO LIST APPLICATION 🚀                   ║"
    echo "║                                                              ║"
    echo "║                   ¡Aplicación Lista!                        ║"
    echo "║                                                              ║"
    echo "╚═══════════════════════════════���═══���══════════════════════════╝"
    echo -e "${NC}"
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
    echo -e "${GREEN}📊 Ver estado de contenedores:${NC}"
    echo -e "   ${YELLOW}docker compose ps${NC}"
    echo ""
    echo -e "${GREEN}📋 Ver logs:${NC}"
    echo -e "   ${YELLOW}docker compose logs -f${NC}"
    echo ""
    echo -e "${GREEN}🛑 Detener aplicación:${NC}"
    echo -e "   ${YELLOW}docker compose down${NC}"
    echo ""
    echo -e "${GREEN}🔄 Reiniciar desde cero:${NC}"
    echo -e "   ${YELLOW}docker compose down -v && docker compose up --build${NC}"
    echo ""
}

# Función para verificar que los servicios estén funcionando
check_services() {
    echo -e "${BOLD}${BLUE}🔍 VERIFICANDO SERVICIOS...${NC}"
    echo ""
    
    # Verificar frontend
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Frontend: Funcionando${NC}"
    else
        echo -e "   ${RED}❌ Frontend: No disponible${NC}"
    fi
    
    # Verificar backend API
    if curl -s http://localhost:8080/api/ > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Backend API: Funcionando${NC}"
    else
        echo -e "   ${RED}❌ Backend API: No disponible${NC}"
    fi
    
    # Verificar base de datos (usando docker compose ps)
    if docker compose ps db | grep -q "healthy\|Up"; then
        echo -e "   ${GREEN}✅ Base de Datos: Funcionando${NC}"
    else
        echo -e "   ${RED}❌ Base de Datos: No disponible${NC}"
    fi
    
    echo ""
}

# Función principal
main() {
    clear
    show_banner
    echo ""
    check_services
    show_links
    show_commands
    
    echo -e "${BOLD}${GREEN}🎉 ¡La aplicación está lista para usar!${NC}"
    echo -e "${BOLD}${BLUE}💡 Abre tu navegador en: ${YELLOW}http://localhost:8080${NC}"
    echo ""
    echo -e "${YELLOW}Presiona Ctrl+C para detener los servicios${NC}"
    echo ""
}

# Ejecutar función principal
main