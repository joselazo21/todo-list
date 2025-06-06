#!/usr/bin/env python3
"""
Script de información de inicio para Todo List Application
Compatible con Windows, Linux y macOS
"""

import os
import sys
import time
import subprocess
import platform
from urllib.request import urlopen
from urllib.error import URLError

# Colores ANSI (funcionan en la mayoría de terminales modernas)
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'
    
    @classmethod
    def disable_on_windows(cls):
        """Deshabilita colores en Windows si no es compatible"""
        if platform.system() == 'Windows':
            # Intenta habilitar colores en Windows 10+
            try:
                import colorama
                colorama.init()
            except ImportError:
                # Si no tiene colorama, deshabilita colores
                cls.GREEN = cls.BLUE = cls.YELLOW = cls.RED = cls.NC = cls.BOLD = ''

Colors.disable_on_windows()

def clear_screen():
    """Limpia la pantalla de manera multiplataforma"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def show_banner():
    """Muestra el banner de la aplicación"""
    print(f"{Colors.GREEN}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║               🚀 TODO LIST APPLICATION 🚀                   ║")
    print("║                                                              ║")
    print("║                   ¡Aplicación Lista!                        ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")

def check_url(url, timeout=5):
    """Verifica si una URL está disponible"""
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except (URLError, Exception):
        return False

def check_services():
    """Verifica el estado de los servicios"""
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 VERIFICANDO SERVICIOS...{Colors.NC}")
    print()
    
    services = [
        ("Frontend Principal", "http://localhost:8080"),
        ("Backend API", "http://localhost:8080/api/"),
        ("Frontend Directo", "http://localhost:5173"),
    ]
    
    for name, url in services:
        if check_url(url):
            print(f"   {Colors.GREEN}✅ {name}: Funcionando{Colors.NC}")
        else:
            print(f"   {Colors.RED}❌ {name}: No disponible{Colors.NC}")
    
    # Verificar base de datos usando docker compose
    try:
        result = subprocess.run(['docker', 'compose', 'ps', 'db'], 
                              capture_output=True, text=True, timeout=10)
        if 'Up' in result.stdout or 'healthy' in result.stdout:
            print(f"   {Colors.GREEN}✅ Base de Datos: Funcionando{Colors.NC}")
        else:
            print(f"   {Colors.RED}❌ Base de Datos: No disponible{Colors.NC}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"   {Colors.YELLOW}⚠️  Base de Datos: No se pudo verificar{Colors.NC}")
    
    print()

def show_links():
    """Muestra los enlaces de acceso"""
    print(f"{Colors.BOLD}{Colors.BLUE}📱 ENLACES DE ACCESO:{Colors.NC}")
    print()
    print(f"{Colors.GREEN}🌐 Aplicación Principal:{Colors.NC}")
    print(f"   {Colors.YELLOW}➜{Colors.NC} http://localhost:8080")
    print()
    print(f"{Colors.GREEN}🔧 Servicios Individuales:{Colors.NC}")
    print(f"   {Colors.YELLOW}➜{Colors.NC} Frontend (React):     http://localhost:5173")
    print(f"   {Colors.YELLOW}➜{Colors.NC} Backend API:          http://localhost:8080/api/")
    print(f"   {Colors.YELLOW}➜{Colors.NC} Admin Django:         http://localhost:8080/admin/")
    print(f"   {Colors.YELLOW}➜{Colors.NC} API Documentation:    http://localhost:8080/api/schema/swagger-ui/")
    print()
    print(f"{Colors.GREEN}🗄️  Base de Datos:{Colors.NC}")
    print(f"   {Colors.YELLOW}➜{Colors.NC} PostgreSQL:           localhost:5432")
    print(f"   {Colors.YELLOW}➜{Colors.NC} Database: todo_database")
    print(f"   {Colors.YELLOW}➜{Colors.NC} User: postgres")
    print()

def show_commands():
    """Muestra comandos útiles"""
    print(f"{Colors.BOLD}{Colors.BLUE}⚡ COMANDOS ÚTILES:{Colors.NC}")
    print()
    print(f"{Colors.GREEN}📊 Ver estado de contenedores:{Colors.NC}")
    print(f"   {Colors.YELLOW}docker compose ps{Colors.NC}")
    print()
    print(f"{Colors.GREEN}📋 Ver logs:{Colors.NC}")
    print(f"   {Colors.YELLOW}docker compose logs -f{Colors.NC}")
    print()
    print(f"{Colors.GREEN}🛑 Detener aplicación:{Colors.NC}")
    print(f"   {Colors.YELLOW}docker compose down{Colors.NC}")
    print()
    print(f"{Colors.GREEN}🔄 Reiniciar desde cero:{Colors.NC}")
    print(f"   {Colors.YELLOW}docker compose down -v && docker compose up --build{Colors.NC}")
    print()

def open_browser():
    """Intenta abrir el navegador automáticamente"""
    try:
        import webbrowser
        print(f"{Colors.YELLOW}🌐 Abriendo navegador...{Colors.NC}")
        webbrowser.open('http://localhost:8080')
        time.sleep(2)
    except Exception:
        pass

def main():
    """Función principal"""
    clear_screen()
    show_banner()
    print()
    
    # Esperar un poco para que los servicios terminen de inicializar
    print(f"{Colors.YELLOW}⏳ Esperando que los servicios terminen de inicializar...{Colors.NC}")
    time.sleep(5)
    
    check_services()
    show_links()
    show_commands()
    
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 ¡La aplicación está lista para usar!{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}💡 Abre tu navegador en: {Colors.YELLOW}http://localhost:8080{Colors.NC}")
    print()
    
    # Preguntar si quiere abrir el navegador automáticamente
    try:
        response = input(f"{Colors.YELLOW}¿Quieres abrir el navegador automáticamente? (y/N): {Colors.NC}")
        if response.lower() in ['y', 'yes', 's', 'si', 'sí']:
            open_browser()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operación cancelada{Colors.NC}")
    
    print(f"{Colors.YELLOW}Presiona Ctrl+C para detener los servicios{Colors.NC}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Script terminado{Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.NC}")
        sys.exit(1)