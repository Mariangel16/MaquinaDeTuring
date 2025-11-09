# MaquinaDeTuring
Este proyecto implementa un simulador **visual e interactivo** de una Máquina de Turing en **Python 3 (Tkinter)**.
Permite cargar una máquina de ejemplo, **ejecutar paso a paso o automáticamente**, visualizar la **cinta**, el **cabezal** y el **estado actual**. Además, incluye un módulo para **probar 10 expresiones regulares** con `re.fullmatch` y mostrar aceptación/rechazo.

## Requisitos
- Python (Tkinter ya viene con muchas instalaciones de Python)
- Visual studio

## Instalación y ejecución
> En Windows, puede bastar con doble clic si `.py` está asociado a Python.
> Tambien se puede abrir el archivo .py en visual studio y ejecutar el programa.

## Características
- Interfaz gráfica con **Tkinter**
- Dos **máquinas de ejemplo** incluidas:
  - `0*1*`
  - `(ab)*`
- **Controles**: *Cargar*, *Reset*, *Paso*, *Auto* con control de velocidad
- **Cinta** desplazable, con celda resaltada en la posición del cabezal
- Panel de **expresiones regulares** con 10 patrones y descripción breve

## Cómo probar
1. Escriba una cadena de entrada en el campo **Cadena de entrada**.
2. Seleccione una máquina (`0*1*` o `(ab)*`) y pulse **Cargar Máquina**.
3. Use **Paso** para avanzar paso a paso o **Auto** para ejecutar automáticamente.
4. Observe el **Estado** y el **Resultado** (aceptada/rechazada).
5. En la sección **Pruebas con Expresiones Regulares**, seleccione un patrón y pulse **Probar Regex** para comprobar la cadena actual.
