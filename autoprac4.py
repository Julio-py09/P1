import flet as ft
import xml.etree.ElementTree as ET
import os
user_dir = os.path.expanduser("~")  # Directorio del usuario
documents_dir = os.path.join(user_dir, "Documents")
import json
from typing import List, Dict, Set, Tuple, Optional
import itertools

class AFD:
    def __init__(self):
        self.alphabet: Set[str] = set()
        self.states: Set[str] = set()
        self.initial_state: str = ""
        self.acceptance_states: Set[str] = set()
        self.transitions: Dict[str, Dict[str, str]] = {}
        
    def add_state(self, state: str):
        self.states.add(state)
        if state not in self.transitions:
            self.transitions[state] = {}
            
    def set_initial_state(self, state: str):
        if state in self.states:
            self.initial_state = state
            
    def add_acceptance_state(self, state: str):
        if state in self.states:
            self.acceptance_states.add(state)
            
    def remove_acceptance_state(self, state: str):
        if state in self.acceptance_states:
            self.acceptance_states.remove(state)
            
    def add_symbol(self, symbol: str):
        self.alphabet.add(symbol)
        
    def add_transition(self, from_state: str, symbol: str, to_state: str):
        if from_state in self.states and to_state in self.states and symbol in self.alphabet:
            if from_state not in self.transitions:
                self.transitions[from_state] = {}
            self.transitions[from_state][symbol] = to_state
            
    def validate_string(self, input_string: str) -> Tuple[bool, List[Tuple[str, str, str]]]:
        if not self.initial_state or not self.states:
            return False, []
            
        current_state = self.initial_state
        trace = []
        
        for char in input_string:
            if char not in self.alphabet:
                return False, trace
                
            if current_state not in self.transitions or char not in self.transitions[current_state]:
                return False, trace
                
            next_state = self.transitions[current_state][char]
            trace.append((current_state, char, next_state))
            current_state = next_state
            
        return current_state in self.acceptance_states, trace
        
    def to_afd_format(self) -> Dict:
        return {
            "alphabet": list(self.alphabet),
            "states": list(self.states),
            "initialState": self.initial_state,
            "acceptanceStates": list(self.acceptance_states),
            "transitions": self.transitions
        }
        
    def to_jff_format(self) -> str:
        """
        Convert the AFD to JFLAP .jff format
        """
        # Create the root element
        root = ET.Element("structure")
        
        # Add type
        ET.SubElement(root, "type").text = "fa"
        
        # Create automaton element
        automaton = ET.SubElement(root, "automaton")
        
        # Add states
        state_id_map = {}  # Map state names to IDs
        for i, state_name in enumerate(self.states):
            state = ET.SubElement(automaton, "state", id=str(i), name=state_name)
            state_id_map[state_name] = str(i)
            
            # Set coordinates (simple layout)
            x = (i % 5) * 100 + 50
            y = (i // 5) * 100 + 50
            ET.SubElement(state, "x").text = str(x)
            ET.SubElement(state, "y").text = str(y)
            
            # Mark initial state
            if state_name == self.initial_state:
                ET.SubElement(state, "initial")
                
            # Mark acceptance states
            if state_name in self.acceptance_states:
                ET.SubElement(state, "final")
                
        # Add transitions
        for from_state, transitions in self.transitions.items():
            for symbol, to_state in transitions.items():
                transition = ET.SubElement(automaton, "transition")
                ET.SubElement(transition, "from").text = state_id_map[from_state]
                ET.SubElement(transition, "to").text = state_id_map[to_state]
                ET.SubElement(transition, "read").text = symbol
                
        # Convert to string
        return ET.tostring(root, encoding='unicode')
        
    @classmethod
    def from_afd_format(cls, data: Dict) -> 'AFD':
        afd = cls()
        
        for symbol in data.get("alphabet", []):
            afd.add_symbol(symbol)
            
        for state in data.get("states", []):
            afd.add_state(state)
            
        afd.set_initial_state(data.get("initialState", ""))
        
        for state in data.get("acceptanceStates", []):
            afd.add_acceptance_state(state)
            
        for from_state, transitions in data.get("transitions", {}).items():
            for symbol, to_state in transitions.items():
                afd.add_transition(from_state, symbol, to_state)
                
        return afd
        
    @classmethod
    def from_jff_format(cls, jff_content: str) -> 'AFD':
        afd = cls()
        root = ET.fromstring(jff_content)
        
        # Map JFLAP state IDs to state names
        state_map = {}
        
        # Extract states
        for state_elem in root.findall(".//state"):
            state_id = state_elem.get("id")
            state_name = state_elem.get("name", state_id)
            state_map[state_id] = state_name
            
            afd.add_state(state_name)
            
            # Check if this is an initial state
            if state_elem.find("initial") is not None:
                afd.set_initial_state(state_name)
                
            # Check if this is an acceptance state
            if state_elem.find("final") is not None:
                afd.add_acceptance_state(state_name)
                
        # Extract transitions
        for transition_elem in root.findall(".//transition"):
            from_id = transition_elem.find("from").text
            to_id = transition_elem.find("to").text
            symbol = transition_elem.find("read").text
            
            if symbol not in afd.alphabet:
                afd.add_symbol(symbol)
                
            afd.add_transition(state_map[from_id], symbol, state_map[to_id])
            
        return afd

    def get_prefixes(self, input_string: str) -> List[str]:
        prefixes = []
        for i in range(len(input_string) + 1):
            prefixes.append(input_string[:i])
        return prefixes
        
    def get_suffixes(self, input_string: str) -> List[str]:
        suffixes = []
        for i in range(len(input_string) + 1):
            suffixes.append(input_string[i:])
        return suffixes
        
    def get_substrings(self, input_string: str) -> List[str]:
        substrings = []
        for i in range(len(input_string)):
            for j in range(i + 1, len(input_string) + 1):
                substrings.append(input_string[i:j])
        return substrings
        
    def get_kleene_closure(self, max_length: int) -> List[str]:
        if not self.alphabet:
            return [""]
            
        result = [""]  # Empty string is always in Kleene closure
        
        for length in range(1, max_length + 1):
            for combination in itertools.product(self.alphabet, repeat=length):
                result.append("".join(combination))
                
        return result
        
    def get_positive_closure(self, max_length: int) -> List[str]:
        if not self.alphabet:
            return []
            
        result = []
        
        for length in range(1, max_length + 1):
            for combination in itertools.product(self.alphabet, repeat=length):
                result.append("".join(combination))
                
        return result

def main(page: ft.Page):
    file_picker = ft.FilePicker(
    on_result=lambda e: handle_file_picker_result(e)
)
       
    def debug_load_automaton(e):
        """Versión de depuración para cargar el autómata."""
        global afd
        file_name = file_name_input.value
        
        # Validación básica
        if not file_name:
            show_debug_message("Error: Nombre de archivo vacío")
            return
        
        try:
            # Obtener el directorio actual
            current_dir = os.getcwd()
            show_debug_message(f"Directorio actual: {current_dir}")
            
            # Construir ruta completa
            if os.path.isabs(file_name):
                full_path = file_name
            else:
                full_path = os.path.join(current_dir, file_name)
            
            show_debug_message(f"Intentando cargar desde: {full_path}")
            
            # Comprobar que el archivo existe
            if not os.path.exists(full_path):
                show_debug_message(f"Error: El archivo no existe en {full_path}")
                return
            
            # Cargar el archivo
            if full_path.endswith('.jff'):
                with open(full_path, 'r', encoding='utf-8') as f:
                    jff_content = f.read()
                show_debug_message("Archivo JFF leído correctamente")
                afd = AFD.from_jff_format(jff_content)
            else:  # .json o .afd
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                show_debug_message("Archivo JSON/AFD leído correctamente")
                afd = AFD.from_afd_format(data)
            
            # Actualizar UI
            alphabet_input.value = ",".join(sorted(afd.alphabet))
            states_input.value = ",".join(sorted(afd.states))
            update_states(None)
            
            # Actualizar estado inicial
            initial_state_dropdown.value = afd.initial_state
            
            # Actualizar estados de aceptación
            for checkbox in acceptance_states_checkboxes.controls:
                if hasattr(checkbox, "label"):
                    checkbox.value = checkbox.label in afd.acceptance_states
            
            update_transition_table()
            
            show_debug_message(f"¡Archivo cargado exitosamente desde {full_path}!")
            
        except Exception as e:
            show_debug_message(f"Error al cargar: {str(e)}")
            import traceback
            show_debug_message(traceback.format_exc())

    def show_debug_message(message):
        """Muestra un mensaje de depuración en la UI y en la consola."""
        print(message)  # Muestra en la consola para depuración
        
        # Crear un diálogo de alerta
        alert_dialog = ft.AlertDialog(
            title=ft.Text("Información de depuración"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(e, alert_dialog))
            ]
        )
        
        page.dialog = alert_dialog
        alert_dialog.open = True
        page.update()

    def close_dialog(e, dialog):
        dialog.open = False
        page.update()
    def debug_save_automaton(e):
        """Versión de depuración para guardar el autómata."""
        file_name = file_name_input.value
        
        # Validación básica
        if not file_name:
            show_debug_message("Error: Nombre de archivo vacío")
            return
        
        # Usar un directorio conocido para garantizar permisos
        try:
            # Obtener el directorio actual
            current_dir = os.getcwd()
            show_debug_message(f"Directorio actual: {current_dir}")
            
            # Construir ruta completa
            if os.path.isabs(file_name):
                full_path = file_name
            else:
                full_path = os.path.join(current_dir, file_name)
            
            show_debug_message(f"Intentando guardar en: {full_path}")
            
            # Asegurar que la extensión sea correcta
            if not any(full_path.endswith(ext) for ext in ['.json', '.jff', '.afd']):
                full_path += '.json'
                show_debug_message(f"Añadida extensión .json: {full_path}")
            
            # Preparar datos
            if full_path.endswith('.jff'):
                data = afd.to_jff_format()
                show_debug_message("Preparados datos en formato JFF")
            else:  # .json o .afd
                data = afd.to_afd_format()
                show_debug_message("Preparados datos en formato JSON/AFD")
            
            # Guardar el archivo de la forma más simple posible
            if full_path.endswith('.jff'):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(data)
            else:
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            
            show_debug_message(f"¡Archivo guardado exitosamente en {full_path}!")
            
        except Exception as e:
            show_debug_message(f"Error al guardar: {str(e)}")
            import traceback
            show_debug_message(traceback.format_exc())

    page.title = "Simulador de Autómatas Finitos Deterministas"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.window_height = 800
    page.window_width = 1000
    
    # Global variables
    global closure_results
    closure_results = None
    global utility_operation_results
    utility_operation_results = None
    global utility_operation_type
    utility_operation_type = None
    
    # AFD instance
    afd = AFD()
    
    # Main tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Definición de AFD",
                content=ft.Container(padding=10)  # Will be filled later
            ),
            ft.Tab(
                text="Simulación",
                content=ft.Container(padding=10)  # Will be filled later
            ),
            ft.Tab(
                text="Utilidades",
                content=ft.Container(padding=10)  # Will be filled later
            ),
        ],
    )
    
    # --- First Tab: AFD Definition ---
    
    # Alphabet definition
    alphabet_title = ft.Text("Definición del Alfabeto", size=16, weight=ft.FontWeight.BOLD)
    alphabet_input = ft.TextField(
        label="Símbolos del alfabeto (separados por comas)",
        hint_text="Por ejemplo: a,b,c",
        expand=True
    )
    
    # Transición tabla
    transitions_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Estado", size=16))],  # Increase text size
        rows=[],
        border=ft.border.all(2, ft.colors.GREY_400),  # Add border
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        column_spacing=20,  # Increase column spacing
        height=400,  # Set a fixed height or use expand=True
        width=600
    )
    
    
    # Text field instances for transitions
    transition_fields = {}

    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        """Maneja el resultado del FilePicker."""
        if e.files:
            try:
                # En caso de selección de archivo (cargar)
                if len(e.files) > 0:
                    file_path = e.files[0].path
                    file_name_input.value = file_path
                    debug_load_automaton(None)
            except Exception as ex:
                show_debug_message(f"Error al procesar resultado de FilePicker: {str(ex)}")
        elif e.path:
            try:
                # En caso de guardar archivo
                file_name_input.value = e.path
                debug_save_automaton(None)
            except Exception as ex:
                show_debug_message(f"Error al procesar resultado de FilePicker (save): {str(ex)}")

    def open_file_picker_save(e):
        """Abre el diálogo para guardar archivo."""
        try:
            file_picker.save_file(
                allowed_extensions=["json", "jff", "afd"],
                file_name="automaton.json"
            )
        except Exception as ex:
            show_debug_message(f"Error al abrir FilePicker para guardar: {str(ex)}")

    def open_file_picker_load(e):
        """Abre el diálogo para cargar archivo."""
        try:
            file_picker.pick_files(
                allowed_extensions=["json", "jff", "afd"],
                allow_multiple=False
            )
        except Exception as ex:
            show_debug_message(f"Error al abrir FilePicker para cargar: {str(ex)}")

    # Actualiza los botones para usar el FilePicker
    save_button = ft.ElevatedButton("Guardar (Debug)", on_click=debug_save_automaton)
    load_button = ft.ElevatedButton("Cargar (Debug)", on_click=debug_load_automaton)
    save_picker_button = ft.ElevatedButton("Guardar con Explorador", on_click=open_file_picker_save)
    load_picker_button = ft.ElevatedButton("Cargar con Explorador", on_click=open_file_picker_load)

    # Actualiza el file_operations_container
 
    def update_alphabet(e):
        symbols = [s.strip() for s in alphabet_input.value.split(",") if s.strip()]
        afd.alphabet = set(symbols)
        update_transition_table()
        page.update()
        
    alphabet_button = ft.ElevatedButton("Actualizar Alfabeto", on_click=update_alphabet)
    alphabet_container = ft.Column([
        alphabet_title,
        ft.Row([alphabet_input, alphabet_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ])
    
    # States definition
    states_title = ft.Text("Definición de Estados", size=16, weight=ft.FontWeight.BOLD)
    states_input = ft.TextField(
        label="Estados (separados por comas)",
        hint_text="Por ejemplo: q0,q1,q2",
        expand=True
    )
    
    initial_state_dropdown = ft.Dropdown(
        label="Estado Inicial",
        options=[],
        width=150
    )
    
    # Keep track of the checkboxes for acceptance states
    acceptance_states_checkboxes = ft.Column([], tight=True)

    

    def pick_files_save(e):
        pick_files_dialog = ft.FilePicker(
            on_result=save_file_result
        )
        page.overlay.append(file_picker)
        page.overlay.append(pick_files_dialog)
        page.update()
        pick_files_dialog.save_file(
            allowed_extensions=["json", "jff", "afd"],
            file_name="automaton.json"
        )

    def pick_files_load(e):
        pick_files_dialog = ft.FilePicker(
            on_result=load_file_result
        )
        page.overlay.append(file_picker)
        page.overlay.append(pick_files_dialog)
        page.update()
        pick_files_dialog.pick_files(
            allowed_extensions=["json", "jff", "afd"],
            allow_multiple=False
        )
    
    def save_file_result(e: ft.FilePickerResultEvent):
        if e.path:
            file_name_input.value = e.path
            page.update()
            save_automaton(None)  # Guardar automáticamente

    def load_file_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_name_input.value = e.files[0].path
            page.update()
            load_automaton(None)  # Cargar automáticamente

    def update_states(e):
        states = [s.strip() for s in states_input.value.split(",") if s.strip()]
        
        # Clear existing states from AFD
        old_states = set(afd.states)
        
        # Update AFD states
        afd.states = set(states)
        
        # Update initial state dropdown
        initial_state_dropdown.options = [
            ft.dropdown.Option(text=state, key=state) for state in states
        ]
        
        # Update acceptance states checkboxes
        acceptance_states_checkboxes.controls.clear()
        
        for state in states:
            afd.add_state(state)
            is_acceptance = state in afd.acceptance_states
            
            def create_on_change_handler(state_name):
                def on_change(e):
                    if e.control.value:
                        afd.add_acceptance_state(state_name)
                    else:
                        afd.remove_acceptance_state(state_name)
                return on_change
            
            checkbox = ft.Checkbox(
                label=state,
                value=is_acceptance,
                on_change=create_on_change_handler(state)
            )
            acceptance_states_checkboxes.controls.append(checkbox)
        
        update_transition_table()
        page.update()
    
    def set_initial_state(e):
        if initial_state_dropdown.value:
            afd.set_initial_state(initial_state_dropdown.value)
            page.update()
    
    states_button = ft.ElevatedButton("Actualizar Estados", on_click=update_states)
    
    states_container = ft.Column([
        states_title,
        ft.Row([states_input, states_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([
            ft.Column([
                ft.Text("Estado Inicial:"),
                initial_state_dropdown
            ]),
            ft.Column([
                ft.Text("Estados de Aceptación:"),
                acceptance_states_checkboxes
            ], expand=True)
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
    ])
    
    # Assign the event handler after the function is defined
    initial_state_dropdown.on_change = set_initial_state
    
    # Transition table
    transitions_title = ft.Text("Función de Transición", size=16, weight=ft.FontWeight.BOLD)
    
    def update_transition_table():
        # Clear existing columns and rows
        transitions_table.columns.clear()
        transitions_table.rows.clear()
        transition_fields.clear()
        
        # Add state column header
        transitions_table.columns.append(ft.DataColumn(ft.Text("Estado")))
        
        # Add column headers for each symbol in the alphabet
        for symbol in sorted(afd.alphabet):
            transitions_table.columns.append(ft.DataColumn(ft.Text(symbol, size=16)))
        
        # Make sure we have at least one column
        if len(transitions_table.columns) == 0:
            transitions_table.columns.append(ft.DataColumn(ft.Text("Estado")))
        
        # Add rows for each state
        for state in sorted(afd.states):
            cells = [ft.DataCell(ft.Text(state, size=16))]
            
            for symbol in sorted(afd.alphabet):
                current_value = ""
                if state in afd.transitions and symbol in afd.transitions[state]:
                    current_value = afd.transitions[state][symbol]
                
                tf = ft.TextField(
                    value=current_value,
                    width=150,
                    height=60,
                    text_size=16,  # Increase text size
                    text_align=ft.TextAlign.CENTER,
                    border=ft.InputBorder.UNDERLINE,
                    filled=True
                )
                # Save reference to the text field
                transition_fields[(state, symbol)] = tf
                cells.append(ft.DataCell(tf))
            
            transitions_table.rows.append(ft.DataRow(cells=cells))
        page.update()
    
    def update_transitions(e):
        for (state, symbol), text_field in transition_fields.items():
            to_state = text_field.value.strip()
            if to_state:
                if to_state in afd.states:
                    afd.add_transition(state, symbol, to_state)
                else:
                    text_field.value = ""
                    text_field.border_color = ft.colors.RED
                    text_field.hint_text = "Estado inválido"
                    page.update()
        
        # After validating, show a confirmation
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Transiciones actualizadas correctamente"),
            action="OK",
        )
        page.snack_bar.open = True
        page.update()
    
    transitions_button = ft.ElevatedButton("Guardar Transiciones", on_click=update_transitions)
    transitions_container = ft.Column([
        transitions_title,
        transitions_table,
        transitions_button
    ])
    
    # File operations
    file_operations_title = ft.Text("Guardar/Cargar Autómata", size=16, weight=ft.FontWeight.BOLD)
    file_name_input = ft.TextField(
        label="Nombre del archivo",
        hint_text="automata.json, automata.jff o automata.afd",
        width=300
    )
    
    def save_automaton(e):
        file_name = file_name_input.value
        if not file_name:
            page.snack_bar = ft.SnackBar(content=ft.Text("Nombre de archivo requerido"))
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            # Asegurarse de usar una ruta absoluta para el archivo
            absolute_path = os.path.abspath(file_name)
            directory = os.path.dirname(absolute_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            if file_name.endswith(".json"):
                # Save as JSON format
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(afd.to_afd_format(), f, indent=2)
            elif file_name.endswith(".jff"):
                # Save as JFLAP format
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(afd.to_jff_format())
            elif file_name.endswith(".afd"):
                # Save as AFD format (same as JSON but with .afd extension)
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(afd.to_afd_format(), f, indent=2)
            else:
                # Default to JSON if no extension
                file_name += ".json"
                absolute_path = os.path.abspath(file_name)
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(afd.to_afd_format(), f, indent=2)
                    
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Autómata guardado como {file_name}"))
            page.snack_bar.open = True
        except PermissionError: 
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar: {str(e)}"))
            page.snack_bar.open = True
        page.update()
    
    def load_automaton(e):
        global afd  # Move the global declaration here, before any assignment
        file_name = file_name_input.value
        if not file_name:
            page.snack_bar = ft.SnackBar(content=ft.Text("Nombre de archivo requerido"))
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            absolute_path = os.path.abspath(file_name)
            if not os.path.exists(file_name):
                page.snack_bar = ft.SnackBar(content=ft.Text(f"El archivo {file_name} no existe"))
                page.snack_bar.open = True
                page.update()
                return
                
            
            if file_name.endswith(".json") or file_name.endswith(".afd"):
                # Load JSON/AFD format
                with open(file_name, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    afd = AFD.from_afd_format(data)
            elif file_name.endswith(".jff"):
                # Load JFLAP format
                with open(file_name, "r", encoding="utf-8") as f:
                    jff_content = f.read()
                    afd = AFD.from_jff_format(jff_content)
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Formato de archivo no soportado"))
                page.snack_bar.open = True
                page.update()
                return
                
            # Update UI to reflect loaded automaton
            alphabet_input.value = ",".join(sorted(afd.alphabet))
            states_input.value = ",".join(sorted(afd.states))
            update_states(None)
            
            # Set initial state in dropdown
            initial_state_dropdown.value = afd.initial_state
            
            # Update acceptance states checkboxes
            for checkbox in acceptance_states_checkboxes.controls:
                if hasattr(checkbox, "label"):
                    checkbox.value = checkbox.label in afd.acceptance_states
            
            update_transition_table()
            
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Autómata cargado desde {file_name}"))
            page.snack_bar.open = True
        except json.JSONDecodeError:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al cargar: {str(e)}"))
            page.snack_bar.open = True
        page.update()
    
    save_button = ft.ElevatedButton("Guardar (Debug)", on_click=debug_save_automaton)
    load_button = ft.ElevatedButton("Cargar(Debug)", on_click=debug_load_automaton)
    
    file_operations_container = ft.Column([
        file_operations_title,
        ft.Row([
            file_name_input,
            save_button,
            load_button
        ])
    ])
    
    def check_write_permissions(e):
        """Verifica si la aplicación tiene permisos de escritura."""
        try:
            # Obtener directorio actual
            current_dir = os.getcwd()
            test_file_path = os.path.join(current_dir, "test_permissions.txt")
            
            # Intentar escribir un archivo de prueba
            with open(test_file_path, "w") as f:
                f.write("Prueba de permisos de escritura")
                
            # Intentar leer el archivo
            with open(test_file_path, "r") as f:
                content = f.read()
                
            # Eliminar el archivo de prueba
            os.remove(test_file_path)
            
            show_debug_message(f"¡Prueba de permisos exitosa!\n"
                            f"Directorio: {current_dir}\n"
                            f"Se pudo escribir y leer correctamente.")
            
        except Exception as e:
            show_debug_message(f"Error en la prueba de permisos:\n{str(e)}")

    # Añade un botón de prueba de permisos en la interfaz
    permission_button = ft.ElevatedButton("Verificar Permisos", on_click=check_write_permissions)

    # Actualiza el file_operations_container para incluir el nuevo botón
    file_operations_container = ft.Column([
        file_operations_title,
        ft.Row([
            file_name_input,
            save_button,
            load_button,
            permission_button
        ])
    ])
    # Assign the first tab content
    tabs.tabs[0].content = ft.Container(
        content=ft.Column([
            alphabet_container,
            ft.Divider(),
            states_container,
            ft.Divider(),
            transitions_container,
            ft.Divider(),
            file_operations_container
        ]),
        padding=20
    )
    
    # --- Second Tab: Simulation ---
    simulation_title = ft.Text("Simulación de Cadenas", size=16, weight=ft.FontWeight.BOLD)
    input_string = ft.TextField(
        label="Cadena a evaluar",
        hint_text="Por ejemplo: abba",
        width=300
    )
    
    simulation_result = ft.Text("", size=16)
    simulation_trace = ft.Column([])
    
    def simulate_string(e):
        string_to_evaluate = input_string.value
        
        if not string_to_evaluate:
            simulation_result.value = "Por favor ingrese una cadena para evaluar"
            simulation_result.color = ft.colors.RED
            simulation_trace.controls.clear()
            page.update()
            return
            
        is_accepted, trace = afd.validate_string(string_to_evaluate)
        
        if is_accepted:
            simulation_result.value = f"La cadena '{string_to_evaluate}' es ACEPTADA por el autómata"
            simulation_result.color = ft.colors.GREEN
        else:
            if not trace:
                simulation_result.value = f"La cadena '{string_to_evaluate}' contiene símbolos que no están en el alfabeto o el autómata no está bien definido"
            else:
                simulation_result.value = f"La cadena '{string_to_evaluate}' es RECHAZADA por el autómata"
            simulation_result.color = ft.colors.RED
            
        # Display trace
        simulation_trace.controls.clear()
        
        if trace:
            # Header for the trace table
            trace_header = ft.Row([
                ft.Text("Estado Actual", width=150, weight=ft.FontWeight.BOLD),
                ft.Text("Símbolo", width=100, weight=ft.FontWeight.BOLD),
                ft.Text("Estado Siguiente", width=150, weight=ft.FontWeight.BOLD)
            ])
            simulation_trace.controls.append(trace_header)
            
            # Add each step in the trace
            for current, symbol, next_state in trace:
                step = ft.Row([
                    ft.Text(current, width=150),
                    ft.Text(symbol, width=100),
                    ft.Text(next_state, width=150)
                ])
                simulation_trace.controls.append(step)
                
            # Add final state information
            if trace:
                final_state = trace[-1][2]  # The last transition's destination state
                is_final_acceptance = final_state in afd.acceptance_states
                
                final_state_text = ft.Text(
                    f"Estado final: {final_state} ({'aceptación' if is_final_acceptance else 'no aceptación'})",
                    color=ft.colors.GREEN if is_final_acceptance else ft.colors.RED,
                    weight=ft.FontWeight.BOLD
                )
                simulation_trace.controls.append(final_state_text)
        
        page.update()
    
    simulate_button = ft.ElevatedButton("Simular", on_click=simulate_string)
    
    # Assign the second tab content
    tabs.tabs[1].content = ft.Container(
        content=ft.Column([
            simulation_title,
            ft.Row([input_string, simulate_button]),
            simulation_result,
            ft.Container(height=20),  # Spacer
            ft.Text("Traza de ejecución:", size=16, weight=ft.FontWeight.BOLD),
            simulation_trace
        ]),
        padding=20
    )
    
    # --- Third Tab: Utilities ---
    utilities_title = ft.Text("Operaciones sobre Cadenas", size=16, weight=ft.FontWeight.BOLD)
    
    # String operations
    string_operations_container = ft.Column([])
    utility_string_input = ft.TextField(
        label="Cadena para operaciones",
        hint_text="Por ejemplo: abba",
        width=300
    )
    
    export_file_name = ft.TextField(
        label="Nombre del archivo para exportar",
        hint_text="resultados.txt",
        width=300
    )
    
    # Results display
    utility_results = ft.Column([])
    
    def export_results(e):
        file_name = export_file_name.value
        if not file_name:
            page.snack_bar = ft.SnackBar(content=ft.Text("Nombre de archivo requerido para exportar"))
            page.snack_bar.open = True
            page.update()
            return
            
        if not file_name.endswith(".txt"):
            file_name += ".txt"
            
        try:
            with open(file_name, "w") as f:
                if utility_operation_type == "prefixes":
                    f.write(f"Prefijos de '{utility_string_input.value}':\n")
                    for prefix in utility_operation_results:
                        is_accepted, _ = afd.validate_string(prefix)
                        f.write(f"'{prefix}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}\n")
                        
                elif utility_operation_type == "suffixes":
                    f.write(f"Sufijos de '{utility_string_input.value}':\n")
                    for suffix in utility_operation_results:
                        is_accepted, _ = afd.validate_string(suffix)
                        f.write(f"'{suffix}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}\n")
                        
                elif utility_operation_type == "substrings":
                    f.write(f"Subcadenas de '{utility_string_input.value}':\n")
                    for substring in utility_operation_results:
                        is_accepted, _ = afd.validate_string(substring)
                        f.write(f"'{substring}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}\n")
                        
                elif utility_operation_type == "kleene":
                    f.write(f"Cerradura de Kleene (Σ*) con longitud máxima {int(closure_length.value)}:\n")
                    
                    # Group by length
                    for length in range(int(closure_length.value) + 1):
                        length_strings = [s for s in utility_operation_results if len(s) == length]
                        if length_strings:
                            f.write(f"\nLongitud {length}:\n")
                            for string in length_strings:
                                is_accepted, _ = afd.validate_string(string)
                                f.write(f"'{string if string else 'ε'}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}\n")
                                
                elif utility_operation_type == "positive":
                    f.write(f"Cerradura Positiva (Σ+) con longitud máxima {int(closure_length.value)}:\n")
                    
                    # Group by length
                    for length in range(1, int(closure_length.value) + 1):
                        length_strings = [s for s in utility_operation_results if len(s) == length]
                        if length_strings:
                            f.write(f"\nLongitud {length}:\n")
                            for string in length_strings:
                                is_accepted, _ = afd.validate_string(string)
                                f.write(f"'{string}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}\n")
                                
                elif utility_operation_type == "validation":
                    f.write("Resultados de validación:\n\n")
                    
                    # Count accepted and rejected strings
                    accepted_strings = []
                    rejected_strings = []
                    
                    for string in utility_operation_results:
                        is_accepted, _ = afd.validate_string(string)
                        if is_accepted:
                            accepted_strings.append(string)
                        else:
                            rejected_strings.append(string)
                            
                    f.write("Cadenas ACEPTADAS:\n")
                    for string in accepted_strings:
                        f.write(f"'{string if string else 'ε'}'\n")
                        
                    f.write("\nCadenas RECHAZADAS:\n")
                    for string in rejected_strings:
                        f.write(f"'{string if string else 'ε'}'\n")
                        
                    f.write(f"\nTotal: {len(utility_operation_results)} cadenas, {len(accepted_strings)} aceptadas, {len(rejected_strings)} rechazadas\n")
                    
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Resultados exportados a {file_name}"))
            page.snack_bar.open = True
        except Exception as e:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al exportar: {str(e)}"))
            page.snack_bar.open = True
        page.update()
    def get_prefixes(e):
        string = utility_string_input.value
        if not string:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor ingrese una cadena"))
            page.snack_bar.open = True
            page.update()
            return
            
        global utility_operation_results, utility_operation_type
        utility_operation_results = afd.get_prefixes(string)
        utility_operation_type = "prefixes"
        
        # Display results
        utility_results.controls.clear()
        
        # Header for the results
        utility_results.controls.append(ft.Text(f"Prefijos de '{string}':", weight=ft.FontWeight.BOLD))
        
        # Add each prefix with validation result
        for prefix in utility_operation_results:
            is_accepted, _ = afd.validate_string(prefix)
            result_text = ft.Text(
                f"'{prefix if prefix else 'ε'}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}",
                color=ft.colors.GREEN if is_accepted else ft.colors.RED
            )
            utility_results.controls.append(result_text)
            
        page.update()
        
    def get_suffixes(e):
        string = utility_string_input.value
        if not string:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor ingrese una cadena"))
            page.snack_bar.open = True
            page.update()
            return
            
        global utility_operation_results, utility_operation_type
        utility_operation_results = afd.get_suffixes(string)
        utility_operation_type = "suffixes"
        
        # Display results
        utility_results.controls.clear()
        
        # Header for the results
        utility_results.controls.append(ft.Text(f"Sufijos de '{string}':", weight=ft.FontWeight.BOLD))
        
        # Add each suffix with validation result
        for suffix in utility_operation_results:
            is_accepted, _ = afd.validate_string(suffix)
            result_text = ft.Text(
                f"'{suffix if suffix else 'ε'}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}",
                color=ft.colors.GREEN if is_accepted else ft.colors.RED
            )
            utility_results.controls.append(result_text)
            
        page.update()
        
    def get_substrings(e):
        string = utility_string_input.value
        if not string:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor ingrese una cadena"))
            page.snack_bar.open = True
            page.update()
            return
            
        global utility_operation_results, utility_operation_type
        utility_operation_results = afd.get_substrings(string)
        utility_operation_type = "substrings"
        
        # Display results
        utility_results.controls.clear()
        
        # Header for the results
        utility_results.controls.append(ft.Text(f"Subcadenas de '{string}':", weight=ft.FontWeight.BOLD))
        
        # Add each substring with validation result
        for substring in utility_operation_results:
            is_accepted, _ = afd.validate_string(substring)
            result_text = ft.Text(
                f"'{substring}' - {'ACEPTADA' if is_accepted else 'RECHAZADA'}",
                color=ft.colors.GREEN if is_accepted else ft.colors.RED
            )
            utility_results.controls.append(result_text)
            
        page.update()
    
    # For closures, we need a length input
    closure_length = ft.Slider(
        min=1,
        max=10,
        divisions=9,
        value=3,
        label="{value}",
        width=300
    )
    
    def get_kleene_closure(e):
        if not afd.alphabet:
            page.snack_bar = ft.SnackBar(content=ft.Text("El alfabeto está vacío"))
            page.snack_bar.open = True
            page.update()
            return
            
        length = int(closure_length.value)
        
        global utility_operation_results, utility_operation_type
        utility_operation_results = afd.get_kleene_closure(length)
        utility_operation_type = "kleene"
        
        # Display results
        utility_results.controls.clear()
        
        # Header for the results
        utility_results.controls.append(ft.Text(f"Cerradura de Kleene (Σ*) con longitud máxima {length}:", weight=ft.FontWeight.BOLD))
        
        # Group by length
        for i in range(length + 1):
            length_strings = [s for s in utility_operation_results if len(s) == i]
            if length_strings:
                utility_results.controls.append(ft.Text(f"\nLongitud {i}:", weight=ft.FontWeight.BOLD))
                
                # Organize strings in a table-like structure
                rows = []
                current_row = []
                
                for string in length_strings:
                    is_accepted, _ = afd.validate_string(string)
                    
                    result_text = ft.Text(
                        f"'{string if string else 'ε'}' - {'✓' if is_accepted else '✗'}",
                        color=ft.colors.GREEN if is_accepted else ft.colors.RED,
                        size=14
                    )
                    
                    current_row.append(result_text)
                    
                    # Create rows with 5 items each
                    if len(current_row) == 5:
                        rows.append(ft.Row(current_row, spacing=10))
                        current_row = []
                
                # Add any remaining items
                if current_row:
                    rows.append(ft.Row(current_row, spacing=10))
                
                for row in rows:
                    utility_results.controls.append(row)
            
        page.update()
        
    def get_positive_closure(e):
        if not afd.alphabet:
            page.snack_bar = ft.SnackBar(content=ft.Text("El alfabeto está vacío"))
            page.snack_bar.open = True
            page.update()
            return
            
        length = int(closure_length.value)
        
        global utility_operation_results, utility_operation_type
        utility_operation_results = afd.get_positive_closure(length)
        utility_operation_type = "positive"
        
        # Display results
        utility_results.controls.clear()
        
        # Header for the results
        utility_results.controls.append(ft.Text(f"Cerradura Positiva (Σ+) con longitud máxima {length}:", weight=ft.FontWeight.BOLD))
        
        # Group by length
        for i in range(1, length + 1):
            length_strings = [s for s in utility_operation_results if len(s) == i]
            if length_strings:
                utility_results.controls.append(ft.Text(f"\nLongitud {i}:", weight=ft.FontWeight.BOLD))
                
                # Organize strings in a table-like structure
                rows = []
                current_row = []
                
                for string in length_strings:
                    is_accepted, _ = afd.validate_string(string)
                    
                    result_text = ft.Text(
                        f"'{string}' - {'✓' if is_accepted else '✗'}",
                        color=ft.colors.GREEN if is_accepted else ft.colors.RED,
                        size=14
                    )
                    
                    current_row.append(result_text)
                    
                    # Create rows with 5 items each
                    if len(current_row) == 5:
                        rows.append(ft.Row(current_row, spacing=10))
                        current_row = []
                
                # Add any remaining items
                if current_row:
                    rows.append(ft.Row(current_row, spacing=10))
                
                for row in rows:
                    utility_results.controls.append(row)
            
        page.update()
        
    # Batch validation input
    batch_input = ft.TextField(
        label="Cadenas para validación en lote (separadas por comas)",
        hint_text="Por ejemplo: abba,ab,aa,bb",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=500
    )
    
    def batch_validate(e):
        input_text = batch_input.value
        if not input_text:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor ingrese cadenas para validar"))
            page.snack_bar.open = True
            page.update()
            return
            
        # Split by commas and clean whitespace
        strings = [s.strip() for s in input_text.split(",") if s.strip()]
        
        global utility_operation_results, utility_operation_type
        utility_operation_results = strings
        utility_operation_type = "validation"
        
        # Display results
        utility_results.controls.clear()
        
        # Header for the results
        utility_results.controls.append(ft.Text("Resultados de validación:", weight=ft.FontWeight.BOLD))
        
        # Count accepted and rejected strings
        accepted_strings = []
        rejected_strings = []
        
        for string in strings:
            is_accepted, _ = afd.validate_string(string)
            if is_accepted:
                accepted_strings.append(string)
            else:
                rejected_strings.append(string)
                
        # Show accepted strings
        utility_results.controls.append(ft.Text("\nCadenas ACEPTADAS:", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN))
        if accepted_strings:
            for string in accepted_strings:
                utility_results.controls.append(ft.Text(f"'{string if string else 'ε'}'"))
        else:
            utility_results.controls.append(ft.Text("(Ninguna)"))
            
        # Show rejected strings
        utility_results.controls.append(ft.Text("\nCadenas RECHAZADAS:", weight=ft.FontWeight.BOLD, color=ft.colors.RED))
        if rejected_strings:
            for string in rejected_strings:
                utility_results.controls.append(ft.Text(f"'{string if string else 'ε'}'"))
        else:
            utility_results.controls.append(ft.Text("(Ninguna)"))
            
        # Summary
        utility_results.controls.append(ft.Text(
            f"\nTotal: {len(strings)} cadenas, {len(accepted_strings)} aceptadas, {len(rejected_strings)} rechazadas",
            weight=ft.FontWeight.BOLD
        ))
        
        page.update()
    
    # Buttons for string operations
    prefix_button = ft.ElevatedButton("Prefijos", on_click=get_prefixes)
    suffix_button = ft.ElevatedButton("Sufijos", on_click=get_suffixes)
    substring_button = ft.ElevatedButton("Subcadenas", on_click=get_substrings)
    
    string_operations_container.controls = [
        ft.Text("Operaciones de Cadenas:", weight=ft.FontWeight.BOLD),
        ft.Row([utility_string_input]),
        ft.Row([prefix_button, suffix_button, substring_button]),
    ]
    
    # Create container for closure operations
    closure_operations_container = ft.Column([
        ft.Text("Operaciones de Cerradura:", weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Text("Longitud máxima:"),
            closure_length,
        ]),
        ft.Row([
            ft.ElevatedButton("Cerradura de Kleene (Σ*)", on_click=get_kleene_closure),
            ft.ElevatedButton("Cerradura Positiva (Σ+)", on_click=get_positive_closure),
        ]),
    ])
    
    # Create container for batch validation
    batch_validation_container = ft.Column([
        ft.Text("Validación por Lotes:", weight=ft.FontWeight.BOLD),
        batch_input,
        ft.Row([
            ft.ElevatedButton("Validar", on_click=batch_validate),
        ]),
    ])
    
    # Results export control
    export_container = ft.Column([
        ft.Text("Exportar Resultados:", weight=ft.FontWeight.BOLD),
        ft.Row([
            export_file_name,
            ft.ElevatedButton("Exportar", on_click=export_results),
        ]),
    ])
    
    # Assign the third tab content
    tabs.tabs[2].content = ft.Container(
        content=ft.Column([
            utilities_title,
            string_operations_container,
            ft.Divider(),
            closure_operations_container,
            ft.Divider(),
            batch_validation_container,
            ft.Divider(),
            ft.Container(
                content=utility_results,
                padding=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                bgcolor=ft.colors.GREY_50,
                expand=True
            ),
            ft.Divider(),
            export_container
        ]),
        padding=20
    )
    
    # Add the main tabs to the page
    page.add(tabs)

# Run the app
ft.app(target=main)