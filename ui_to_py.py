from PyQt6 import uic
import os
import subprocess

def generate_python_files():
    ui_directory = 'gui'
    py_directory = 'src/ui_pycode'

    ui_files = [f for f in os.listdir(ui_directory) if f.endswith('.ui')]
    
    for ui_file in ui_files:
        py_file = os.path.splitext(ui_file)[0] + '.py'
        py_path = os.path.join(py_directory, py_file)
        ui_path = os.path.join(ui_directory, ui_file)

        try:
            with open(py_path, 'w', encoding="utf-8") as gui:
                uic.compileUi(ui_path, gui)
            print(f"Compiled {ui_file} to {py_file}")

            with open(py_path, 'a', encoding="utf-8") as gui:
                gui.write("\nimport resources\n")
            print(f"Appended import statement to {py_file}")

        except Exception as e:
            print(f"Error compiling {ui_file}: {e}")

    try:
        subprocess.run(['pyside6-rcc', '-o', 'src/resources.py', 'gui/resources.qrc'], check=True)
        print("Compiled resources.qrc to resources.py")
    except Exception as e:
        print(f"Error compiling resources.qrc: {e}")

if __name__ == "__main__":
    generate_python_files()