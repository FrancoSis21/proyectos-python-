import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import time
import json
from datetime import datetime

class Nodo:
    """Nodo del QuadTree - Adaptado del código Python"""
    def __init__(self, info=0, SI=None, SD=None, ID=None, II=None):
        self.Info = info  # 0=negro, 1=blanco, 2=gris (mixto)
        self.SI = SI      # Superior Izquierdo
        self.SD = SD      # Superior Derecho
        self.ID = ID      # Inferior Derecho
        self.II = II      # Inferior Izquierdo

class QuadTree:
    """QuadTree - Adaptado del código C++"""
    def __init__(self):
        self.Raiz = None
        self.A = None  # Matriz de la imagen
        self.N = 0     # Tamaño de la matriz
        
    def Construir(self, matriz):
        """Construye el QuadTree a partir de una matriz binaria"""
        self.A = matriz
        self.N = len(matriz)
        self.Raiz = None
        self.Cons(0, 0, self.N-1, self.N-1, self.Raiz)
        
    def Cons(self, xi, yi, xf, yf, R):
        """Construcción recursiva del QuadTree"""
        # Calcular la suma de colores en la región
        Color = 0
        for i in range(xi, xf+1):
            for j in range(yi, yf+1):
                Color += self.A[i][j]
        
        # Determinar el tipo de nodo
        area = (xf - xi + 1) * (yf - yi + 1)
        
        if Color == 0:  # Todos negros
            nuevo_nodo = Nodo(0)
        elif Color == area:  # Todos blancos
            nuevo_nodo = Nodo(1)
        else:  # Mixto (gris)
            nuevo_nodo = Nodo(2)
            # Dividir recursivamente en 4 cuadrantes
            mid_x = (xi + xf) // 2
            mid_y = (yi + yf) // 2
            
            # Superior Izquierdo
            nuevo_nodo.SI = Nodo()
            self.Cons(xi, yi, mid_x, mid_y, nuevo_nodo.SI)
            
            # Inferior Izquierdo
            nuevo_nodo.II = Nodo()
            self.Cons(mid_x+1, yi, xf, mid_y, nuevo_nodo.II)
            
            # Inferior Derecho
            nuevo_nodo.ID = Nodo()
            self.Cons(mid_x+1, mid_y+1, xf, yf, nuevo_nodo.ID)
            
            # Superior Derecho
            nuevo_nodo.SD = Nodo()
            self.Cons(xi, mid_y+1, mid_x, yf, nuevo_nodo.SD)
        
        if R is None:
            self.Raiz = nuevo_nodo
        else:
            # Copiar los valores al nodo de referencia
            R.Info = nuevo_nodo.Info
            R.SI = nuevo_nodo.SI
            R.SD = nuevo_nodo.SD
            R.ID = nuevo_nodo.ID
            R.II = nuevo_nodo.II
    
    def get_tree_structure(self):
        """Obtiene la estructura del árbol para visualización"""
        structure = []
        self._get_structure_recursive(self.Raiz, 0, 0, self.N, structure)
        return structure
    
    def _get_structure_recursive(self, nodo, x, y, size, structure):
        """Recursión para obtener la estructura del árbol"""
        if nodo is None:
            return
        
        structure.append({
            'x': x,
            'y': y,
            'size': size,
            'info': nodo.Info
        })
        
        if nodo.Info == 2:  # Nodo gris (tiene hijos)
            half_size = size // 2
            # Procesar los 4 cuadrantes
            self._get_structure_recursive(nodo.SI, x, y, half_size, structure)
            self._get_structure_recursive(nodo.II, x + half_size, y, half_size, structure)
            self._get_structure_recursive(nodo.ID, x + half_size, y + half_size, half_size, structure)
            self._get_structure_recursive(nodo.SD, x, y + half_size, half_size, structure)
    
    def render_quadtree(self, width, height):
        """Renderiza el QuadTree como imagen"""
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        structure = self.get_tree_structure()
        scale_x = width / self.N
        scale_y = height / self.N
        
        for region in structure:
            x = int(region['x'] * scale_x)
            y = int(region['y'] * scale_y)
            size_x = int(region['size'] * scale_x)
            size_y = int(region['size'] * scale_y)
            
            # Determinar color según el tipo de nodo
            if region['info'] == 0:  # Negro
                color = (0, 0, 0)
            elif region['info'] == 1:  # Blanco
                color = (255, 255, 255)
            else:  # Gris (no se dibuja, solo sus hijos)
                continue
            
            draw.rectangle([x, y, x + size_x, y + size_y], fill=color)
        
        return img
    
    def render_with_borders(self, width, height, border_color=(255, 0, 0), border_width=2):
        """Renderiza el QuadTree con bordes"""
        img = self.render_quadtree(width, height)
        draw = ImageDraw.Draw(img)
        
        structure = self.get_tree_structure()
        scale_x = width / self.N
        scale_y = height / self.N
        
        for region in structure:
            if region['info'] != 2:  # Solo dibujar bordes en nodos hoja
                x = int(region['x'] * scale_x)
                y = int(region['y'] * scale_y)
                size_x = int(region['size'] * scale_x)
                size_y = int(region['size'] * scale_y)
                
                draw.rectangle(
                    [x, y, x + size_x - 1, y + size_y - 1],
                    outline=border_color,
                    width=border_width
                )
        
        return img
    
    def count_nodes(self, nodo=None):
        """Cuenta el número de nodos en el árbol"""
        if nodo is None:
            nodo = self.Raiz
        
        if nodo is None:
            return 0
        
        if nodo.Info != 2:  # Nodo hoja
            return 1
        
        # Nodo interno, contar recursivamente
        count = 1
        if nodo.SI:
            count += self.count_nodes(nodo.SI)
        if nodo.SD:
            count += self.count_nodes(nodo.SD)
        if nodo.ID:
            count += self.count_nodes(nodo.ID)
        if nodo.II:
            count += self.count_nodes(nodo.II)
        
        return count
    
    def count_leaves(self, nodo=None):
        """Cuenta solo las hojas del árbol"""
        if nodo is None:
            nodo = self.Raiz
        
        if nodo is None:
            return 0
        
        if nodo.Info != 2:  # Nodo hoja
            return 1
        
        # Nodo interno, contar hojas recursivamente
        count = 0
        if nodo.SI:
            count += self.count_leaves(nodo.SI)
        if nodo.SD:
            count += self.count_leaves(nodo.SD)
        if nodo.ID:
            count += self.count_leaves(nodo.ID)
        if nodo.II:
            count += self.count_leaves(nodo.II)
        
        return count
    
    def get_max_depth(self, nodo=None, depth=0):
        """Obtiene la profundidad máxima del árbol"""
        if nodo is None:
            nodo = self.Raiz
        
        if nodo is None or nodo.Info != 2:
            return depth
        
        max_d = depth
        if nodo.SI:
            max_d = max(max_d, self.get_max_depth(nodo.SI, depth + 1))
        if nodo.SD:
            max_d = max(max_d, self.get_max_depth(nodo.SD, depth + 1))
        if nodo.ID:
            max_d = max(max_d, self.get_max_depth(nodo.ID, depth + 1))
        if nodo.II:
            max_d = max(max_d, self.get_max_depth(nodo.II, depth + 1))
        
        return max_d

class QuadTreeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QuadTree de Imágenes - Implementación C++")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.original_image = None
        self.binary_matrix = None
        self.quadtree = QuadTree()
        self.processing_time = 0
        self.border_color = (255, 0, 0)
        self.threshold = 128  # Umbral para binarización
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TLabelframe', background='#2b2b2b', foreground='white')
        style.configure('TLabelframe.Label', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#4a4a4a', foreground='white')
        style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
        
    def setup_ui(self):
        # Barra de menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Cargar Imagen", command=self.load_image)
        file_menu.add_command(label="Guardar QuadTree", command=self.save_quadtree)
        file_menu.add_command(label="Guardar Comparación", command=self.save_comparison)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Estadísticas", command=self.export_stats)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Mostrar Árbol ASCII", command=self.show_tree_ascii)
        tools_menu.add_command(label="Cambiar Color de Bordes", command=self.change_border_color)
        
        # Frame principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Controles
        left_panel = ttk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        self.setup_controls(left_panel)
        
        # Panel derecho - Visualización
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_visualization(right_panel)
        
        # Barra de estado
        self.status_bar = ttk.Label(self.root, text="Listo - Implementación basada en código C++", 
                                    relief=tk.SUNKEN, anchor=tk.W, background='#1e1e1e', 
                                    foreground='white')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_controls(self, parent):
        """Configura el panel de controles"""
        # Cargar imagen
        load_frame = ttk.LabelFrame(parent, text="Imagen", padding="10")
        load_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(load_frame, text="📁 Cargar Imagen", 
                  command=self.load_image, width=25).pack(pady=2)
        
        self.img_info = ttk.Label(load_frame, text="Sin imagen", foreground='gray')
        self.img_info.pack(pady=2)
        
        # Parámetros de binarización
        params_frame = ttk.LabelFrame(parent, text="Binarización", padding="10")
        params_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(params_frame, text="Umbral (0-255):").pack(anchor=tk.W)
        threshold_container = ttk.Frame(params_frame)
        threshold_container.pack(fill=tk.X, pady=2)
        
        self.threshold_var = tk.IntVar(value=128)
        self.threshold_scale = ttk.Scale(threshold_container, from_=0, to=255, 
                                        variable=self.threshold_var, 
                                        orient=tk.HORIZONTAL,
                                        command=self.on_threshold_change)
        self.threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.threshold_label = ttk.Label(threshold_container, text="128", width=6)
        self.threshold_label.pack(side=tk.RIGHT, padx=5)
        
        # Método de binarización
        ttk.Label(params_frame, text="Método:").pack(anchor=tk.W, pady=(10, 0))
        self.binarize_method = tk.StringVar(value='threshold')
        ttk.Radiobutton(params_frame, text="Umbral Simple", 
                       variable=self.binarize_method, value='threshold').pack(anchor=tk.W)
        ttk.Radiobutton(params_frame, text="Otsu", 
                       variable=self.binarize_method, value='otsu').pack(anchor=tk.W)
        ttk.Radiobutton(params_frame, text="Media", 
                       variable=self.binarize_method, value='mean').pack(anchor=tk.W)
        
        ttk.Button(params_frame, text="🔄 Binarizar y Construir", 
                  command=self.process_quadtree, width=25).pack(pady=10)
        
        # Opciones de visualización
        view_frame = ttk.LabelFrame(parent, text="Visualización", padding="10")
        view_frame.pack(fill=tk.X, pady=5)
        
        self.show_borders = tk.BooleanVar(value=True)
        ttk.Checkbutton(view_frame, text="Mostrar Bordes", 
                       variable=self.show_borders,
                       command=self.update_display).pack(anchor=tk.W)
        
        ttk.Label(view_frame, text="Ancho de Borde:").pack(anchor=tk.W, pady=(10, 0))
        border_container = ttk.Frame(view_frame)
        border_container.pack(fill=tk.X, pady=2)
        
        self.border_width_var = tk.IntVar(value=2)
        ttk.Scale(border_container, from_=1, to=5, 
                 variable=self.border_width_var, 
                 orient=tk.HORIZONTAL,
                 command=lambda x: self.update_display()).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.border_label = ttk.Label(border_container, text="2", width=6)
        self.border_label.pack(side=tk.RIGHT, padx=5)
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(parent, text="Estadísticas del QuadTree", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=20, width=35, 
                                 bg='#1e1e1e', fg='white', 
                                 font=('Consolas', 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.update_stats_display()
        
    def setup_visualization(self, parent):
        """Configura el panel de visualización"""
        # Notebook para pestañas
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña: Comparación
        compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(compare_frame, text="Comparación")
        
        images_container = ttk.Frame(compare_frame)
        images_container.pack(fill=tk.BOTH, expand=True)
        
        # Imagen original
        left_panel = ttk.LabelFrame(images_container, text="Imagen Original")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.original_canvas = tk.Canvas(left_panel, bg='#1e1e1e')
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Matriz binaria
        middle_panel = ttk.LabelFrame(images_container, text="Matriz Binaria")
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.binary_canvas = tk.Canvas(middle_panel, bg='#1e1e1e')
        self.binary_canvas.pack(fill=tk.BOTH, expand=True)
        
        # QuadTree
        right_panel = ttk.LabelFrame(images_container, text="QuadTree")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.quadtree_canvas = tk.Canvas(right_panel, bg='#1e1e1e')
        self.quadtree_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña: Matriz
        matrix_frame = ttk.Frame(self.notebook)
        self.notebook.add(matrix_frame, text="Matriz de Datos")
        
        matrix_scroll_frame = ttk.Frame(matrix_frame)
        matrix_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar_y = ttk.Scrollbar(matrix_scroll_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(matrix_scroll_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.matrix_text = tk.Text(matrix_scroll_frame, bg='#1e1e1e', fg='white',
                                   font=('Consolas', 10),
                                   yscrollcommand=scrollbar_y.set,
                                   xscrollcommand=scrollbar_x.set,
                                   wrap=tk.NONE)
        self.matrix_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.matrix_text.yview)
        scrollbar_x.config(command=self.matrix_text.xview)
        
    def load_image(self):
        """Carga una imagen desde el disco"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Todas las imágenes", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp")
            ]
        )
        
        if file_path:
            try:
                self.status_bar.config(text="Cargando imagen...")
                self.root.update()
                
                self.original_image = Image.open(file_path)
                
                # Convertir a escala de grises
                self.original_image = self.original_image.convert('L')
                
                # Redimensionar a potencia de 2 para QuadTree
                size = max(self.original_image.size)
                power_of_2 = 2 ** int(np.ceil(np.log2(size)))
                power_of_2 = min(power_of_2, 512)  # Limitar tamaño máximo
                
                self.original_image = self.original_image.resize(
                    (power_of_2, power_of_2), 
                    Image.Resampling.LANCZOS
                )
                
                w, h = self.original_image.size
                self.img_info.config(text=f"{w}x{h} px")
                
                self.display_original()
                self.process_quadtree()
                
                self.status_bar.config(text=f"Imagen cargada: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
                self.status_bar.config(text="Error al cargar imagen")
    
    def binarize_image(self):
        """Convierte la imagen a matriz binaria"""
        if self.original_image is None:
            return None
        
        img_array = np.array(self.original_image)
        method = self.binarize_method.get()
        
        if method == 'threshold':
            threshold = self.threshold_var.get()
            binary = (img_array > threshold).astype(int)
        elif method == 'otsu':
            # Método de Otsu
            threshold = self.otsu_threshold(img_array)
            self.threshold_var.set(int(threshold))
            self.threshold_label.config(text=str(int(threshold)))
            binary = (img_array > threshold).astype(int)
        elif method == 'mean':
            threshold = np.mean(img_array)
            self.threshold_var.set(int(threshold))
            self.threshold_label.config(text=str(int(threshold)))
            binary = (img_array > threshold).astype(int)
        
        return binary
    
    def otsu_threshold(self, image):
        """Calcula el umbral óptimo usando el método de Otsu"""
        histogram, bin_edges = np.histogram(image, bins=256, range=(0, 256))
        histogram = histogram.astype(float)
        
        # Normalizar histograma
        histogram /= histogram.sum()
        
        # Calcular umbrales
        bins = np.arange(256)
        
        # Pesos acumulados
        weight_bg = np.cumsum(histogram)
        weight_fg = 1 - weight_bg
        
        # Medias acumuladas
        mean_bg = np.cumsum(histogram * bins)
        
        # Evitar división por cero
        with np.errstate(divide='ignore', invalid='ignore'):
            mean_bg = mean_bg / weight_bg
            mean_fg = (np.sum(histogram * bins) - np.cumsum(histogram * bins)) / weight_fg
        
        # Varianza entre clases
        variance_between = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        
        # Encontrar el umbral óptimo
        threshold = np.argmax(variance_between)
        
        return threshold
    
    def display_original(self):
        """Muestra la imagen original"""
        if self.original_image:
            canvas_width = self.original_canvas.winfo_width()
            canvas_height = self.original_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_copy = self.original_image.copy()
                img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
                self.original_photo = ImageTk.PhotoImage(img_copy)
                self.original_canvas.delete("all")
                self.original_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.original_photo
                )
    
    def display_binary(self):
        """Muestra la matriz binaria"""
        if self.binary_matrix is not None:
            # Crear imagen desde la matriz binaria
            binary_img = Image.fromarray((self.binary_matrix * 255).astype(np.uint8), mode='L')
            
            canvas_width = self.binary_canvas.winfo_width()
            canvas_height = self.binary_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_copy = binary_img.copy()
                img_copy.thumbnail((canvas_width, canvas_height), Image.Resampling.NEAREST)
                
                self.binary_photo = ImageTk.PhotoImage(img_copy)
                self.binary_canvas.delete("all")
                self.binary_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.binary_photo
                )
    
    def process_quadtree(self):
        """Procesa la imagen con el QuadTree"""
        if self.original_image is None:
            return
        
        try:
            self.status_bar.config(text="Procesando QuadTree...")
            self.root.update()
            
            start_time = time.time()
            
            # Binarizar imagen
            self.binary_matrix = self.binarize_image()
            self.display_binary()
            
            # Mostrar matriz en la pestaña
            self.display_matrix_data()
            
            # Construir QuadTree
            self.quadtree.Construir(self.binary_matrix.tolist())
            
            self.processing_time = time.time() - start_time
            
            self.update_stats_display()
            self.update_display()
            
            num_leaves = self.quadtree.count_leaves()
            self.status_bar.config(
                text=f"QuadTree generado - Hojas: {num_leaves} - Tiempo: {self.processing_time:.3f}s"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar: {str(e)}")
            self.status_bar.config(text="Error al procesar")
    
    def display_matrix_data(self):
        """Muestra la matriz binaria como texto"""
        self.matrix_text.delete(1.0, tk.END)
        
        if self.binary_matrix is None:
            self.matrix_text.insert(tk.END, "No hay matriz binaria disponible")
            return
        
        N = len(self.binary_matrix)
        self.matrix_text.insert(tk.END, f"Matriz Binaria {N}x{N}\n")
        self.matrix_text.insert(tk.END, "=" * (N * 2 + 10) + "\n\n")
        
        # Mostrar matriz
        for i in range(N):
            for j in range(N):
                self.matrix_text.insert(tk.END, str(self.binary_matrix[i][j]) + " ")
            self.matrix_text.insert(tk.END, "\n")
    
    def update_display(self):
        """Actualiza la visualización del QuadTree"""
        if self.quadtree.Raiz is None:
            return
        
        try:
            size = len(self.binary_matrix)
            
            if self.show_borders.get():
                quad_img = self.quadtree.render_with_borders(
                    size, size, 
                    self.border_color, 
                    self.border_width_var.get()
                )
            else:
                quad_img = self.quadtree.render_quadtree(size, size)
            
            canvas_width = self.quadtree_canvas.winfo_width()
            canvas_height = self.quadtree_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                quad_display = quad_img.copy()
                quad_display.thumbnail((canvas_width, canvas_height), Image.Resampling.NEAREST)
                
                self.quadtree_photo = ImageTk.PhotoImage(quad_display)
                self.quadtree_canvas.delete("all")
                self.quadtree_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.quadtree_photo
                )
            
            # Actualizar label de borde
            self.border_label.config(text=str(self.border_width_var.get()))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar: {str(e)}")
    
    def update_stats_display(self):
        """Actualiza el panel de estadísticas"""
        self.stats_text.delete(1.0, tk.END)
        
        if self.quadtree.Raiz is None:
            self.stats_text.insert(tk.END, "Sin datos\n\nProcesa una imagen para\nver estadísticas.")
            return
        
        num_nodes = self.quadtree.count_nodes()
        num_leaves = self.quadtree.count_leaves()
        max_depth = self.quadtree.get_max_depth()
        
        # Contar tipos de nodos
        structure = self.quadtree.get_tree_structure()
        black_nodes = sum(1 for s in structure if s['info'] == 0)
        white_nodes = sum(1 for s in structure if s['info'] == 1)
        gray_nodes = sum(1 for s in structure if s['info'] == 2)
        
        stats_info = f"""═══════════════════════════════
ESTADÍSTICAS DEL QUADTREE
═══════════════════════════════

Implementación: C++ Adaptado
Estructura: Nodo con 4 hijos
            (SI, SD, ID, II)

NODOS:
  Total: {num_nodes}
  Hojas: {num_leaves}
  Internos: {num_nodes - num_leaves}

TIPOS DE NODO:
  Negro (0): {black_nodes}
  Blanco (1): {white_nodes}
  Gris (2): {gray_nodes}

PROFUNDIDAD:
  Máxima: {max_depth}

MATRIZ:
  Tamaño: {len(self.binary_matrix)}x{len(self.binary_matrix)}
  Umbral: {self.threshold_var.get()}
  Método: {self.binarize_method.get().title()}

RENDIMIENTO:
  Tiempo: {self.processing_time:.3f}s

═══════════════════════════════
"""
        
        self.stats_text.insert(tk.END, stats_info)
    
    def on_threshold_change(self, value):
        """Maneja cambios en el umbral"""
        self.threshold_label.config(text=str(int(float(value))))
    
    def change_border_color(self):
        """Cambia el color de los bordes"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Seleccionar color de borde")
        if color[0]:
            self.border_color = tuple(int(c) for c in color[0])
            if self.quadtree.Raiz:
                self.update_display()
    
    def save_quadtree(self):
        """Guarda la imagen del QuadTree"""
        if self.quadtree.Raiz is None:
            messagebox.showwarning("Advertencia", "No hay QuadTree para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        
        if file_path:
            try:
                size = len(self.binary_matrix)
                
                if self.show_borders.get():
                    img = self.quadtree.render_with_borders(
                        size, size, self.border_color, self.border_width_var.get()
                    )
                else:
                    img = self.quadtree.render_quadtree(size, size)
                
                img.save(file_path)
                messagebox.showinfo("Éxito", f"QuadTree guardado en: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def save_comparison(self):
        """Guarda una imagen comparativa"""
        if self.quadtree.Raiz is None:
            messagebox.showwarning("Advertencia", "No hay QuadTree para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        
        if file_path:
            try:
                size = len(self.binary_matrix)
                
                # Crear imagen comparativa
                comparison = Image.new('RGB', (size * 3 + 40, size + 80), color='white')
                draw = ImageDraw.Draw(comparison)
                
                # Imagen original
                orig_gray = self.original_image.convert('RGB')
                comparison.paste(orig_gray, (10, 60))
                
                # Matriz binaria
                binary_img = Image.fromarray((self.binary_matrix * 255).astype(np.uint8), mode='L')
                binary_rgb = binary_img.convert('RGB')
                comparison.paste(binary_rgb, (size + 20, 60))
                
                # QuadTree
                if self.show_borders.get():
                    quad_img = self.quadtree.render_with_borders(
                        size, size, self.border_color, self.border_width_var.get()
                    )
                else:
                    quad_img = self.quadtree.render_quadtree(size, size)
                
                comparison.paste(quad_img, (size * 2 + 30, 60))
                
                # Añadir texto
                try:
                    font = ImageFont.truetype("arial.ttf", 14)
                    font_title = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                    font_title = ImageFont.load_default()
                
                draw.text((10, 10), "QuadTree - Comparación", fill='black', font=font_title)
                draw.text((10, 40), "Original", fill='black', font=font)
                draw.text((size + 20, 40), f"Binaria (Umbral={self.threshold_var.get()})", 
                         fill='black', font=font)
                draw.text((size * 2 + 30, 40), f"QuadTree ({self.quadtree.count_leaves()} hojas)", 
                         fill='black', font=font)
                
                comparison.save(file_path)
                messagebox.showinfo("Éxito", f"Comparación guardada en: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def export_stats(self):
        """Exporta las estadísticas a un archivo JSON"""
        if self.quadtree.Raiz is None:
            messagebox.showwarning("Advertencia", "No hay estadísticas para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("TXT", "*.txt")]
        )
        
        if file_path:
            try:
                structure = self.quadtree.get_tree_structure()
                black_nodes = sum(1 for s in structure if s['info'] == 0)
                white_nodes = sum(1 for s in structure if s['info'] == 1)
                gray_nodes = sum(1 for s in structure if s['info'] == 2)
                
                data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'implementation': 'C++ Adapted QuadTree',
                    'image_size': f"{len(self.binary_matrix)}x{len(self.binary_matrix)}",
                    'parameters': {
                        'threshold': self.threshold_var.get(),
                        'binarization_method': self.binarize_method.get()
                    },
                    'statistics': {
                        'total_nodes': self.quadtree.count_nodes(),
                        'leaf_nodes': self.quadtree.count_leaves(),
                        'max_depth': self.quadtree.get_max_depth(),
                        'black_nodes': black_nodes,
                        'white_nodes': white_nodes,
                        'gray_nodes': gray_nodes
                    },
                    'processing_time': self.processing_time
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Éxito", f"Estadísticas exportadas a: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
    
    def show_tree_ascii(self):
        """Muestra el árbol en formato ASCII"""
        if self.quadtree.Raiz is None:
            messagebox.showinfo("Árbol", "No hay QuadTree para mostrar")
            return
        
        # Crear ventana para mostrar el árbol
        tree_window = tk.Toplevel(self.root)
        tree_window.title("Estructura del QuadTree (ASCII)")
        tree_window.geometry("800x600")
        tree_window.configure(bg='#2b2b2b')
        
        frame = ttk.Frame(tree_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = ttk.Scrollbar(frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        text = tk.Text(frame, bg='#1e1e1e', fg='white', font=('Consolas', 10),
                      yscrollcommand=scrollbar_y.set,
                      xscrollcommand=scrollbar_x.set,
                      wrap=tk.NONE)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=text.yview)
        scrollbar_x.config(command=text.yview)
        
        # Generar representación ASCII del árbol
        text.insert(tk.END, "═" * 80 + "\n")
        text.insert(tk.END, "ESTRUCTURA DEL QUADTREE\n")
        text.insert(tk.END, "═" * 80 + "\n\n")
        text.insert(tk.END, "Leyenda:\n")
        text.insert(tk.END, "  0 = Negro (todos los píxeles son 0)\n")
        text.insert(tk.END, "  1 = Blanco (todos los píxeles son 1)\n")
        text.insert(tk.END, "  2 = Gris (píxeles mixtos, tiene 4 hijos)\n\n")
        text.insert(tk.END, "Estructura: [SI, SD, ID, II]\n")
        text.insert(tk.END, "  SI = Superior Izquierdo\n")
        text.insert(tk.END, "  SD = Superior Derecho\n")
        text.insert(tk.END, "  ID = Inferior Derecho\n")
        text.insert(tk.END, "  II = Inferior Izquierdo\n\n")
        text.insert(tk.END, "=" * 80 + "\n\n")
        
        self._print_tree_ascii(self.quadtree.Raiz, text, "", True)
        
        text.config(state=tk.DISABLED)
    
    def _print_tree_ascii(self, nodo, text_widget, prefix, is_last):
        """Imprime el árbol en formato ASCII recursivamente"""
        if nodo is None:
            return
        
        # Determinar el símbolo de conexión
        connector = "└── " if is_last else "├── "
        
        # Determinar el tipo de nodo
        node_type = {0: "Negro", 1: "Blanco", 2: "Gris"}
        
        text_widget.insert(tk.END, prefix + connector + f"[{nodo.Info}] {node_type.get(nodo.Info, 'Desconocido')}\n")
        
        # Si es un nodo gris (tiene hijos)
        if nodo.Info == 2:
            # Preparar prefijo para los hijos
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            # Imprimir los 4 hijos
            children = [
                ("SI", nodo.SI),
                ("SD", nodo.SD),
                ("ID", nodo.ID),
                ("II", nodo.II)
            ]
            
            for i, (name, child) in enumerate(children):
                if child is not None:
                    is_last_child = (i == 3)
                    text_widget.insert(tk.END, new_prefix + ("└── " if is_last_child else "├── ") + f"{name}:\n")
                    child_prefix = new_prefix + ("    " if is_last_child else "│   ")
                    self._print_tree_ascii(child, text_widget, child_prefix, True)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuadTreeGUI(root)

    root.mainloop()
