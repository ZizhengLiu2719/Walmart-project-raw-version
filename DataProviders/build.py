#!/usr/bin/env python3
"""
Cross-platform runner:
- Recursively finds Go main packages (main.go), Java projects (Maven/Gradle), and others in the future
- Starts them in background
- Ensures background processes (and their children) are killed when this Python script exits
- Writes stdout/stderr to logs/<projectname>-<timestamp>.(out|err)
Works on Unix-like systems and Windows.
"""
from pathlib import Path
import subprocess
import signal
import atexit
import os
import platform
import datetime

IS_WINDOWS = platform.system().lower().startswith("win")

# List of dicts: { "proc": Popen, "stdout": fileobj, "stderr": fileobj, "cwd": Path }
processes = []


def project_paths(cwd: Path):
    """
    Returns a list of path objects correlating to each Data Provider project.
    Add to this, and create a function to parse and run it to make build.py
    automatically launch it.
    """
    return [
        {
            "path": cwd / "National_Weather_XML",
            "language": "go",
            "port": 8081,
        },
        {
            "path": cwd / "Healthcare_XML",
            "language": "java:maven",
            "port": 8082,
        },
        {
            "path": cwd / "Employees_JSON",
            "language": "python:uvicorn",
            "port": 8001,
        },
        {
            "path": cwd / "Inventory_JSON",
            "language": "python:uvicorn",
            "port": 8002,
        },
        {
            "path": cwd / "Distribution_YAML",
            "language": "python:uvicorn",
            "port": 8003
        },
        {
            "path": cwd / "Warehouse_YAML",
            "language": "python:uvicorn",
            "port": 8004
        },
        {
            "path": cwd / "Transport_CSV",
            "language": "java:spring-boot",
            "port": 8084
        },
        {
            "path": cwd / "Finances_CSV",
            "language": "java:spring-boot",
            "port": 8085
        },
    ]


def _timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def _safe_name(path: Path):
    # produce a short safe name for logs
    return path.name.replace(" ", "_")


def start_background_process(cmd, cwd: Path, port: int = None):
    """
    Start a background process in a new process group (platform-specific),
    and redirect stdout/stderr to log files to avoid blocking.
    """
    cwd = Path(cwd)
    logs_dir = cwd / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    name = _safe_name(cwd) + "-" + _timestamp()
    out_path = logs_dir / f"{name}.out"
    err_path = logs_dir / f"{name}.err"

    # Open files in binary mode and keep handles (don't close them)
    out_f = open(out_path, "wb")
    err_f = open(err_path, "wb")

    creationflags = 0
    preexec_fn = None

    if IS_WINDOWS:
        # Use a new process group on Windows
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        # On Unix, put the child in a new process group
        def preexec_fn(): return os.setpgrp()

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=out_f,
            stderr=err_f,
            creationflags=creationflags,
            preexec_fn=preexec_fn,
            # do NOT use shell=True; commands are passed as lists
        )
    except FileNotFoundError:
        out_f.close()
        err_f.close()
        print(f"[ERROR] Command not found: {cmd[0]}")
        return None
    except Exception as e:
        out_f.close()
        err_f.close()
        print(f"[ERROR] Failed to start {' '.join(cmd)} in {cwd}: {e}")
        return None

    # record optional port so cleanup can find orphaned listeners
    processes.append({"proc": proc, "stdout": out_f,
                     "stderr": err_f, "cwd": cwd, "cmd": cmd, "port": port})
    # print(f"[STARTED] pid={proc.pid} cmd={' '.join(cmd)} cwd={cwd} stdout={out_path} stderr={err_path}")
    return proc


# Opens, Reads, and Prints the README.md file within the called path.
def read_data_provider_info(path: Path):
    info_file = path / "docs/general_info.txt"
    if not info_file.exists():
        print("[ERROR] No Data Provider info file found. \n")
    else:
        info_object = open(info_file, "r")
        info_lines = info_object.readlines()

        print("")  # New line for better formatting
        for info_line in info_lines:
            print(info_line)


def run_go_main_package(path: Path):
    """Run Go main package if main.go exists in this folder."""
    main_file = path / "main.go"
    if main_file.exists():
        read_data_provider_info(path)
        return start_background_process(["go", "run", "."], path)
    elif (path / "cmd/server/main.go").exists():
        read_data_provider_info(path / "cmd/server/")
        return start_background_process(["go", "run", "."], path / "cmd/server/")


def run_java_maven(path: Path, port: int = None):
    pom_file = path / "pom.xml"
    if pom_file.exists():
        subprocess.run([mvn_cmd(), "package"], cwd=path,
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        read_data_provider_info(path)
        return start_background_process(["java", "-jar", "target/patient-soap-1.0.0.jar"], path, port=port)


def run_spring_boot(path: Path, port: int = None):
    pom_file = path / "pom.xml"
    if pom_file.exists():
        read_data_provider_info(path)
        return start_background_process([mvn_cmd(), "spring-boot:run"], path, port=port)

def run_python_uvicorn(path: Path, port: int):
    global port_num
    main_py = path / "main.py"
    if main_py.exists():
        read_data_provider_info(path)
        return start_background_process(["uvicorn", "main:app", "--port", f"{port}"], path)


def mvn_cmd():
    global IS_WINDOWS
    return "mvn.cmd" if IS_WINDOWS else "mvn"


def is_venv_present(root_dir: Path):
    venv_file = root_dir / ".venv"
    if venv_file.exists():
        return True
    else:
        return False


def generate_venv():
    global IS_WINDOWS
    completed_process = subprocess.run(["python", "-m", "venv", ".venv"],
                                       check=True, stdout=subprocess.DEVNULL)
    if completed_process.returncode == 0:
        if IS_WINDOWS:
            subprocess.run([".venv\\Scripts\\activate.bat"],
                           check=True)
        else:
            subprocess.run(["source", ".venv/bin/activate"],
                           check=True, stdout=subprocess.DEVNULL)


def install_libraries():
    subprocess.run(["pip", "install", "fastapi", "uvicorn", "pydantic", "pyYAML"],
                   check=True, stdout=subprocess.DEVNULL)

def launch(path: Path):
    """Launches all of the Data Provider projects"""
    path_list = project_paths(path)
    for path_obj in path_list:
        path_to_root = path_obj.get('path')
        language = path_obj.get('language')
        port = path_obj.get('port')

        match language:
            case "go":
                run_go_main_package(path_to_root)
                continue
            case "java:maven":
                run_java_maven(path_to_root, port)
                continue
            case "java:gradle":
                print("Do nothing")
                continue
            case "java:spring-boot":
                run_spring_boot(path_to_root, port)
                continue
            case "python:uvicorn":
                run_python_uvicorn(path_to_root, port)
                continue
            case _:
                print("No processable language found")
                continue

def cleanup():
    """Kill all started processes and close log files."""
    if not processes:
        return
    print("[CLEANUP] Terminating background processes...")

    # Kill in reverse order (children first)
    for item in reversed(processes):
        proc = item["proc"]
        port = item.get("port")
        try:
            if IS_WINDOWS:
                # First try graceful group signal (requires CREATE_NEW_PROCESS_GROUP at start)
                try:
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                    proc.wait(timeout=3)
                    print(f"[KILL] Sent CTRL_BREAK_EVENT to pid {proc.pid}")
                except Exception:
                    # Fallback: kill whole process tree using taskkill (reliable for Java/Maven forks)
                    try:
                        subprocess.run(
                            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        print(f"[KILL] Used taskkill on pid {proc.pid}")
                    except Exception as e:
                        print(f"[WARN] taskkill failed for pid {proc.pid}: {e}")
            else:
                # Unix: kill process group
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                    print(f"[KILL] Sent SIGTERM to pgid {proc.pid}")
                except ProcessLookupError:
                    pass
                except Exception as e:
                    print(f"[WARN] Error killing pgid {proc.pid}: {e}")

                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                        print(f"[KILL] Sent SIGKILL to pgid {proc.pid}")
                    except Exception:
                        pass

            # If the tracked process exited early but left an orphan (e.g. a child java),
            # attempt to find and kill any process listening on the configured port.
            if port:
                try:
                    if IS_WINDOWS:
                        # find PIDs listening on the port
                        out = subprocess.check_output(["netstat", "-ano"], text=True)
                        for line in out.splitlines():
                            if f":{port} " in line or f":{port}\t" in line:
                                parts = line.split()
                                pid = parts[-1]
                                if pid and pid.isdigit():
                                    subprocess.run(["taskkill", "/PID", pid, "/T", "/F"],
                                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    print(f"[KILL] taskkill pid {pid} listening on port {port}")
                    else:
                        # try lsof (common) to find listening pid
                        try:
                            out = subprocess.check_output(["lsof", "-iTCP:%d" % port, "-sTCP:LISTEN", "-t"], text=True)
                            for pid in out.splitlines():
                                pid = pid.strip()
                                if pid:
                                    subprocess.run(["kill", "-9", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    print(f"[KILL] killed pid {pid} listening on port {port}")
                        except subprocess.CalledProcessError:
                            # lsof not present or no listener; try ss as fallback
                            try:
                                out = subprocess.check_output(["ss", "-ltnp"], text=True)
                                for line in out.splitlines():
                                    if f":{port} " in line:
                                        # pid info like users:(("java",pid=1234,fd=...)
                                        if "pid=" in line:
                                            pid = line.split("pid=")[1].split(",")[0]
                                            subprocess.run(["kill", "-9", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                            print(f"[KILL] killed pid {pid} (ss) listening on port {port}")
                            except Exception:
                                pass
                except Exception as e:
                    print(f"[WARN] while trying to cleanup leftover listener on port {port}: {e}")

        except Exception as e:
            print(f"[ERROR] while terminating pid {getattr(proc,'pid', 'unknown')}: {e}")
        finally:
            # close log files
            try:
                item["stdout"].close()
            except Exception:
                pass
            try:
                item["stderr"].close()
            except Exception:
                pass

    processes.clear()
    print("[CLEANUP] Done.")


atexit.register(cleanup)

if __name__ == "__main__":
    root = Path.cwd().resolve()

    print(f"[INFO] Running on platform: {platform.system()}")
    print(f"[INFO] Launching projects under: {root}")
    try:
        if (is_venv_present(root)):
            install_libraries()
            launch(root)
        else:
            generate_venv()
            install_libraries()
            launch(root)
    except Exception as e:
        print('-------------------------------------------')
        print('An error occurred while running the build script:', e)
        print('Please ensure you have the following dependencies installed:')
        print('- Java v24')
        print('- Maven')
        print('- Python v3.12 or greater')
        print('- Golang v1.25')
        print('- Node v22 or greater')
        print('-------------------------------------------')

    print("[INFO] Background processes started (if any).")
    print("[INFO] Logs are under each project's `logs/` directory.")
    print("[INFO] Press Enter to exit (or Ctrl+C). Exiting will kill launched processes.")
    try:
        input()
    except KeyboardInterrupt:
        pass

    # Exiting triggers atexit cleanup()
