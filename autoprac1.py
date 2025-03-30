import flet as ft
from itertools import product

def subcadenas(cadena):
    return [cadena[i:j] for i in range(len(cadena)) for j in range(i + 1, len(cadena) + 1)]

def prefijos(cadena):
    return [cadena[:i] for i in range(1, len(cadena) + 1)]

def sufijos(cadena):
    return [cadena[i:] for i in range(len(cadena))]

def cerradura_kleene(alfabeto, max_len):
    return ["".join(p) for i in range(max_len + 1) for p in product(alfabeto, repeat=i)]

def cerradura_positiva(alfabeto, max_len):
    return ["".join(p) for i in range(1, max_len + 1) for p in product(alfabeto, repeat=i)]

def main(page: ft.Page):
    page.title = "Operaciones con Cadenas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    input_str = ft.TextField(label="Ingrese una cadena")
    input_alphabet = ft.TextField(label="Ingrese el alfabeto separado por comas")
    input_length = ft.TextField(label="Longitud máxima", keyboard_type=ft.KeyboardType.NUMBER)
    
    output_area = ft.Text()
    
    def calcular(_):
        cadena = input_str.value
        alfabeto = input_alphabet.value.split(",")
        max_len = int(input_length.value) if input_length.value.isdigit() else 0
        
        resultado = f"Subcadenas: {subcadenas(cadena)}\n"
        resultado += f"Prefijos: {prefijos(cadena)}\n"
        resultado += f"Sufijos: {sufijos(cadena)}\n"
        resultado += f"Cerradura de Kleene: {cerradura_kleene(alfabeto, max_len)}\n"
        resultado += f"Cerradura Positiva: {cerradura_positiva(alfabeto, max_len)}\n"
        
        output_area.value = resultado
        page.update()
    
    calcular_btn = ft.ElevatedButton("Calcular", on_click=calcular)
    
    def exportar(_):
        with open("resultados.txt", "w") as f:
            f.write(output_area.value)
        page.snack_bar = ft.SnackBar(ft.Text("Resultados guardados en 'resultados.txt'"))
        page.snack_bar.open = True
        page.update()
    
    export_btn = ft.ElevatedButton("Exportar", on_click=exportar)
    
    page.add(input_str, input_alphabet, input_length, calcular_btn, output_area, export_btn)

ft.app(target=main)