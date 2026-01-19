import gradio as gr
import os
import datetime
import json
import shutil
from pathlib import Path

# Import DocCleaner modules
from doc_cleaner import scanner, duplicates, content_reader, classifier, renamer, organizer, exporter
from doc_cleaner.main import get_file_dates


class DocCleanerApp:
    def __init__(self):
        self.last_manifest_path = None
        
    def process_folder(self, folder_path, dry_run, recursive, progress=gr.Progress()):
        """Main processing function."""
        if not folder_path or not os.path.exists(folder_path):
            return "❌ Error: Por favor selecciona una carpeta válida.", ""
        
        try:
            output_log = []
            
            def log(msg):
                output_log.append(msg)
                return "\n".join(output_log)
            
            # Header
            log(f"{'='*60}")
            log(f"📁 DocCleaner - Inicio de Ejecución")
            log(f"{'='*60}")
            log(f"Carpeta: {folder_path}")
            log(f"Modo: {'🔒 SIMULACRO (Dry Run)' if dry_run else '⚡ REAL'}")
            log(f"Recursivo: {'✓ Sí' if recursive else '✗ No'}")
            log(f"{'='*60}\n")
            
            progress(0.1, desc="Creando estructura de salida...")
            
            # Create output structure
            run_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_root = organizer.create_output_structure(folder_path, run_timestamp, dry_run=dry_run)
            log(f"📂 Carpeta de salida: {output_root}\n")
            
            progress(0.2, desc="Escaneando archivos...")
            
            # Scan
            log(f"🔍 Escaneando archivos... (Recursivo: {recursive})")
            all_files = scanner.scan_folder(folder_path, recursive=recursive)
            log(f"✓ Encontrados {len(all_files)} archivos con extensiones permitidas.\n")
            
            if len(all_files) == 0:
                log("⚠️  No se encontraron archivos para procesar.")
                return "\n".join(output_log), ""
            
            progress(0.3, desc="Detectando duplicados...")
            
            # Detect duplicates
            log("🔎 Detectando duplicados...")
            dup_results = duplicates.process_duplicates(all_files, dry_run=dry_run)
            
            # Process files
            final_results = []
            moved_dups = 0
            processed_count = 0
            
            log(f"\n📋 Procesando {len(dup_results)} archivos...\n")
            
            total_files = len(dup_results)
            for idx, item in enumerate(dup_results):
                progress(0.3 + (0.6 * (idx / total_files)), desc=f"Procesando archivo {idx+1}/{total_files}...")
                
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
                    log(f"🔄 Duplicado: {os.path.basename(original_path)}")
                    continue
                
                # Non-duplicate processing
                try:
                    log(f"⚙️  Procesando: {os.path.basename(original_path)}")
                    
                    metadata = content_reader.read_content(original_path)
                    topic = classifier.classify_document(metadata)
                    res_entry['topic'] = topic
                    
                    new_name = renamer.generate_new_name(original_path, topic, ref_date)
                    dest_dir = organizer.determine_destination(output_root, topic, ref_date)
                    final_path = organizer.move_file(original_path, dest_dir, new_name, dry_run=dry_run)
                    
                    res_entry['current_path'] = final_path
                    final_results.append(res_entry)
                    processed_count += 1
                    
                    log(f"   → Tema: {topic}")
                    log(f"   → Nuevo nombre: {new_name}\n")
                    
                except Exception as e:
                    log(f"❌ Error procesando {original_path}: {e}\n")
                    res_entry['error'] = str(e)
                    res_entry['current_path'] = original_path
                    final_results.append(res_entry)
            
            progress(0.9, desc="Generando reportes...")
            
            # Export
            if not dry_run:
                exporter.generate_reports(final_results, output_root)
                self.last_manifest_path = os.path.join(output_root, "manifest.json")
                log(f"\n💾 Reportes generados en: {output_root}")
            else:
                log("\n[Modo Simulacro] No se generaron reportes.")
            
            progress(1.0, desc="Completado!")
            
            # Summary
            log(f"\n{'='*60}")
            log("✅ Ejecución Completada")
            log(f"{'='*60}")
            log(f"Total archivos escaneados: {len(all_files)}")
            log(f"Duplicados movidos: {moved_dups}")
            log(f"Archivos organizados: {processed_count}")
            log(f"Ubicación de salida: {output_root}")
            log(f"{'='*60}\n")
            
            # Return manifest path for undo button
            manifest_info = self.last_manifest_path if not dry_run else ""
            
            return "\n".join(output_log), manifest_info
            
        except Exception as e:
            return f"❌ ERROR CRÍTICO: {e}", ""
    
    def undo_execution(self, manifest_path):
        """Restore files from manifest."""
        if not manifest_path or not os.path.exists(manifest_path):
            return "❌ Error: No se encontró el archivo manifest.json"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            output_log = []
            
            def log(msg):
                output_log.append(msg)
            
            log(f"{'='*60}")
            log("↶ Restaurando archivos...")
            log(f"{'='*60}\n")
            
            restored = 0
            errors = 0
            
            for entry in manifest:
                original = entry.get('original_path')
                current = entry.get('current_path')
                
                if not original or not current or original == current:
                    continue
                
                if not os.path.exists(current):
                    log(f"⚠️  Archivo no encontrado: {current}")
                    errors += 1
                    continue
                
                if os.path.exists(original):
                    log(f"⚠️  Ubicación original ocupada: {original}")
                    errors += 1
                    continue
                
                try:
                    os.makedirs(os.path.dirname(original), exist_ok=True)
                    shutil.move(current, original)
                    log(f"✓ Restaurado: {os.path.basename(original)}")
                    restored += 1
                except Exception as e:
                    log(f"❌ Error: {e}")
                    errors += 1
            
            log(f"\n{'='*60}")
            log(f"Restauración completada: {restored} archivos, {errors} errores")
            log(f"{'='*60}\n")
            
            return "\n".join(output_log)
            
        except Exception as e:
            return f"❌ Error al restaurar: {e}"


def create_interface():
    """Create Gradio interface."""
    app = DocCleanerApp()
    
    with gr.Blocks(title="DocCleaner", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 📁 DocCleaner
        ### Organizador Inteligente de Documentos
        
        Organiza automáticamente tus documentos PDF, Word, Excel y PowerPoint por tema y fecha.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                folder_input = gr.Textbox(
                    label="📂 Carpeta a Organizar",
                    placeholder="Escribe la ruta completa de la carpeta (ej: C:\\Mis Documentos)",
                    interactive=True,
                    info="Ingresa la ruta completa de la carpeta que deseas organizar"
                )
                
                with gr.Row():
                    example_btn = gr.Button("💡 Ejemplo de Ruta", size="sm")
                
                with gr.Row():
                    dry_run_check = gr.Checkbox(
                        label="🔒 Modo Simulacro (Dry Run) - No mover archivos",
                        value=True,
                        info="Recomendado para la primera ejecución"
                    )
                    recursive_check = gr.Checkbox(
                        label="📂 Escaneo Recursivo",
                        value=True,
                        info="Incluir subcarpetas"
                    )
                
                with gr.Row():
                    run_btn = gr.Button("▶ Ejecutar Limpieza", variant="primary", size="lg")
                    undo_btn = gr.Button("↶ Deshacer Última Ejecución", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("""
                ### ℹ️ Instrucciones
                
                1. **Selecciona** la carpeta con tus documentos
                2. **Activa** Modo Simulacro para probar
                3. **Ejecuta** la limpieza
                4. **Revisa** los logs y resultados
                5. Si todo está bien, ejecuta sin simulacro
                
                ### 🎯 Temas Detectados
                - 📋 **FORMATO**: Plantillas y formularios
                - 📖 **PROCEDIMIENTO**: Manuales y guías
                - 📝 **ACTA**: Actas de reunión
                - 🔄 **PROCESO**: Diagramas de flujo
                - 📄 **OTROS**: Documentos genéricos
                """)
        
        gr.Markdown("---")
        
        output_log = gr.Textbox(
            label="📊 Progreso y Logs",
            lines=20,
            max_lines=30,
            interactive=False
        )
        
        manifest_state = gr.State("")
        
        # Event handlers
        def show_example():
            import platform
            if platform.system() == "Windows":
                return "C:\\Users\\TuUsuario\\Documents\\MisCarpetas"
            else:
                return "/home/usuario/documentos"
        
        example_btn.click(
            fn=show_example,
            outputs=folder_input
        )
        
        run_btn.click(
            fn=app.process_folder,
            inputs=[folder_input, dry_run_check, recursive_check],
            outputs=[output_log, manifest_state]
        )
        
        undo_btn.click(
            fn=app.undo_execution,
            inputs=[manifest_state],
            outputs=[output_log]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )
