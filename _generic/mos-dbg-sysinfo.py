import sys
import os
import platform
import subprocess
import json

def mostrar_info_sistema():
    print("=== Información del Sistema Anfitrión ===")
    print(f"Sistema Operativo: {platform.system()}")
    print(f"Versión del SO: {platform.release()}")
    print(f"Arquitectura: {platform.machine()}")
    print(f"Procesador: {platform.processor()}")
    print(f"Directorio de trabajo actual: {os.getcwd()}")
    print(f"Usuario actual: {os.getlogin()}")
    print("\n")

def localizar_versiones_python():
    print("=== Versiones de Python Localizadas ===")
    python_info_sistema = {
        "version": sys.version.split()[0],
        "executable": sys.executable
    }
    print(f"Versión actual de Python (sistema): {python_info_sistema['version']} (ubicación: {python_info_sistema['executable']})")
    
    posibles_pythons = ['python', 'python3', 'python3.8', 'python3.9', 'python3.10', 'python3.11', 'python3.12']
    for py in posibles_pythons:
        try:
            version = subprocess.check_output([py, '--version'], stderr=subprocess.STDOUT).decode('utf-8').strip()
            print(f"{py}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    print("\n")
    return python_info_sistema

def obtener_info_python(venv_python_exe):
    """Ejecuta un comando para obtener información de Python desde el ejecutable dado."""
    try:
        version = subprocess.check_output([venv_python_exe, '--version'], stderr=subprocess.STDOUT).decode('utf-8').strip()
        info_script = 'import sys; import json; print(json.dumps({"version": sys.version.split()[0], "executable": sys.executable}))'
        info_output = subprocess.check_output([venv_python_exe, '-c', info_script]).decode('utf-8').strip()
        return json.loads(info_output)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None

def comparar_python_info(sistema_info, venv_info):
    print("\n=== Diferencias entre Python del Sistema y del Venv ===")
    if not venv_info:
        print("No se pudo obtener información del Python del venv.")
        return
    print(f"Versión - Sistema: {sistema_info['version']} | Venv: {venv_info['version']}")
    print(f"Ejecutable - Sistema: {sistema_info['executable']} | Venv: {venv_info['executable']}")
    if sistema_info['version'] == venv_info['version']:
        print("La versión de Python es la misma en el sistema y el venv.")
    else:
        print("Las versiones de Python son diferentes.")
    if sistema_info['executable'] == venv_info['executable']:
        print("El ejecutable de Python es el mismo (esto no debería ocurrir en un venv).")
    else:
        print("Los ejecutables de Python son diferentes, como se espera en un venv.")

def analizar_venv():
    print("=== Análisis de Entornos Virtuales (venv) ===")
    en_venv = sys.prefix != sys.base_prefix
    if en_venv:
        print("Se está ejecutando en un entorno virtual (venv).")
        print(f"Directorio base del venv: {sys.prefix}")
        try:
            paquetes = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=freeze']).decode('utf-8')
            print("Paquetes instalados en este venv:")
            print(paquetes if paquetes.strip() else "No hay paquetes instalados.")
        except subprocess.CalledProcessError:
            print("Error al listar paquetes con pip.")
    else:
        print("No se está ejecutando en un entorno virtual (venv).")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nBuscando directorios venv desde: {script_dir}")
    venvs_encontrados = []
    
    for root, dirs, files in os.walk(script_dir):
        if 'bin' in dirs and 'lib' in dirs and 'include' in dirs:
            venvs_encontrados.append(root)
    
    if not venvs_encontrados:
        print("No se encontraron entornos virtuales en el directorio del script ni en sus subdirectorios.")
        return None, None
    
    if len(venvs_encontrados) > 1:
        print(f"Se encontraron múltiples entornos virtuales ({len(venvs_encontrados)}). No se activará ninguno.")
        for venv_path in venvs_encontrados:
            print(f"Entorno virtual encontrado: {venv_path}")
        return None, None
    
    venv_path = venvs_encontrados[0]
    print(f"\n=== Entorno virtual encontrado: {venv_path} ===")
    
    if platform.system() == "Windows":
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
    else:
        python_exe = os.path.join(venv_path, 'bin', 'python')
        activate_script = os.path.join(venv_path, 'bin', 'activate')
    
    if en_venv and sys.prefix == venv_path:
        print("El entorno virtual encontrado ya está activo.")
        venv_info = {"version": sys.version.split()[0], "executable": sys.executable}
    else:
        print("El entorno virtual no está activo. Instrucciones para activarlo:")
        if platform.system() == "Windows":
            print(f"Ejecuta: {activate_script}")
        else:
            print(f"Ejecuta: source {activate_script}")
        
        venv_info = obtener_info_python(python_exe)
        if venv_info:
            print(f"\nInformación de Python en el venv:")
            print(f"Versión: {venv_info['version']}")
            print(f"Ejecutable: {venv_info['executable']}")
            try:
                paquetes = subprocess.check_output([python_exe, '-m', 'pip', 'list', '--format=freeze']).decode('utf-8')
                print("Paquetes instalados en el venv:")
                print(paquetes if paquetes.strip() else "No hay paquetes instalados.")
            except subprocess.CalledProcessError:
                print("Error al listar paquetes con pip.")
        
        site_packages = os.path.join(venv_path, 'lib', 'site-packages')
        if os.path.exists(site_packages):
            print(f"Directorio de site-packages: {site_packages}")
        else:
            try:
                site_cmd = subprocess.check_output([python_exe, '-c', 'import site; print(site.getsitepackages()[0])']).decode('utf-8').strip()
                print(f"Directorio de site-packages: {site_cmd}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("No se pudo determinar el directorio de site-packages.")
    
    print("\n=== Instrucción para desactivar el venv ===")
    print("Para desactivar el entorno virtual, ejecuta en tu terminal:")
    print("deactivate")
    
    return venv_path, venv_info

if __name__ == "__main__":
    python_info_sistema = localizar_versiones_python()
    mostrar_info_sistema()
    venv_path, venv_info = analizar_venv()
    if venv_path and venv_info:
        comparar_python_info(python_info_sistema, venv_info)