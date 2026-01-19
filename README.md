# DocCleaner - Organizador Inteligente de Documentos

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

Organiza automáticamente tus documentos PDF, Word, Excel y PowerPoint por tema y fecha usando clasificación inteligente.

## 🚀 Características

- **🔍 Clasificación Automática**: Detecta el tema del documento (Formato, Procedimiento, Acta, Proceso)
- **📅 Organización por Fecha**: Agrupa archivos por mes y año
- **🔄 Detección de Duplicados**: Identifica y mueve archivos duplicados
- **🔒 Modo Simulacro**: Prueba sin mover archivos reales
- **↶ Función Deshacer**: Restaura archivos a su ubicación original
- **🌐 Interfaz Web**: GUI moderna y fácil de usar
- **📊 Logs Detallados**: Seguimiento completo de todas las operaciones

## 📦 Instalación

### Requisitos
- Python 3.13 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/absolutmilo/DocCleaner.git
cd DocCleaner
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Interfaz Web (Recomendado)

1. **Iniciar la aplicación**
```bash
python gui_web.py
```

2. **Abrir en el navegador**
   - La aplicación se abrirá automáticamente en `http://127.0.0.1:7860`
   - Si no se abre, copia la URL en tu navegador

3. **Usar la interfaz**
   - Selecciona la carpeta con tus documentos
   - Activa "Modo Simulacro" para la primera prueba
   - Haz clic en "Ejecutar Limpieza"
   - Revisa los logs y resultados
   - Si todo está bien, ejecuta sin simulacro

### Línea de Comandos

```bash
# Modo simulacro (recomendado primero)
python -m doc_cleaner.main "C:\Ruta\A\Carpeta" --dry-run --recursive

# Ejecución real
python -m doc_cleaner.main "C:\Ruta\A\Carpeta" --recursive

# Solo carpeta actual (sin subcarpetas)
python -m doc_cleaner.main "C:\Ruta\A\Carpeta"
```

### Deshacer Cambios

**Desde la GUI Web:**
- Haz clic en "Deshacer Última Ejecución"

**Desde línea de comandos:**
```bash
python scripts/restore.py "C:\Ruta\A\Output\manifest.json"
```

## 📁 Estructura de Salida

```
DocCleaner_Run_2026-01-19_08-00-00/
├── FORMATOS/
│   ├── Ene2026/
│   │   └── 2026-01-15_FORMATO_plantilla-evaluacion.docx
│   └── Dic2025/
├── PROCEDIMIENTOS/
│   └── Ene2026/
│       └── 2026-01-10_PROCEDIMIENTO_manual-usuario.pdf
├── ACTAS/
├── PROCESOS/
├── OTROS/
├── logs/
│   └── doccleaner.log
└── manifest.json
```

## ⚙️ Configuración

Edita `doc_cleaner/config.json` para personalizar:

```json
{
    "topic_keywords": {
        "FORMATO": ["formato", "template", "plantilla", "formulario"],
        "PROCEDIMIENTO": ["procedimiento", "manual", "guia"],
        "ACTA": ["acta", "minutes", "reunion"],
        "PROCESO": ["proceso", "diagrama", "flujo"]
    },
    "topic_folders": {
        "FORMATO": "FORMATOS",
        "PROCEDIMIENTO": "PROCEDIMIENTOS",
        "ACTA": "ACTAS",
        "PROCESO": "PROCESOS",
        "GENERIC": "OTROS"
    }
}
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest tests/

# Ejecutar pruebas específicas
python -m pytest tests/test_classifier.py
```

## 📋 Temas Detectados

| Tema | Palabras Clave | Carpeta de Salida |
|------|----------------|-------------------|
| 📋 FORMATO | formato, template, plantilla, formulario | FORMATOS |
| 📖 PROCEDIMIENTO | procedimiento, manual, guia, instructivo | PROCEDIMIENTOS |
| 📝 ACTA | acta, minutes, reunion, meeting | ACTAS |
| 🔄 PROCESO | proceso, diagrama, flujo | PROCESOS |
| 📄 GENERIC | (otros documentos) | OTROS |

## 🔧 Solución de Problemas

### La GUI no se abre
```bash
# Reinstalar Gradio
pip install --upgrade gradio

# Verificar instalación
python -c "import gradio; print(gradio.__version__)"
```

### Errores de lectura de archivos
- Verifica que los archivos no estén abiertos en otra aplicación
- Asegúrate de tener permisos de lectura/escritura en la carpeta

### Clasificación incorrecta
- Edita `config.json` para agregar palabras clave específicas
- Usa nombres de archivo descriptivos

## 📝 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 👤 Autor

**absolutmilo**
- GitHub: [@absolutmilo](https://github.com/absolutmilo)

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias, por favor abre un [issue](https://github.com/absolutmilo/DocCleaner/issues).
