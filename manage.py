#!/usr/bin/env python
import os
import sys
import socket

def get_local_ip():
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    return local_ip

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_system.settings')  
    local_ip = get_local_ip()
    port = os.getenv('SERVER_PORT', '8000')  
    addrport = f"{local_ip}:{port}"
    
    if len(sys.argv) == 2 and sys.argv[1] == 'runserver':
        sys.argv.append(addrport)
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
