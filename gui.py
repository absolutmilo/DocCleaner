import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import datetime
import logging
from pathlib import Path

# Import DocCleaner modules
from doc_cleaner import scanner, duplicates, content_reader, classifier, renamer, organizer, exporter
from doc_cleaner.main import get_file_dates


class TextRedirector:
    """Redirect stdout/stderr to a Text widget."""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, text):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, text, (self.tag,))
        self.widget.see(tk.END)
        self.widget.configure(state='disabled')
        
    def flush(self):
        pass


class DocCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DocCleaner - Organizador Inteligente de Documentos")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.folder_path = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)  # Default to dry run for safety
        self.recursive = tk.BooleanVar(value=True)  # Default to recursive
        self.is_running = False
        self.last_manifest_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="📁 DocCleaner", font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Organiza tus documentos automáticamente", 
                                   font=('Segoe UI', 9), foreground='gray')
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Carpeta a Organizar", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        folder_entry = ttk.Entry(input_frame, textvariable=self.folder_path, state='readonly')
        folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(input_frame, text="Seleccionar...", command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        
        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Opciones", padding="10")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        dry_run_check = ttk.Checkbutton(options_frame, text="🔒 Modo Simulacro (Dry Run) - No mover archivos", 
                                       variable=self.dry_run)
        dry_run_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        recursive_check = ttk.Checkbutton(options_frame, text="📂 Escaneo Recursivo (incluir subcarpetas)", 
                                         variable=self.recursive)
        recursive_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Actions Section
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        
        self.run_btn = ttk.Button(actions_frame, text="▶ Ejecutar Limpieza", 
                                 command=self.run_cleaner, style='Accent.TButton')
        self.run_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.undo_btn = ttk.Button(actions_frame, text="↶ Deshacer Última Ejecución", 
                                   command=self.undo_last_run, state='disabled')
        self.undo_btn.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Progreso y Logs", padding="10")
        output_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(output_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(output_frame, height=20, state='disabled', 
                                                  wrap=tk.WORD, font=('Consolas', 9))
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.log_text.tag_config("stdout", foreground="black")
        self.log_text.tag_config("stderr", foreground="red")
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("error", foreground="red")
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta a organizar")
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"Carpeta seleccionada: {folder}\n", "info")
            
    def log_message(self, message, tag="stdout"):
        """Add message to log text widget."""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message, (tag,))
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        
    def update_status(self, message):
        """Update status bar."""
        self.status_label.config(text=message)
        
    def run_cleaner(self):
        if self.is_running:
            messagebox.showwarning("En Ejecución", "Ya hay una operación en curso.")
            return
            
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Por favor selecciona una carpeta válida.")
            return
            
        # Confirm if not dry run
        if not self.dry_run.get():
            response = messagebox.askyesno(
                "Confirmar Ejecución",
                "¿Estás seguro de que deseas mover archivos?\n\n"
                "Recomendación: Ejecuta primero en Modo Simulacro para verificar."
            )
            if not response:
                return
        
        # Disable buttons
        self.run_btn.config(state='disabled')
        self.undo_btn.config(state='disabled')
        self.is_running = True
        
        # Clear log
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        # Start progress bar
        self.progress.start(10)
        self.update_status("Ejecutando...")
        
        # Run in thread
        thread = threading.Thread(target=self.execute_cleaner, args=(folder,), daemon=True)
        thread.start()
        
    def execute_cleaner(self, root_path):
        """Execute the cleaning process (runs in background thread)."""
        try:
            # Redirect stdout to log widget
            sys.stdout = TextRedirector(self.log_text, "stdout")
            sys.stderr = TextRedirector(self.log_text, "stderr")
            
            dry_run = self.dry_run.get()
            recursive = self.recursive.get()
            
            self.log_message(f"\n{'='*60}\n", "info")
            self.log_message(f"DocCleaner - Inicio de Ejecución\n", "info")
            self.log_message(f"{'='*60}\n", "info")
            self.log_message(f"Carpeta: {root_path}\n")
            self.log_message(f"Modo: {'SIMULACRO (Dry Run)' if dry_run else 'REAL'}\n")
            self.log_message(f"Recursivo: {'Sí' if recursive else 'No'}\n")
            self.log_message(f"{'='*60}\n\n", "info")
            
            # Create output structure
            run_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_root = organizer.create_output_structure(root_path, run_timestamp, dry_run=dry_run)
            print(f"📁 Carpeta de salida: {output_root}\n")
            
            # Setup logging
            if not dry_run:
                log_dir = os.path.join(output_root, "logs")
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, "doccleaner.log")
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                logging.getLogger().addHandler(file_handler)
            
            # Scan
            print(f"🔍 Escaneando archivos... (Recursivo: {recursive})")
            all_files = scanner.scan_folder(root_path, recursive=recursive)
            print(f"✓ Encontrados {len(all_files)} archivos con extensiones permitidas.\n")
            
            # Detect duplicates
            print("🔎 Detectando duplicados...")
            dup_results = duplicates.process_duplicates(all_files, dry_run=dry_run)
            
            # Process files
            final_results = []
            moved_dups = 0
            processed_count = 0
            
            print(f"\n📋 Procesando {len(dup_results)} archivos...\n")
            
            for item in dup_results:
                original_path = item['original_path']
                is_dup = item['is_duplicate']
                
                try:
                    created_iso, modified_iso, ref_date = get_file_dates(original_path)
                except FileNotFoundError:
                    if is_dup and item.get('final_path'):
                        created_iso, modified_iso, ref_date = get_file_dates(item['final_path'])
                    else:
                        created_iso, modified_iso, ref_date = "", "", datetime.datetime.now()
                
                res_entry = {
                    "original_path": original_path,
                    "created_at": created_iso,
                    "modified_at": modified_iso,
                    "is_duplicate": is_dup,
                    "topic": None,
                    "current_path": item.get('final_path', original_path)
                }
                
                if is_dup:
                    moved_dups += 1
                    final_results.append(res_entry)
                    print(f"🔄 Duplicado: {os.path.basename(original_path)}")
                    continue
                
                # Non-duplicate processing
                try:
                    print(f"⚙️  Procesando: {os.path.basename(original_path)}")
                    
                    metadata = content_reader.read_content(original_path)
                    topic = classifier.classify_document(metadata)
                    res_entry['topic'] = topic
                    
                    new_name = renamer.generate_new_name(original_path, topic, ref_date)
                    dest_dir = organizer.determine_destination(output_root, topic, ref_date)
                    final_path = organizer.move_file(original_path, dest_dir, new_name, dry_run=dry_run)
                    
                    res_entry['current_path'] = final_path
                    final_results.append(res_entry)
                    processed_count += 1
                    
                    print(f"   → Tema: {topic}")
                    print(f"   → Nuevo nombre: {new_name}\n")
                    
                except Exception as e:
                    print(f"❌ Error procesando {original_path}: {e}\n")
                    res_entry['error'] = str(e)
                    res_entry['current_path'] = original_path
                    final_results.append(res_entry)
            
            # Export
            if not dry_run:
                exporter.generate_reports(final_results, output_root)
                self.last_manifest_path = os.path.join(output_root, "manifest.json")
                print(f"\n💾 Reportes generados en: {output_root}")
            else:
                print("\n[Modo Simulacro] No se generaron reportes.")
            
            # Summary
            print(f"\n{'='*60}")
            print("✅ Ejecución Completada")
            print(f"{'='*60}")
            print(f"Total archivos escaneados: {len(all_files)}")
            print(f"Duplicados movidos: {moved_dups}")
            print(f"Archivos organizados: {processed_count}")
            print(f"Ubicación de salida: {output_root}")
            print(f"{'='*60}\n")
            
            # Update UI
            self.root.after(0, lambda: self.update_status("✓ Completado"))
            if not dry_run and self.last_manifest_path:
                self.root.after(0, lambda: self.undo_btn.config(state='normal'))
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO: {e}\n")
            self.root.after(0, lambda: self.update_status(f"❌ Error: {str(e)}"))
            
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            
            # Stop progress and re-enable buttons
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.run_btn.config(state='normal'))
            self.is_running = False
            
    def undo_last_run(self):
        if not self.last_manifest_path or not os.path.exists(self.last_manifest_path):
            messagebox.showerror("Error", "No se encontró el archivo manifest.json de la última ejecución.")
            return
            
        response = messagebox.askyesno(
            "Confirmar Deshacer",
            f"¿Deseas restaurar los archivos a sus ubicaciones originales?\n\n"
            f"Manifest: {self.last_manifest_path}"
        )
        
        if not response:
            return
            
        # Run restore script
        try:
            import json
            import shutil
            
            with open(self.last_manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            self.log_message(f"\n{'='*60}\n", "info")
            self.log_message("Restaurando archivos...\n", "info")
            self.log_message(f"{'='*60}\n\n", "info")
            
            restored = 0
            errors = 0
            
            for entry in manifest:
                original = entry.get('original_path')
                current = entry.get('current_path')
                
                if not original or not current or original == current:
                    continue
                
                if not os.path.exists(current):
                    self.log_message(f"⚠️  Archivo no encontrado: {current}\n", "warning")
                    errors += 1
                    continue
                
                if os.path.exists(original):
                    self.log_message(f"⚠️  Ubicación original ocupada: {original}\n", "warning")
                    errors += 1
                    continue
                
                try:
                    os.makedirs(os.path.dirname(original), exist_ok=True)
                    shutil.move(current, original)
                    self.log_message(f"✓ Restaurado: {os.path.basename(original)}\n")
                    restored += 1
                except Exception as e:
                    self.log_message(f"❌ Error: {e}\n", "error")
                    errors += 1
            
            self.log_message(f"\n{'='*60}\n", "info")
            self.log_message(f"Restauración completada: {restored} archivos, {errors} errores\n", "info")
            self.log_message(f"{'='*60}\n\n", "info")
            
            messagebox.showinfo("Completado", f"Restaurados {restored} archivos.\nErrores: {errors}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar: {e}")


def main():
    root = tk.Tk()
    app = DocCleanerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
