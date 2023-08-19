# Bienvenido a AChurchBot!

En este programa podras realizar evaluaciones de expresiones en lambda cálculo.

Incluye un archivo *achurch.py* en el que tenemos un bot de telegram con el que nos podemos comunicar via mensaje y contesta con las operaciones y los gráficos que lleva a cabo.

Incluye un archivo *achurch_terminal.py* en el que podemos ejecutar el evaluador de forma local (con el terminal), hacer las mismas evaluaciones pero sin la parte gráfica y con un formato de salida de las operaciones es diferent.

Y por último incluye el archivo *lc.g4* que contiene la gramática.

# Cómo instalar

Para poder hacer uso del bot primero debemos instalar en nuestro pc los siguientes elementos:

* antlr4 (se aconseja la version 1.12):
```
    pip install antlr4-tools
    pip install antlr4-python3-runtime
```

* python-telegram-bot:
```
    pip install python-telegram-bot
```
* pydot
```
    pip install pydot
    sudo apt install graphviz
```

# Uso

Poner los archivos en la misma carpeta y ejecutar: 
* antlr4 -Dlanguage=Python3 -no-listener lc.g4
* antlr4 -Dlanguage=Python3 -no-listener -visitor lc.g4

Ejecutar el archivo que se desea:

* Bot (version aconsejada):

Introducid "python3 achurch.py" en el terminal para iniciar el bot.


A partir de aquí todo el input se realizar mediante mensajes de telegram con el bot.

Si introducimos texto realizará la evaluación de la expresión que hemos introducido y también mostrará un grafico con el arbol de la expresion.

(EN EL RARO CASO DE QUE LA IMAGEN DEL GRÁFICO NO CARGUE, REFRESCAD LA PÁGINA DE TELEGRAM)

Para introducir macros podemos seguir el siguiente formato: 
NOMBRE = (\parametros.expresion) 
y para introducir una expresion a evaluar este:
(\parametros.expresion)

Si queremos saber acerca de los comandos que podemos utilizar en el bot solo tenemos que enviar un mensaje con /help.


* Terminal:

Poned los archivos en la misma carpeta y ejecutar con "python3 achurch_terminal.py" en el terminal para iniciar el evaluador.

A continuación introducimos las expresiones que queremos evaluar;


Con el formato:

NOMBRE = (\parametros.expresion), obtendremos una macro

Y con el formato:

(\parametros.expresion) se realizaran todas las operaciones (beta reduccion y alfa conversion) sobre la expresion introducida hasta llegar al resultado final.

# Acceso al bot

Para poder hacer uso del código en "formato bot" tienes que primero crear un bot de telegram con @botfather, es un proceso sencillo.

Cuando lo hayas creado copia el token en esta linea de código que encontraras en el achurch.py:

app = Application.builder().token(
    " ").build() #Introduce el token que te ha dado el botfather entre las comillas


# Autor

Richard Pie Sánchez. 06/2023

