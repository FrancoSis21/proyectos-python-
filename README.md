QuadTree de Imágenes (Interfaz Gráfica con Tkinter)
README — Instrucciones de Uso y Requisitos

Esta aplicación permite visualizar y analizar imágenes mediante una estructura de datos QuadTree, implementada en Python con interfaz gráfica. 
El sistema carga una imagen, la convierte a escala de grises y genera su representación binaria, que se usa para construir el QuadTree.

Requisitos

Lenguaje: Python 3.9 o superior
Librerías necesarias:
    pip install pillow numpy
(Tkinter viene incluido en la mayoría de las distribuciones de Python)

Ejecución

1. Guarda el código en un archivo, por ejemplo: quadtree_gui.py
2. Ejecuta el programa con:
    python quadtree_gui.py

Funcionalidades principales

- Cargar Imagen
- Binarización (umbral manual, Otsu, media)
- Construcción del QuadTree
- Visualización (original, binaria, árbol)
- Estadísticas (nodos, profundidad, tiempo)
- Exportaciones (imagen, comparación, JSON)


Controles básicos

- Archivo → Cargar Imagen
- Archivo → Guardar QuadTree
- Archivo → Exportar Estadísticas
- Herramientas → Mostrar Árbol ASCII
- Umbral: 0–255
- Mostrar Bordes: on/off

Ejemplo de uso:

1. Carga una imagen.
2. Ajusta el umbral o elige “Otsu”.
3. Presiona “Binarizar y Construir”.
4. Observa las estadísticas.
5. Exporta resultados desde el menú “Archivo”.
