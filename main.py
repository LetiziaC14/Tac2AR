# coding: utf-8
# main.py
import os
import sys
import subprocess
import config
import utils
import traceback
import platform

print("DEBUG: main.py avviato (prima del logging).")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, 'pipeline.log')

    # Save console handles BEFORE redirection
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    print(f"L'output completo verra salvato in: {log_file_path}")

    # --- Utilities:

    # Convert Windows path → WSL bash path
    def windows_to_bash_path(path):
        """Convert 'C:\\path\\file.sh' → '/mnt/c/path/file.sh'."""
        if ":" not in path:
            return path  # not a Windows path, return unchanged
        path = path.replace("\\", "/")
        drive = path[0].lower()
        return f"/mnt/{drive}{path[2:]}"
    

    # ASK USER IF KIDNEY PIPELINE SHOULD RUN
    print("\nVuoi eseguire la pipeline di segmentazione renale (run_all.sh)? [y/N]")
    user_choice = input().strip().lower()

    if user_choice in ("y", "yes", "s", "si"):
        
        system = platform.system()


        # --- CASE 1: Windows host → script must be on Windows filesystem
        if system == "Windows":
            win_path = config.KIDNEY_SEGMENTATION_PIPELINE_DIR
            if not os.path.exists(win_path):
                print(f"ERRORE: run_all.sh non trovato in '{win_path}'.")
                sys.exit(1)

            bash_path = windows_to_bash_path(win_path)

        # --- CASE 2: Linux or macOS → expect POSIX path
        else:
            posix_path = config.KIDNEY_SEGMENTATION_PIPELINE_DIR
            if not os.path.exists(posix_path):
                print(f"ERRORE: run_all.sh non trovato in '{posix_path}'.")
                sys.exit(1)

            bash_path = posix_path   # no conversion required
            
        print(f"Eseguo run_all.sh tramite bash: {bash_path}")

        # Path for separate kidney pipeline log
        runall_log_path = os.path.join(script_dir, "run_kidney.log")

        try:
            # Run in binary mode to avoid UnicodeDecodeError
            result = subprocess.run(
                ["bash", bash_path],
                capture_output=True,
                text=False
            )

            stdout = result.stdout.decode(errors="replace")
            stderr = result.stderr.decode(errors="replace")

            # Save raw output to run_kidney.log
            with open(runall_log_path, "w", encoding="utf-8") as f:
                f.write("=== STDOUT ===\n")
                f.write(stdout)
                f.write("\n\n=== STDERR ===\n")
                f.write(stderr)

            print(f"\nOutput run_all.sh salvato in: {runall_log_path}")
            print("Pipeline di segmentazione renale completata. Esco da main.py.")
            sys.exit(0)

        except subprocess.CalledProcessError as e:
            stdout = e.stdout.decode(errors="replace")
            stderr = e.stderr.decode(errors="replace")

            with open(runall_log_path, "w", encoding="utf-8") as f:
                f.write("=== STDOUT (error case) ===\n")
                f.write(stdout)
                f.write("\n\n=== STDERR (error case) ===\n")
                f.write(stderr)

            print(f"ERRORE durante run_all.sh. Vedi {runall_log_path}")
            sys.exit(1)

    else:
        print("Pipeline di segmentazione renale saltata.")

    # NOW START TAC2AR FULL PIPELINE

    try:
        # Redirect ALL output to pipeline.log
        with open(log_file_path, 'w', encoding=config.FILE_ENCODING) as log_file:
            sys.stdout = log_file
            sys.stderr = log_file

            print(f"DEBUG: Logging reindirizzato al file {log_file_path}")
            print("\n--- Avvio Pipeline ---\n")

            # --- FASE 1: Segmentazione ---
            print("--- FASE 1: Avvio Pipeline di Segmentazione ---")

            segmentation_script_path = os.path.join(script_dir, "segmentator_pipeline.py")
            python_executable = os.path.join(sys.prefix, 'Scripts', 'python.exe')

            if not os.path.exists(python_executable):
                print(f"Errore: Eseguibile Python non trovato in '{python_executable}'.")
                sys.exit(1)

            try:
                print(f"DEBUG: Esecuzione di {python_executable} {segmentation_script_path}")

                result = subprocess.run(
                    [python_executable, segmentation_script_path],
                    check=True,
                    text=True,
                    capture_output=True,
                    encoding=config.FILE_ENCODING
                )

                print("Pipeline di segmentazione completata con successo.\n")
                print("--- SEGMENTATION STDOUT (catturato) ---")
                print(result.stdout)
                if result.stderr:
                    print("--- SEGMENTATION STDERR (catturato) ---")
                    print(result.stderr)

            except subprocess.CalledProcessError as e:
                print(f"ERRORE CRITICO durante la pipeline di segmentazione. Codice: {e.returncode}")
                print(e.stdout)
                print(e.stderr)
                sys.exit(1)

            except Exception as e:
                print(f"ERRORE INATTESO durante la segmentazione: {e}")
                traceback.print_exc()
                sys.exit(1)

            # --- FASE 2: Preparazione Blender ---
            print("\n--- PREPARAZIONE PER BLENDER: Conversione registro shader ---")
            try:
                utils.yaml_to_json(config.BLENDER_SHADER_REGISTRY_FILE, config.BLENDER_SHADER_REGISTRY_TMP)
            except Exception as e:
                print(f"ERRORE CRITICO durante conversione registro shader: {e}")
                sys.exit(1)

            # --- FASE 2: Blender Pipeline ---
            print("\n--- FASE 2: Avvio Pipeline di Blender ---")
            blender_pipeline_script_path = os.path.join(script_dir, "blender_pipeline.py")
            blender_executable = config.BLENDER_EXECUTABLE

            if not os.path.exists(blender_pipeline_script_path):
                print(f"ERRORE: Script Blender non trovato in '{blender_pipeline_script_path}'.")
                sys.exit(1)

            if not os.path.exists(blender_executable):
                print(f"Errore: Eseguibile Blender non trovato in '{blender_executable}'.")
                sys.exit(1)

            command = [
                blender_executable,
                "--factory-startup",
                "--background",
                "--python", blender_pipeline_script_path
            ]

            try:
                print(f"DEBUG: Esecuzione di: {' '.join(command)}")

                result = subprocess.run(
                    command,
                    check=True,
                    text=True,
                    capture_output=True,
                    encoding=config.FILE_ENCODING
                )

                print("--- BLENDER STDOUT ---")
                print(result.stdout)

                if result.stderr:
                    print("\n--- BLENDER STDERR ---")
                    print(result.stderr)

                print("\n--- Pipeline Blender COMPLETATA ---")

            except subprocess.CalledProcessError as e:
                print(f"ERRORE CRITICO durante la pipeline Blender. Codice: {e.returncode}")
                print(e.stdout)
                print(e.stderr)
                sys.exit(1)

            print("\n--- Pipeline TAC 2 AR Terminata con Successo ---")

    except Exception as main_e:
        print(f"ERRORE FATALE in main.py: {main_e}", file=original_stderr)
        traceback.print_exc(file=original_stderr)
        sys.exit(1)

    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        try:
            print("Pulizia del file di log")
            utils.clean_log_file(log_file_path)
        except Exception as e:
            print(f"Errore durante la pulizia del log: {e}")

        print("Esecuzione terminata. Controlla pipeline.log per i dettagli.")
