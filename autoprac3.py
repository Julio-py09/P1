import flet as ft
import xml.etree.ElementTree as ET
from xml.dom import minidom
from itertools import product
import json
from typing import List, Dict, Set, Union, Tuple

class AutomatonSimulator:
    def __init__(self):
        self.alphabet: List[str] = []
        self.states: List[str] = []
        self.initial_state: Union[str, None] = None
        self.accepting_states: List[str] = []
        self.transition_table: Dict[Tuple[str, str], Union[str, List[str]]] = {}
        self.is_nfa: bool = False

    @staticmethod
    def substrings(s: str) -> List[str]:
        """Genera todas las subcadenas de una cadena"""
        return [s[i:j] for i in range(len(s)) for j in range(i+1, len(s)+1)]

    @staticmethod
    def prefixes(s: str) -> List[str]:
        """Genera todos los prefijos de una cadena"""
        return [s[:i] for i in range(len(s)+1)]

    @staticmethod
    def suffixes(s: str) -> List[str]:
        """Genera todos los sufijos de una cadena"""
        return [s[i:] for i in range(len(s)+1)]

    @staticmethod
    def kleene_closure(alphabet: List[str], max_len: int) -> List[str]:
        """Genera la cerradura de Kleene para un alfabeto"""
        return ["".join(p) for i in range(max_len+1) for p in product(alphabet, repeat=i)]

    @staticmethod
    def positive_closure(alphabet: List[str], max_len: int) -> List[str]:
        """Genera la cerradura positiva para un alfabeto"""
        return ["".join(p) for i in range(1, max_len+1) for p in product(alphabet, repeat=i)]

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Simulador Avanzado de AFD/AFN"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Instancia del simulador
    simulator = AutomatonSimulator()

    # ========== Controles de la Interfaz ==========
    # Entradas básicas
    alphabet_input = ft.TextField(
        label="Alfabeto (separado por comas)",
        width=350,
        hint_text="Ej: a,b,c",
        border_color=ft.colors.BLUE_400
    )
    
    states_input = ft.TextField(
        label="Estados (separados por comas)",
        width=350,
        hint_text="Ej: q0,q1,q2",
        border_color=ft.colors.BLUE_400
    )
    
    # Dropdown para estado inicial
    initial_state_dropdown = ft.Dropdown(
        label="Estado inicial",
        width=350,
        options=[],
        border_color=ft.colors.BLUE_400
    )
    
    # Checkboxes para estados de aceptación
    accepting_states_checkboxes = ft.Column()
    
    # Selector de tipo de autómata
    automaton_type = ft.Switch(
        label="Autómata No Determinista (AFN)",
        value=False,
        active_color=ft.colors.GREEN,
        inactive_track_color=ft.colors.RED,
        on_change=lambda e: update_automaton_type(e)
    )

    input_string = ft.TextField(
        label="Cadena a validar",
        width=350,
        hint_text="Ej: aabba",
        border_color=ft.colors.BLUE_400
    )
    
    # Tabla de transiciones
    transition_table_display = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=300
    )
    
    # Área de resultados
    output_text = ft.Text(
        style=ft.TextThemeStyle.BODY_MEDIUM,
        color=ft.colors.BLUE_800
    )
    
    simulation_output = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=200
    )
    
    # Controles para operaciones de lenguaje
    operations_input = ft.TextField(
        label="Cadena para operaciones",
        width=350,
        border_color=ft.colors.PURPLE_400
    )
    
    max_len_input = ft.TextField(
        label="Longitud máxima para cerraduras",
        width=150,
        value="3",
        border_color=ft.colors.PURPLE_400
    )
    
    operations_output = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=300
    )
    
    # File Picker
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    # ========== Funciones Principales ==========
    def update_automaton_type(e):
        """Actualiza el tipo de autómata entre AFD y AFN"""
        simulator.is_nfa = automaton_type.value
        
        # Convertir transiciones existentes al nuevo tipo
        for key, value in list(simulator.transition_table.items()):
            if simulator.is_nfa:
                if not isinstance(value, list):
                    simulator.transition_table[key] = [value] if value else []
            else:
                if isinstance(value, list):
                    simulator.transition_table[key] = value[0] if value else ""
        
        update_transition_table()
        page.update()

    def update_alphabet(e):
        """Actualiza el alfabeto del autómata"""
        simulator.alphabet = [s.strip() for s in alphabet_input.value.split(",") if s.strip()]
        update_transition_table()
        page.update()

    def update_states(e):
        """Actualiza la lista de estados del autómata"""
        simulator.states = [s.strip() for s in states_input.value.split(",") if s.strip()]
        
        # Actualizar dropdown de estado inicial
        initial_state_dropdown.options = [
            ft.dropdown.Option(state) 
            for state in simulator.states
        ]
        initial_state_dropdown.value = None
        simulator.initial_state = None
        
        # Actualizar checkboxes de estados de aceptación
        accepting_states_checkboxes.controls = [
            ft.Checkbox(label=state, value=False)
            for state in simulator.states
        ]
        
        # Limpiar tabla de transiciones
        simulator.transition_table.clear()
        update_transition_table()
        page.update()

    def update_transition_table():
        """Actualiza la visualización de la tabla de transiciones"""
        transition_table_display.controls.clear()
        
        # Agregar el símbolo ε al alfabeto si no está presente
        if "ε" not in simulator.alphabet:
            simulator.alphabet.append("ε")
        
        if simulator.states and simulator.alphabet:
            # Crear encabezado
            header = ft.Row([ft.Text("Estado", width=150, weight="bold")])
            header.controls.extend(
                ft.Text(symbol, width=150, weight="bold") 
                for symbol in simulator.alphabet
            )
            transition_table_display.controls.append(header)
            
            # Crear filas para cada estado
            for state in simulator.states:
                row = ft.Row([ft.Text(state, width=150)])
                
                for symbol in simulator.alphabet:
                    current = simulator.transition_table.get((state, symbol), [] if simulator.is_nfa else "")
                    
                    cell = ft.TextField(
                        width=150,
                        hint_text="q0,q1" if simulator.is_nfa else "q0",
                        value=",".join(current) if simulator.is_nfa and isinstance(current, list) else current,
                        dense=True,
                        border_color=ft.colors.BLUE_300,
                        on_change=lambda e, s=state, sym=symbol: update_transition_cell(s, sym, e.control.value)
                    )
                    row.controls.append(cell)
                
                transition_table_display.controls.append(row)
        
        page.update()

    def update_transition_cell(state: str, symbol: str, value: str):
        """Actualiza una celda específica en la tabla de transiciones"""
        value = value.strip()
        
        if not value:
            simulator.transition_table.pop((state, symbol), None)
            return
            
        if simulator.is_nfa:
            # Procesar múltiples estados para AFN
            destinations = [s.strip() for s in value.split(",") if s.strip()]
            invalid = [s for s in destinations if s not in simulator.states]
            
            if invalid:
                output_text.value = f"Error: Estados inválidos: {', '.join(invalid)}"
                page.update()
                return
                
            simulator.transition_table[(state, symbol)] = destinations
        else:
            # Procesar único estado para AFD
            if value not in simulator.states:
                output_text.value = f"Error: Estado destino '{value}' no definido."
                page.update()
                return
                
            simulator.transition_table[(state, symbol)] = value

    def define_automaton(e):
        """Define el autómata completo"""
        # Actualizar estado inicial
        simulator.initial_state = initial_state_dropdown.value
        
        # Actualizar estados de aceptación
        simulator.accepting_states = [
            checkbox.label for checkbox in accepting_states_checkboxes.controls
            if checkbox.value
        ]
        
        if validate_automaton():
            output_text.value = "Autómata definido correctamente!"
        page.update()

    def validate_automaton() -> bool:
        """Valida que el autómata esté correctamente definido"""
        if not simulator.initial_state:
            output_text.value = "Error: Seleccione un estado inicial."
            return False
            
        if not simulator.accepting_states:
            output_text.value = "Error: Seleccione al menos un estado de aceptación."
            return False
            
        if not simulator.is_nfa:
            # Validación adicional para AFD
            for state in simulator.states:
                for symbol in simulator.alphabet:
                    if (state, symbol) not in simulator.transition_table:
                        output_text.value = f"Error: Falta transición para ({state}, {symbol})."
                        return False
                        
        return True

    # ========== Funciones de Validación y Simulación ==========
    def validate_string(input_str: str) -> Tuple[bool, str, List]:
        """Valida si una cadena es aceptada por el autómata"""
        if not simulator.initial_state:
            return False, "Error: No hay estado inicial definido.", []
        
        current_states = {simulator.initial_state}
        trace = []

        # Expandir transiciones lambda desde el estado inicial
        current_states = expand_lambda_transitions(current_states)

        for symbol in input_str:
            if symbol not in simulator.alphabet:
                return False, f"Error: Símbolo '{symbol}' no está en el alfabeto.", trace

            next_states = set()
            for state in current_states:
                destinations = simulator.transition_table.get((state, symbol), [])
                next_states.update(destinations)

            # Expandir transiciones lambda desde los estados alcanzados
            next_states = expand_lambda_transitions(next_states)

            if not next_states:
                return False, f"Error: No hay transición para '{symbol}' desde {current_states}.", trace

            trace.append((sorted(current_states), symbol, sorted(next_states)))
            current_states = next_states

        # Verificar si algún estado final es un estado de aceptación
        is_accepted = any(state in simulator.accepting_states for state in current_states)
        if is_accepted:
            message = f"Cadena ACEPTADA. Estados finales de aceptación: {sorted(current_states)}"
        else:
            message = f"Cadena RECHAZADA. Estados finales: {sorted(current_states)}"
        return is_accepted, message, trace

    def expand_lambda_transitions(states: Set[str]) -> Set[str]:
        """Expande las transiciones lambda (ε) desde un conjunto de estados"""
        expanded_states = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            lambda_transitions = simulator.transition_table.get((state, "ε"), [])
            for next_state in lambda_transitions:
                if next_state not in expanded_states:
                    expanded_states.add(next_state)
                    stack.append(next_state)

        return expanded_states
    
    def show_lambda_closure(e):
        """Muestra la clausura lambda de un estado seleccionado"""
        selected_state = initial_state_dropdown.value
        if not selected_state:
            output_text.value = "Error: Seleccione un estado para calcular la clausura lambda."
            page.update()
            return

        lambda_closure = expand_lambda_transitions({selected_state})
        output_text.value = f"Clausura Lambda de {selected_state}: {{{', '.join(sorted(lambda_closure))}}}"
        page.update()

    def run_validation(e):
        """Maneja el evento de validación de cadena"""
        input_str = input_string.value.strip()
        if not input_str:
            output_text.value = "Error: Ingrese una cadena para validar."
            page.update()
            return

        # Validar la cadena usando la función validate_string
        is_accepted, message, trace = validate_string(input_str)
        
        # Mostrar el mensaje de validación (si es válida o no)
        output_text.value = message
        
        # Mostrar traza de ejecución
        simulation_output.controls.clear()
        simulation_output.controls.append(ft.Text("Traza de ejecución:", weight="bold"))
        
        for step in trace:
            current, symbol, next_states = step
            if symbol == "ε":
                sim_text = ft.Text(
                    f"δ({{{', '.join(current)}}}, λ) = {{{', '.join(next_states)}}}",
                    color=ft.colors.PURPLE_700
                )
            else:
                sim_text = ft.Text(
                    f"δ({{{', '.join(current)}}}, {symbol}) = {{{', '.join(next_states)}}}",
                    color=ft.colors.BLUE_700
                )
            simulation_output.controls.append(sim_text)
            
            # Mostrar estados activos en cada paso
            simulation_output.controls.append(
                ft.Text(f"Estados activos: {{{', '.join(current)}}}", color=ft.colors.GREEN_800)
            )
            simulation_output.controls.append(
                ft.Text(f"Estados siguientes: {{{', '.join(next_states)}}}", color=ft.colors.ORANGE_800)
            )
        
        # Agregar mensaje final en la traza indicando si la cadena es válida o no
        if is_accepted:
            simulation_output.controls.append(
                ft.Text("Resultado: La cadena es válida (llega a un estado de aceptación).", color=ft.colors.GREEN_700, weight="bold")
            )
        else:
            simulation_output.controls.append(
                ft.Text("Resultado: La cadena NO es válida (no llega a un estado de aceptación).", color=ft.colors.RED_700, weight="bold")
            )
        
        # Actualizar la página para reflejar los cambios
        page.update()

    def step_by_step_simulation(e):
        """Ejecuta una simulación paso a paso"""
        input_str = input_string.value.strip()
        if not input_str:
            output_text.value = "Error: Ingrese una cadena para simular."
            page.update()
            return

        simulation_output.controls.clear()
        simulation_output.controls.append(ft.Text("Simulación Paso a Paso:", size=16, weight="bold"))
        
        current_states = {simulator.initial_state}
        simulation_output.controls.append(
            ft.Text(f"Estado inicial: {{{', '.join(current_states)}}}", color=ft.colors.GREEN_800)
        )

        for i, symbol in enumerate(input_str):
            if symbol not in simulator.alphabet:
                output_text.value = f"Error: Símbolo '{symbol}' no está en el alfabeto."
                page.update()
                return

            next_states = set()
            transitions = []
            
            for state in current_states:
                destinations = simulator.transition_table.get((state, symbol), [])
                if simulator.is_nfa:
                    for dest in destinations:
                        transitions.append((state, dest))
                    next_states.update(destinations)
                else:
                    if destinations:
                        transitions.append((state, destinations))
                        next_states.add(destinations)

            if not next_states:
                simulation_output.controls.append(
                    ft.Text(f"Paso {i+1}: No hay transición para '{symbol}'", color=ft.colors.RED)
                )
                output_text.value = "Cadena RECHAZADA (transición faltante)"
                page.update()
                return

            # Mostrar transiciones
            simulation_output.controls.append(
                ft.Text(f"\nPaso {i+1}: Símbolo '{symbol}'", weight="bold")
            )
            
            for src, dest in transitions:
                simulation_output.controls.append(
                    ft.Text(f"  {src} → {dest}", color=ft.colors.BLUE_600)
                )
            
            simulation_output.controls.append(
                ft.Text(f"Estados actuales: {{{', '.join(sorted(next_states))}}}", color=ft.colors.GREEN_800)
            )
            
            current_states = next_states

        # Verificar aceptación
        final_accepting = [s for s in current_states if s in simulator.accepting_states]
        if final_accepting:
            output_text.value = f"CADENA ACEPTADA. Estados finales de aceptación: {final_accepting}"
        else:
            output_text.value = f"CADENA RECHAZADA. Estados finales: {sorted(current_states)}"
        
        page.update()

    # ========== Funciones de Operaciones ==========
    def calculate_operations(e):
        """Calcula todas las operaciones lingüísticas para una cadena"""
        input_str = operations_input.value.strip()
        if not input_str:
            output_text.value = "Error: Ingrese una cadena para analizar."
            page.update()
            return

        try:
            max_len = int(max_len_input.value) if max_len_input.value else 3
            if max_len < 1:
                raise ValueError("La longitud debe ser ≥1")
        except ValueError:
            output_text.value = "Error: Longitud máxima debe ser un número ≥1."
            page.update()
            return

        # Calcular todas las operaciones
        results = {
            "Subcadenas": simulator.substrings(input_str),
            "Prefijos": simulator.prefixes(input_str),
            "Sufijos": simulator.suffixes(input_str)
        }

        # Calcular cerraduras usando el alfabeto definido o caracteres de la cadena
        current_alphabet = simulator.alphabet if simulator.alphabet else list(set(input_str))
        results["Cerradura de Kleene (Σ*)"] = simulator.kleene_closure(current_alphabet, max_len)
        results["Cerradura Positiva (Σ+)"] = simulator.positive_closure(current_alphabet, max_len)

        # Mostrar resultados en una tabla
        operations_output.controls.clear()
        data_rows = []
        
        for op_name, items in results.items():
            display_text = ", ".join(items) if items else "∅"
            data_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(op_name, weight="bold")),
                        ft.DataCell(ft.Text(display_text))
                    ]
                )
            )

        operations_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Operación", weight="bold")),
                ft.DataColumn(ft.Text("Resultado", weight="bold"))
            ],
            rows=data_rows,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5
        )
        
        operations_output.controls.append(operations_table)
        
        # Mostrar advertencia si se usó alfabeto temporal
        if not simulator.alphabet:
            output_text.value = f"Nota: Se usaron los caracteres '{', '.join(current_alphabet)}' como alfabeto."
            page.update()

    # ========== Funciones de Exportación e Importación ==========
    def export_automaton(e):
        """Exporta el autómata a formato .afd"""
        if not validate_automaton():
            page.update()
            return

        content = [
            f"Tipo: {'AFN' if simulator.is_nfa else 'AFD'}",
            f"Alfabeto: {','.join(simulator.alphabet)}",
            f"Estados: {','.join(simulator.states)}",
            f"Estado inicial: {simulator.initial_state}",
            f"Estados de aceptación: {','.join(simulator.accepting_states)}"
        ]
        
        for (state, symbol), destinations in simulator.transition_table.items():
            if simulator.is_nfa:
                content.append(f"Transición: {state},{symbol}->{','.join(destinations)}")
            else:
                content.append(f"Transición: {state},{symbol}->{destinations}")

        file_picker.save_file(
            allowed_extensions=["afd"],
            dialog_title="Guardar Autómata",
            file_name="automata.afd"
        )
        if file_picker.result:
            save_to_file(file_picker.result, "\n".join(content))

    def export_jff(e):
        """Exporta el autómata a formato JFLAP (.jff)"""
        if not validate_automaton():
            page.update()
            return

        root = ET.Element("structure")
        root.set("type", "fa")
        automaton = ET.SubElement(root, "automaton")
    
    # Crear estados
        state_ids = {state: str(i) for i, state in enumerate(simulator.states)}
        for state in simulator.states:
            state_elem = ET.SubElement(automaton, "state")
            state_elem.set("id", state_ids[state])
            state_elem.set("name", state)
        
        # Posición para visualización
            ET.SubElement(state_elem, "x").text = str(100 + 200 * (int(state_ids[state]) % 5))
            ET.SubElement(state_elem, "y").text = str(100 + 200 * (int(state_ids[state]) // 5))
        
            if state == simulator.initial_state:
                ET.SubElement(state_elem, "initial")
            if state in simulator.accepting_states:
                ET.SubElement(state_elem, "final")

    # Crear transiciones
        for (from_state, symbol), destinations in simulator.transition_table.items():
            if simulator.is_nfa:
                for dest in destinations:
                    trans_elem = ET.SubElement(automaton, "transition")
                    ET.SubElement(trans_elem, "from").text = state_ids[from_state]
                    ET.SubElement(trans_elem, "to").text = state_ids[dest]
                    read_elem = ET.SubElement(trans_elem, "read")
                    if symbol != "ε":
                        read_elem.text = symbol
            else:
                trans_elem = ET.SubElement(automaton, "transition")
                ET.SubElement(trans_elem, "from").text = state_ids[from_state]
                ET.SubElement(trans_elem, "to").text = state_ids[destinations]
                read_elem = ET.SubElement(trans_elem, "read")
                if symbol != "ε":
                    read_elem.text = symbol

    # Generar XML
        xml_str = ET.tostring(root, encoding="unicode")
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

        def save_jff_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, "w", encoding="utf-8") as file:
                        file.write(pretty_xml)
                    output_text.value = f"Archivo JFLAP guardado exitosamente en: {e.path}"
                except Exception as ex:
                    output_text.value = f"Error al guardar el archivo: {str(ex)}"
                page.update()

        file_picker.on_result = save_jff_result
        file_picker.save_file(
            allowed_extensions=["jff"],
            dialog_title="Guardar como JFLAP",
            file_name="automata.jff"
        )
        if file_picker.result:
            save_to_file(file_picker.result, pretty_xml)

    def import_afd(e):
        """Importa un autómata desde formato .afd"""
        def import_afd_result(e: ft.FilePickerResultEvent):
            if not e.files or len(e.files) == 0:
                return

            try:
                file_path = e.files[0].path
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

        # Reiniciar simulador
                simulator.alphabet = []
                simulator.states = []
                simulator.initial_state = None
                simulator.accepting_states = []
                simulator.transition_table = {}

                for line in lines:
                    line = line.strip()
                    if line.startswith("Tipo:"):
                        simulator.is_nfa = "AFN" in line
                        automaton_type.value = simulator.is_nfa
                    elif line.startswith("Alfabeto:"):
                        simulator.alphabet = line.split(":", 1)[1].strip().split(",")
                        alphabet_input.value = ",".join(simulator.alphabet)
                    elif line.startswith("Estados:"):
                        simulator.states = line.split(":", 1)[1].strip().split(",")
                        states_input.value = ",".join(simulator.states)
                    elif line.startswith("Estado inicial:"):
                        simulator.initial_state = line.split(":", 1)[1].strip()
                    elif line.startswith("Estados de aceptación:"):
                        simulator.accepting_states = line.split(":", 1)[1].strip().split(",")
                    elif line.startswith("Transición:"):
                # Formato: "Transición: estado,símbolo->destino1,destino2,..."
                        parts = line.split(":", 1)[1].strip().split("->")
                        src_parts = parts[0].strip().split(",")
                        state, symbol = src_parts[0], src_parts[1]
                        destinations = parts[1].strip().split(",")
                
                        if simulator.is_nfa:
                            simulator.transition_table[(state, symbol)] = destinations
                        else:
                            simulator.transition_table[(state, symbol)] = destinations[0]

        # Actualizar interfaz
                update_states(None)  # Recrear checkboxes
        
        # Actualizar opciones del dropdown del estado inicial
                initial_state_dropdown.options = [
                    ft.dropdown.Option(state) for state in simulator.states
                ]
                initial_state_dropdown.value = simulator.initial_state  # Asignar el estado inicial
        
        # Marcar estados de aceptación
                for checkbox in accepting_states_checkboxes.controls:
                    checkbox.value = checkbox.label in simulator.accepting_states
        
        # Actualizar tabla de transiciones y llenar celdas
                update_transition_table()
        
        # Definir automáticamente el autómata después de importar
                define_automaton(None)
        
                output_text.value = f"Autómata importado correctamente desde: {file_path}"
        
            except Exception as ex:
                output_text.value = f"Error al importar: {str(ex)}"
    
        page.update()

        file_picker.on_result = import_afd_result
        file_picker.pick_files(
            allowed_extensions=["afd"],
            dialog_title="Importar Autómata AFD/AFN"
        )

    def import_jff(e):
        """Importa un autómata desde formato JFLAP (.jff)"""
        def import_jff_result(e: ft.FilePickerResultEvent):
            if not e.files or len(e.files) == 0:
                return

            try:
                file_path = e.files[0].path
                tree = ET.parse(file_path)
                root = tree.getroot()
        
        # Reiniciar simulador
                simulator.alphabet = []
                simulator.states = []
                simulator.initial_state = None
                simulator.accepting_states = []
                simulator.transition_table = {}
                simulator.is_nfa = False  # Por defecto AFD

        # Mapa de ID a nombre de estado
                state_map = {}
                automaton = root.find(".//automaton")
        
        # Procesar estados
                for state_elem in automaton.findall("./state"):
                    state_id = state_elem.get("id")
                    state_name = state_elem.get("name") or state_id
                    state_map[state_id] = state_name
                    simulator.states.append(state_name)
            
                    if state_elem.find("./initial") is not None:
                        simulator.initial_state = state_name
            
                    if state_elem.find("./final") is not None:
                        simulator.accepting_states.append(state_name)
        
        # Recopilar alfabeto y transiciones
                symbols_set = set()
                for trans_elem in automaton.findall("./transition"):
                    from_id = trans_elem.find("from").text
                    to_id = trans_elem.find("to").text
                    from_state = state_map[from_id]
                    to_state = state_map[to_id]
            
                    symbol_elem = trans_elem.find("read")
                    symbol = symbol_elem.text if symbol_elem is not None and symbol_elem.text else "ε"
            
                    if symbol != "ε":
                        symbols_set.add(symbol)
            
            # Detectar si es AFN
                    key = (from_state, symbol)
                    if key in simulator.transition_table:
                        simulator.is_nfa = True
                        if isinstance(simulator.transition_table[key], list):
                            simulator.transition_table[key].append(to_state)
                        else:
                            simulator.transition_table[key] = [simulator.transition_table[key], to_state]
                    else:
                        simulator.transition_table[key] = to_state if not simulator.is_nfa else [to_state]
        
        # Convertir todas las transiciones a listas si es AFN
                simulator.alphabet = list(symbols_set)
                if simulator.is_nfa:
                    for key, value in list(simulator.transition_table.items()):
                        if not isinstance(value, list):
                            simulator.transition_table[key] = [value]
        
        # Actualizar interfaz
                automaton_type.value = simulator.is_nfa
                alphabet_input.value = ",".join(simulator.alphabet)
                states_input.value = ",".join(simulator.states)
        
                update_states(None)  # Recrear checkboxes
        
        # Actualizar opciones del dropdown del estado inicial
                initial_state_dropdown.options = [
                    ft.dropdown.Option(state) for state in simulator.states
                ]
                initial_state_dropdown.value = simulator.initial_state  # Asignar el estado inicial
        
        # Marcar estados de aceptación
                for checkbox in accepting_states_checkboxes.controls:
                    checkbox.value = checkbox.label in simulator.accepting_states
        
        # Actualizar tabla de transiciones
                update_transition_table()
        
        # Definir automáticamente el autómata después de importar
                define_automaton(None)
        
                output_text.value = f"Autómata importado correctamente desde: {file_path}"
        
            except Exception as ex:
                output_text.value = f"Error al importar: {str(ex)}"
    
            page.update()

        file_picker.on_result = import_jff_result
        file_picker.pick_files(
            allowed_extensions=["jff"],
            dialog_title="Importar Autómata JFLAP"
        )
    # Función para guardar archivos
    # Esta función se usa tanto para .afd como para .jff
    # Se puede mejorar para manejar diferentes tipos de archivos
    # y extensiones en el futuro

    def save_to_file(file_path: str, content: str):
        """Guarda contenido en un archivo"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            output_text.value = f"Archivo guardado exitosamente: {file_path}"
        except Exception as ex:
            output_text.value = f"Error al guardar: {str(ex)}"
        page.update()

    # ========== Botones y Controles ==========
    validate_button = ft.ElevatedButton(
        "Validar Cadena",
        icon=ft.icons.CHECK_CIRCLE,
        on_click=run_validation,
        width=200
    )
    
    step_by_step_button = ft.ElevatedButton(
        "Simulación Paso a Paso",
        icon=ft.icons.PLAY_ARROW,
        on_click=step_by_step_simulation,
        width=200
    )

    lambda_closure_button = ft.ElevatedButton(
        "Mostrar Clausura Lambda",
        icon=ft.icons.LAYERS,
        on_click=show_lambda_closure,
        width=200
    )
    
    export_afd_button = ft.ElevatedButton(
        "Exportar .afd",
        icon=ft.icons.SAVE,
        on_click=export_automaton,
        width=150
    )
    export_jff_button = ft.ElevatedButton(
        "Exportar JFLAP",
        icon=ft.icons.SAVE_ALT,
        on_click=export_jff,
        width=150
    )
    
    import_afd_button = ft.ElevatedButton(
        "Importar .afd",
        icon=ft.icons.UPLOAD_FILE,
        on_click=import_afd,
        width=150
    )
    
    import_jff_button = ft.ElevatedButton(
        "Importar JFLAP",
        icon=ft.icons.FOLDER_OPEN,
        on_click=import_jff,
        width=150
    )
    
    calculate_ops_button = ft.ElevatedButton(
        "Calcular Operaciones",
        icon=ft.icons.CALCULATE,
        on_click=calculate_operations,
        width=200
    )
    
    define_button = ft.ElevatedButton(
        "Definir Autómata",
        icon=ft.icons.DONE_ALL,
        on_click=define_automaton,
        width=200
    )
    
    # ========== Layout de la Interfaz ==========
    # Conectar eventos de cambios
    alphabet_input.on_change = update_alphabet
    states_input.on_change = update_states
    
    # Contenedor principal
    page.add(
        ft.Text("Simulador Avanzado de Autómatas Finitos", size=25, weight="bold"),
        ft.Divider(),
        
        # Sección de definición
        ft.Text("Definición del Autómata", size=18, weight="bold"),
        ft.Row([
            ft.Column([
                alphabet_input,
                states_input,
                initial_state_dropdown,
                automaton_type,
            ]),
            ft.Column([
                ft.Text("Estados de Aceptación:", weight="bold"),
                accepting_states_checkboxes,
                define_button
            ]),
        ]),
        
        ft.Divider(),
        
        # Tabla de transiciones
        ft.Text("Tabla de Transiciones", size=18, weight="bold"),
        transition_table_display,
        
        ft.Divider(),
        
        # Sección de validación
        ft.Text("Validación de Cadenas", size=18, weight="bold"),
        ft.Row([
            input_string,
            validate_button,
            step_by_step_button
        ]),
        ft.Container(
            content=simulation_output,
            border=ft.border.all(1, ft.colors.BLUE_200),
            border_radius=5,
            padding=10
        ),
        
        ft.Divider(),
        
        # Sección de operaciones
        ft.Text("Operaciones de Lenguaje", size=18, weight="bold"),
        ft.Row([
            operations_input,
            max_len_input,
            calculate_ops_button
        ]),
        operations_output,
        
        ft.Divider(),
        
        # Sección de importación/exportación
        ft.Text("Importar / Exportar", size=18, weight="bold"),
        ft.Row([
            export_afd_button,
            export_jff_button,
            import_afd_button,
            import_jff_button
        ]),
        
        # Área de salida para mensajes
        ft.Divider(),
        ft.Container(
            content=output_text,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5,
            padding=10
        )
    )

# Iniciar la aplicación
ft.app(main)