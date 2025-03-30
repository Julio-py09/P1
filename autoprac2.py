import flet as ft
import xml.etree.ElementTree as ET
from xml.dom import minidom  # Importar minidom para formatear el XML
from itertools import product

def subcadenas(cadena):
    return [cadena[i:j] for i in range(len(cadena)) for j in range(i + 1, len(cadena) + 1)]

def prefijos(cadena):
    return [cadena[:i] for i in range(len(cadena) + 1)]

def sufijos(cadena):
    return [cadena[i:] for i in range(len(cadena) + 1)]

def cerradura_kleene(alfabeto, max_len):
    return ["".join(p) for i in range(max_len + 1) for p in product(alfabeto, repeat=i)]

def cerradura_positiva(alfabeto, max_len):
    return ["".join(p) for i in range(1, max_len + 1) for p in product(alfabeto, repeat=i)]

def main(page: ft.Page):
    page.title = "Simulador de AFD"
    page.vertical_alignment = "start"
    page.horizontal_alignment = "center"
    page.padding = 20
    page.scroll = "adaptive"

    # Variables para almacenar los datos del AFD
    alphabet = []
    states = []
    initial_state = None
    accepting_states = []
    transition_table = {}

    # Controles de la interfaz
    alphabet_input = ft.TextField(label="Alfabeto (separado por comas)", width=300)
    states_input = ft.TextField(label="Estados (separados por comas)", width=300)
    initial_state_dropdown = ft.Dropdown(label="Estado inicial", width=300)
    accepting_states_checkboxes = ft.Column()
    transition_table_display = ft.Column()
    output_text = ft.Text()

    # Botones faltantes que se referencian en el código
    update_alphabet_button = ft.ElevatedButton("Actualizar Alfabeto", width=150)
    update_states_button = ft.ElevatedButton("Actualizar Estados", width=150)
    define_button = ft.ElevatedButton("Definir AFD", width=150)
    import_afd_button = ft.ElevatedButton("Importar AFD (.afd)", width=150)
    import_jff_button = ft.ElevatedButton("Importar JFF (.jff)", width=150)

    # Controles para validación de cadenas
    input_string = ft.TextField(label="Cadena a validar", width=300)
    validate_button = ft.ElevatedButton("Validar Cadena", width=150)
    simulation_output = ft.Column()
    step_by_step_button = ft.ElevatedButton("Simulación Paso a Paso", width=150)

    # Controles para funcionalidades adicionales
    export_afd_button = ft.ElevatedButton("Exportar AFD (.afd)", width=150)
    export_jff_button = ft.ElevatedButton("Exportar JFF (.jff)", width=150)
    
    # UNIFICADO: Sección para todas las operaciones de lenguajes formales
    operations_input = ft.TextField(label="Cadena para operaciones", width=300)
    max_len_input = ft.TextField(label="Longitud máxima para cerraduras", width=300, value="3")
    calculate_operations_button = ft.ElevatedButton("Calcular Todas las Operaciones", width=200)
    operations_output = ft.Column()
    
    # FilePicker para importar y exportar archivos
    file_picker = ft.FilePicker()

    def update_states(e):
        states.clear()
        states.extend([state.strip() for state in states_input.value.split(",")])
        initial_state_dropdown.options = [ft.dropdown.Option(state) for state in states]
        initial_state_dropdown.value = None
        accepting_states_checkboxes.controls.clear()
        for state in states:
            checkbox = ft.Checkbox(label=state, value=False)
            accepting_states_checkboxes.controls.append(checkbox)
        update_transition_table()
        page.update()

    def update_alphabet(e):
        alphabet.clear()
        alphabet.extend([symbol.strip() for symbol in alphabet_input.value.split(",")])
        update_transition_table()
        page.update()

    def update_transition_table():
        transition_table_display.controls.clear()
        if states and alphabet:
            # Crear la fila de encabezado con los símbolos del alfabeto
            header_row = ft.Row([ft.Text("Estado", width=100)])
            for symbol in alphabet:
                header_row.controls.append(ft.Text(symbol, width=100))
            transition_table_display.controls.append(header_row)

            # Crear una fila para cada estado
            for state in states:
                state_row = ft.Row([ft.Text(state, width=100)])
                for symbol in alphabet:
                    # Obtener el estado de destino desde la tabla de transiciones
                    destination_state = transition_table.get((state, symbol), "")
                    cell_input = ft.TextField(width=100, value=destination_state)
                    cell_input.on_change = lambda e, s=state, sym=symbol: update_transition_cell(s, sym, e.control.value)
                    state_row.controls.append(cell_input)
                transition_table_display.controls.append(state_row)
        page.update()

    def update_transition_cell(state, symbol, value):
        if value:
            transition_table[(state, symbol)] = value
        else:
            transition_table.pop((state, symbol), None)

    def define_afd(e):
        initial_state = initial_state_dropdown.value
        accepting_states.clear()
        for checkbox in accepting_states_checkboxes.controls:
            if checkbox.value:
                accepting_states.append(checkbox.label)
        output_text.value = (
            f"Alfabeto: {alphabet}\n"
            f"Estados: {states}\n"
            f"Estado inicial: {initial_state}\n"
            f"Estados de aceptación: {accepting_states}\n"
            f"Tabla de transiciones: {transition_table}"
        )
        page.update()

    def import_afd(e):
        """Abre el diálogo para seleccionar un archivo .afd."""
        file_picker.pick_files(
            allowed_extensions=["afd"],
            dialog_title="Selecciona un archivo .afd",
        )

    def import_jff(e):
        """Abre el diálogo para seleccionar un archivo .jff."""
        file_picker.pick_files(
            allowed_extensions=["jff"],
            dialog_title="Selecciona un archivo .jff",
        )

    def on_file_pick(e: ft.FilePickerResultEvent):
        """Maneja la selección de un archivo .afd o .jff."""
        if e.files:
            file_path = e.files[0].path
            try:
                if file_path.endswith(".afd"):
                    # Importar desde archivo .afd
                    with open(file_path, "r") as file:
                        lines = file.readlines()
                        # Limpiar datos actuales
                        alphabet.clear()
                        states.clear()
                        initial_state_dropdown.value = None
                        accepting_states.clear()
                        transition_table.clear()

                        # Leer el archivo línea por línea
                        for line in lines:
                            line = line.strip()
                            if line.startswith("Alfabeto:"):
                                alphabet.extend(line.split(":")[1].strip().split(","))
                            elif line.startswith("Estados:"):
                                states.extend(line.split(":")[1].strip().split(","))
                            elif line.startswith("Estado inicial:"):
                                initial_state_dropdown.value = line.split(":")[1].strip()
                            elif line.startswith("Estados de aceptación:"):
                                accepting_states.extend(line.split(":")[1].strip().split(","))
                            elif line.startswith("Transición:"):
                                parts = line.split(":")[1].strip().split("->")
                                left = parts[0].strip().split(",")
                                right = parts[1].strip()
                                transition_table[(left[0].strip(), left[1].strip())] = right

                elif file_path.endswith(".jff"):
                    # Importar desde archivo .jff
                    tree = ET.parse(file_path)
                    root = tree.getroot()

                    # Limpiar datos actuales
                    alphabet.clear()
                    states.clear()
                    initial_state_dropdown.value = None
                    accepting_states.clear()
                    transition_table.clear()

                    # Extraer los estados
                    for state in root.findall(".//state"):
                        state_id = state.get("id")
                        state_name = state.get("name") if state.get("name") else state_id
                        # Normalizar el nombre del estado (agregar 'q' si no lo tiene)
                        if not state_name.startswith("q"):
                            state_name = f"q{state_name}"
                        states.append(state_name)

                        # Verificar si es el estado inicial
                        if state.find("initial") is not None:
                            initial_state_dropdown.value = state_name

                        # Verificar si es un estado de aceptación
                        if state.find("final") is not None:
                            accepting_states.append(state_name)

                    # Extraer el alfabeto de las transiciones
                    for transition in root.findall(".//transition"):
                        read_symbol = transition.find("read").text
                        if read_symbol not in alphabet:  # Evitar duplicados
                            alphabet.append(read_symbol)

                    # Extraer las transiciones
                    for transition in root.findall(".//transition"):
                        from_state = transition.find("from").text
                        to_state = transition.find("to").text
                        read_symbol = transition.find("read").text

                        # Normalizar los nombres de los estados en las transiciones
                        if not from_state.startswith("q"):
                            from_state = f"q{from_state}"
                        if not to_state.startswith("q"):
                            to_state = f"q{to_state}"

                        # Agregar la transición a la tabla
                        transition_table[(from_state, read_symbol)] = to_state

                    # Depuración: Imprimir la tabla de transiciones
                    print("Tabla de transiciones extraída:", transition_table)

                # Actualizar la interfaz
                alphabet_input.value = ",".join(alphabet)
                states_input.value = ",".join(states)
                initial_state_dropdown.options = [ft.dropdown.Option(state) for state in states]
                accepting_states_checkboxes.controls.clear()
                for state in states:
                    checkbox = ft.Checkbox(label=state, value=state in accepting_states)
                    accepting_states_checkboxes.controls.append(checkbox)
                update_transition_table()
                page.update()
            except Exception as ex:
                output_text.value = f"Error al importar el archivo: {ex}"
                page.update()

    def validate_string(e):
        """Valida si la cadena es aceptada por el AFD."""
        if not initial_state_dropdown.value:
            output_text.value = "Error: No se ha definido un estado inicial."
            page.update()
            return

        current_state = initial_state_dropdown.value
        input_str = input_string.value
        trace = []  # Para almacenar la traza del recorrido

        for symbol in input_str:
            if symbol not in alphabet:
                output_text.value = f"Error: El símbolo '{symbol}' no está en el alfabeto."
                page.update()
                return

            next_state = transition_table.get((current_state, symbol), None)
            if not next_state:
                output_text.value = f"Error: No hay transición definida para ('{current_state}', '{symbol}')."
                page.update()
                return

            trace.append((current_state, symbol, next_state))
            current_state = next_state

        # Verificar si el estado final es de aceptación
        if current_state in accepting_states:
            output_text.value = f"La cadena '{input_str}' es ACEPTADA."
        else:
            output_text.value = f"La cadena '{input_str}' es RECHAZADA."

        # Mostrar la traza del recorrido
        simulation_output.controls.clear()
        simulation_output.controls.append(ft.Text("Traza del recorrido:"))
        for step in trace:
            simulation_output.controls.append(ft.Text(f"Estado: {step[0]}, Símbolo: {step[1]}, Siguiente Estado: {step[2]}"))
        page.update()

    def step_by_step_simulation(e):
        """Simula el proceso de validación paso a paso."""
        if not initial_state_dropdown.value:
            output_text.value = "Error: No se ha definido un estado inicial."
            page.update()
            return

        current_state = initial_state_dropdown.value
        input_str = input_string.value
        trace = []  # Para almacenar la traza del recorrido

        simulation_output.controls.clear()
        simulation_output.controls.append(ft.Text("Simulación Paso a Paso:"))
        simulation_output.controls.append(ft.Text(f"Estado inicial: {current_state}"))

        for symbol in input_str:
            if symbol not in alphabet:
                output_text.value = f"Error: El símbolo '{symbol}' no está en el alfabeto."
                page.update()
                return

            next_state = transition_table.get((current_state, symbol), None)
            if not next_state:
                output_text.value = f"Error: No hay transición definida para ('{current_state}', '{symbol}')."
                page.update()
                return

            trace.append((current_state, symbol, next_state))
            simulation_output.controls.append(ft.Text(f"Símbolo: {symbol}, Siguiente Estado: {next_state}"))
            current_state = next_state

        # Verificar si el estado final es de aceptación
        if current_state in accepting_states:
            output_text.value = f"La cadena '{input_str}' es ACEPTADA."
        else:
            output_text.value = f"La cadena '{input_str}' es RECHAZADA."

        page.update()

    def export_afd(e):
        """Exporta el AFD a un archivo .afd."""
        if not states or not alphabet or not initial_state_dropdown.value:
            output_text.value = "Error: No se ha definido un AFD completo."
            page.update()
            return

        content = []
        content.append(f"Alfabeto: {', '.join(alphabet)}")
        content.append(f"Estados: {', '.join(states)}")
        content.append(f"Estado inicial: {initial_state_dropdown.value}")
        content.append(f"Estados de aceptación: {', '.join(accepting_states)}")
        for (state, symbol), next_state in transition_table.items():
            content.append(f"Transición: {state},{symbol} -> {next_state}")

        file_picker.save_file(
            allowed_extensions=["afd"],
            dialog_title="Guardar AFD como .afd",
            file_name="afd.afd",
        )
        # Guardar el contenido después de que se seleccione la ubicación del archivo
        if file_picker.result and file_picker.result.path:
            save_file(file_picker.result, "\n".join(content))

    def export_jff(e):
        """Exporta el AFD a un archivo .jff."""
        if not states or not alphabet or not initial_state_dropdown.value:
            output_text.value = "Error: No se ha definido un AFD completo."
            page.update()
            return

        # Crear el elemento raíz del XML
        root = ET.Element("structure")
        root.set("type", "fa")
        automaton = ET.SubElement(root, "automaton")

        # Crear un mapeo de IDs para los estados
        state_ids = {state: str(i) for i, state in enumerate(states)}

        # Agregar estados
        for state in states:
            state_element = ET.SubElement(automaton, "state")
            # Usar IDs numéricos para compatibilidad con JFLAP
            state_element.set("id", state_ids[state])
            state_element.set("name", state)
            
            # Agregar posiciones aleatorias para mejor visualización
            # Estos valores son sólo para visualización en JFLAP
            x_pos = str(100 + 150 * (states.index(state) % 5))
            y_pos = str(100 + 150 * (states.index(state) // 5))
            
            # Agregar coordenadas como elementos hijos
            x_element = ET.SubElement(state_element, "x")
            x_element.text = x_pos
            y_element = ET.SubElement(state_element, "y")
            y_element.text = y_pos
            
            # Marcar estado inicial y estados de aceptación
            if state == initial_state_dropdown.value:
                ET.SubElement(state_element, "initial")
            if state in accepting_states:
                ET.SubElement(state_element, "final")

        # Agregar transiciones usando los IDs numéricos
        for (from_state, symbol), to_state in transition_table.items():
            if from_state in state_ids and to_state in state_ids:
                transition_element = ET.SubElement(automaton, "transition")
                from_element = ET.SubElement(transition_element, "from")
                from_element.text = state_ids[from_state]
                to_element = ET.SubElement(transition_element, "to")
                to_element.text = state_ids[to_state]
                read_element = ET.SubElement(transition_element, "read")
                read_element.text = symbol

        # Convertir el árbol XML a una cadena con formato
        xml_str = ET.tostring(root, encoding="unicode")

        # Agregar indentación y saltos de línea al XML
        dom = minidom.parseString(xml_str)
        pretty_xml_str = dom.toprettyxml(indent="  ")  # Indentación de 2 espacios

        # Guardar el archivo
        file_picker.save_file(
            allowed_extensions=["jff"],
            dialog_title="Guardar AFD como .jff",
            file_name="afd.jff",
        )
        # Guardar el contenido después de que se seleccione la ubicación del archivo
        if hasattr(file_picker, 'result') and file_picker.result and file_picker.result.path:
            save_file(file_picker.result, pretty_xml_str)

    def save_file(e: ft.FilePickerResultEvent, content: str):
        """Guarda el contenido en un archivo."""
        if e.path:
            try:
                with open(e.path, "w", encoding="utf-8") as file:
                    file.write(content)
                output_text.value = f"Archivo guardado correctamente en {e.path}"
            except Exception as ex:
                output_text.value = f"Error al guardar el archivo: {ex}"
            page.update()

    # FUNCIÓN UNIFICADA: Calcular todas las operaciones para una misma cadena
    def calculate_all_operations(e):
        """Calcula todas las operaciones: subcadenas, prefijos, sufijos, y cerraduras."""
        input_str = operations_input.value
        if not input_str:
            output_text.value = "Error: No se ha ingresado una cadena para las operaciones."
            page.update()
            return
        
        try:
            max_length = int(max_len_input.value)
            if max_length < 1:
                output_text.value = "Error: La longitud máxima para cerraduras debe ser al menos 1."
                page.update()
                return
        except ValueError:
            output_text.value = "Error: La longitud máxima debe ser un número entero."
            page.update()
            return
        
        # Calcular todas las operaciones
        all_substrings = subcadenas(input_str)
        all_prefixes = prefijos(input_str)
        all_suffixes = sufijos(input_str)
        
        # Cerraduras solo si el alfabeto está definido
        if alphabet:
            kleene_star_result = cerradura_kleene(alphabet, max_length)
            kleene_plus_result = cerradura_positiva(alphabet, max_length)
        else:
            # Si no hay alfabeto definido, usar los caracteres de la cadena como alfabeto
            temp_alphabet = list(set(input_str))
            kleene_star_result = cerradura_kleene(temp_alphabet, max_length)
            kleene_plus_result = cerradura_positiva(temp_alphabet, max_length)
            output_text.value = f"Nota: Se usó '{', '.join(temp_alphabet)}' como alfabeto para las cerraduras."
        
        # Mostrar resultados
        operations_output.controls.clear()
        
        # Resultados en formato de tabla
        result_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Operación")),
                ft.DataColumn(ft.Text("Resultado"))
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Subcadenas")),
                    ft.DataCell(ft.Text(", ".join(all_substrings)))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Prefijos")),
                    ft.DataCell(ft.Text(", ".join(all_prefixes)))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Sufijos")),
                    ft.DataCell(ft.Text(", ".join(all_suffixes)))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Cerradura de Kleene (Σ*)")),
                    ft.DataCell(ft.Text(", ".join(kleene_star_result)))
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Cerradura Positiva (Σ+)")),
                    ft.DataCell(ft.Text(", ".join(kleene_plus_result)))
                ]),
            ],
        )
        operations_output.controls.append(result_table)
        
        # Botón para exportar todos los resultados a TXT
        export_operations_button = ft.ElevatedButton(
            "Exportar resultados a TXT",
            on_click=lambda _: export_operations_txt(
                input_str, all_substrings, all_prefixes, all_suffixes, 
                kleene_star_result, kleene_plus_result
            ),
        )
        operations_output.controls.append(export_operations_button)
        
        page.update()
    
    # FUNCIÓN: Exportar todas las operaciones
    def export_operations_txt(input_str, substrings, prefixes, suffixes, kleene_star, kleene_plus):
        """Exporta todos los resultados de las operaciones a un archivo de texto."""
        content = [
            f"OPERACIONES PARA LA CADENA: '{input_str}'",
            "",
            f"Subcadenas: {', '.join(substrings)}",
            "",
            f"Prefijos: {', '.join(prefixes)}",
            "",
            f"Sufijos: {', '.join(suffixes)}",
            "",
            f"Cerradura de Kleene (Σ*): {', '.join(kleene_star)}",
            "",
            f"Cerradura Positiva (Σ+): {', '.join(kleene_plus)}"
        ]
        
        file_picker.save_file(
            allowed_extensions=["txt"],
            dialog_title="Guardar operaciones como .txt",
            file_name="operaciones.txt",
        )
        # Guardar el contenido después de que se seleccione la ubicación del archivo
        if file_picker.result and file_picker.result.path:
            save_file(file_picker.result, "\n".join(content))

    def export_all_results(_):
        """Función que exporta todos los resultados en un solo archivo."""
        content = []
        
        # Información del AFD
        content.append("INFORMACIÓN DEL AUTÓMATA FINITO DETERMINISTA")
        content.append(f"Alfabeto: {', '.join(alphabet)}")
        content.append(f"Estados: {', '.join(states)}")
        content.append(f"Estado inicial: {initial_state_dropdown.value}")
        content.append(f"Estados de aceptación: {', '.join(accepting_states)}")
        content.append("Tabla de transiciones:")
        for (state, symbol), next_state in transition_table.items():
            content.append(f"  {state}, {symbol} -> {next_state}")
        
        # Agregar resultados de validación si existe
        if input_string.value:
            content.append("\nVALIDACIÓN DE CADENA")
            content.append(f"Cadena validada: {input_string.value}")
            content.append(output_text.value)
        
        # Agregar resultados de operaciones si existe
        if operations_input.value:
            content.append("\nOPERACIONES DE LENGUAJES FORMALES")
            content.append(f"Cadena de entrada: {operations_input.value}")
            content.append(f"Subcadenas: {', '.join(subcadenas(operations_input.value))}")
            content.append(f"Prefijos: {', '.join(prefijos(operations_input.value))}")
            content.append(f"Sufijos: {', '.join(sufijos(operations_input.value))}")
            
            # Cerraduras
            max_len = int(max_len_input.value) if max_len_input.value.isdigit() else 3
            if alphabet:
                temp_alphabet = alphabet
            else:
                temp_alphabet = list(set(operations_input.value))
            
            content.append(f"Alfabeto para cerraduras: {', '.join(temp_alphabet)}")
            content.append(f"Longitud máxima: {max_len}")
            content.append(f"Cerradura de Kleene: {', '.join(cerradura_kleene(temp_alphabet, max_len))}")
            content.append(f"Cerradura Positiva: {', '.join(cerradura_positiva(temp_alphabet, max_len))}")
        
        # Guardar todos los resultados
        file_picker.save_file(
            allowed_extensions=["txt"],
            dialog_title="Guardar todos los resultados",
            file_name="todos_resultados.txt",
        )
        # Guardar el contenido después de que se seleccione la ubicación del archivo
        if file_picker.result and file_picker.result.path:
            save_file(file_picker.result, "\n".join(content))

    # Añadir botón para exportar todos los resultados
    export_all_button = ft.ElevatedButton(
        "Exportar Todos los Resultados", 
        on_click=export_all_results,
        width=200
    )

    # Configurar el FilePicker
    file_picker.on_result = on_file_pick
    page.overlay.append(file_picker)

    # Asignar funciones a los botones
    update_states_button.on_click = update_states
    update_alphabet_button.on_click = update_alphabet
    define_button.on_click = define_afd
    import_afd_button.on_click = import_afd
    import_jff_button.on_click = import_jff
    validate_button.on_click = validate_string
    step_by_step_button.on_click = step_by_step_simulation
    export_afd_button.on_click = export_afd
    export_jff_button.on_click = export_jff
    calculate_operations_button.on_click = calculate_all_operations

    # Crear un contenedor para cada sección con un borde para mejor organización
    def create_section(title, controls):
        return ft.Container(
            content=ft.Column(
                [ft.Text(title, size=16, weight="bold")] + controls,
                spacing=10
            ),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(bottom=10)
        )

    # Crear pestañas para dividir la interfaz
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            # Tab 1: Simulador de AFD (combina Definición, Validación y Exportación)
            ft.Tab(
                text="Simulador de AFD",
                content=ft.Container(
                    content=ft.Column(
                        [
                            create_section("Definición del AFD", [
                                ft.Row([alphabet_input, update_alphabet_button]),
                                ft.Row([states_input, update_states_button]),
                                ft.Row([initial_state_dropdown]),
                                ft.Text("Estados de Aceptación:"),
                                accepting_states_checkboxes,
                                ft.Text("Función de Transición:"),
                                transition_table_display,
                                ft.Row([define_button, import_afd_button, import_jff_button]),
                            ]),
                            
                            create_section("Validación de Cadenas", [
                                ft.Row([input_string, validate_button, step_by_step_button]),
                                output_text,
                                simulation_output,
                            ]),
                            
                            create_section("Exportación", [
                                ft.Row([export_afd_button, export_jff_button, export_all_button]),
                            ]),
                        ],
                        spacing=5,
                        scroll="adaptive",
                    ),
                    padding=10,
                )
            ),
            
            # Tab 2: Operaciones de Lenguajes Formales
            ft.Tab(
                text="Operaciones de Lenguajes Formales",
                content=ft.Container(
                    content=ft.Column(
                        [
                            create_section("Operaciones de Lenguajes Formales", [
                                ft.Text("Ingrese una cadena para calcular todas las operaciones:"),
                                ft.Row([operations_input], alignment="center"),
                                ft.Row([max_len_input], alignment="center"),
                                ft.Row([calculate_operations_button], alignment="center"),
                                operations_output,
                                ]),
                        ],
                        spacing=5,
                        scroll="adaptive",
                    ),
                    padding=10,
                )
            ),
        ],
        expand=1,
    )

    # Añadir las pestañas a la página
    page.add(tabs)

ft.app(target=main)