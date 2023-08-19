from __future__ import annotations
from antlr4 import *
from lcLexer import lcLexer
from lcParser import lcParser
from lcVisitor import lcVisitor
from dataclasses import dataclass
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import pydot

# Arbol Semántico


@dataclass
class Vacio:
    pass


@dataclass
class Aplicacion:
    left: terme
    right: terme


@dataclass
class Abstraccion:
    parametres: str
    sub_terme: terme


@dataclass
class Letra:
    letra: str


terme = Letra | Abstraccion | Aplicacion | Vacio

macros_dict = {}


def variablesPosibles(var_usadas):

    # Genera un set con las variables posibles por las que podemos sustituir para hacer la 
    #alfa reducción

    abecedario = set(string.ascii_lowercase)
    return abecedario - var_usadas


def extractVariablesArbolDerecha(terme):

    # Obtenemos las variables del termino de la derecha y lo añadimos al set de variables

    set_variables_right = set()
    if isinstance(terme, Abstraccion):
        set_variables_right.update(
            extractVariablesArbolDerecha(terme.sub_terme))
    elif isinstance(terme, Aplicacion):
        set_variables_right.update(extractVariablesArbolDerecha(terme.left))
        set_variables_right.update(extractVariablesArbolDerecha(terme.right))

    elif isinstance(terme, Letra):
        set_variables_right.add(terme.letra)

    return set_variables_right


def extractVariablesLigadas(terme):

    # Obtenemos las variables ligadas del termino de la izquierda y las metemos en un set

    set_variables_left = set()
    if isinstance(terme, Abstraccion):
        set_variables_left.add(terme.parametres)
        set_variables_left.update(extractVariablesLigadas(terme.sub_terme))
    elif isinstance(terme, Aplicacion):
        set_variables_left.update(extractVariablesLigadas(terme.left))
        set_variables_left.update(extractVariablesLigadas(terme.right))
    return set_variables_left


def extractVariablesLibres(terme):

    # Hacemos una diferencia de conjuntos para obtener la variable

    set_variables_ligadas_izq = extractVariablesLigadas(terme)
    set_variables_libres_drch = extractVariablesArbolDerecha(terme)

    variables_libres = set_variables_libres_drch - set_variables_ligadas_izq
    return variables_libres


def sustituir_variable_en_terme(terme, variable, new_variable):

    # Sustituimos la variables y sus apariciones en la expresion por la variable 
    #"new_variable"

    if isinstance(terme, Aplicacion):
        left = sustituir_variable_en_terme(terme.left, variable, new_variable)
        right = terme.right
        return Aplicacion(left, right)

    elif isinstance(terme, Abstraccion):
        parametres = terme.parametres.replace(variable, new_variable)
        sub_terme = sustituir_variable_en_terme(
            terme.sub_terme, variable, new_variable)
        return Abstraccion(parametres, sub_terme)

    elif isinstance(terme, Letra):
        letra = terme.letra.replace(variable, new_variable)
        return Letra(letra)

    else:
        return terme


def alfa_conversion(terme, list_reductions):

    # Comprobamos si es necesaria una alfa conversion y si lo es, la llevamos a cabo

    var_left = extractVariablesLigadas(terme.left)
    var_right = extractVariablesLibres(terme.right)

    set_para_sustituir = var_left.intersection(var_right)
    set_posible = set()

    new_terme = terme
    if len(set_para_sustituir) != 0:

        # Si existen variables que provocan conlisión, iniciamos la sustitución

        set_posible = variablesPosibles(var_left.union(var_right))

        for var in set_para_sustituir:

            # Elegimos una variable aleatoria y la sustiuimos por la variable que provoca la 
            #colisión
            # Luego lo ponemos en formato string y lo metemos en la lista de reducciones

            new_var = random.choice(list(set_posible))
            new_terme = sustituir_variable_en_terme(terme, var, new_var)

            original_terme_string = terme_to_string(terme.left)
            mod_terme_string = terme_to_string(new_terme.left)
            list_reductions.append(
                original_terme_string + ' → ' + "α" + ' → ' + original_terme_string)

    return new_terme


def terme_to_string(terme):

    # Convertimos el terme en una string

    list_to_print = []
    match terme:
        case Aplicacion(left, right):
            list_to_print.append('(')
            list_to_print.extend(terme_to_string(left))
            list_to_print.extend(terme_to_string(right))
            list_to_print.append(')')
        case Abstraccion(parametres, sub_terme):
            list_to_print.append('(')
            list_to_print.extend('λ' + parametres + '.')
            list_to_print.extend(terme_to_string(sub_terme))
            list_to_print.append(')')

        case Letra(letra):
            list_to_print.append(letra)

    return "".join(list_to_print)


def sustitucion(sub_terme, parametres, right):

    # Hacemos la sustitución de la letra por el parametro right
    # (en caso de que el sub_terme sea una letra hacemos llamadas recursivas

    match sub_terme:
        case Abstraccion(p, t):

            new_sub_terme = sustitucion(t, parametres, right)
            return Abstraccion(p, new_sub_terme)

        case Aplicacion(left, r):
            new_left = sustitucion(left, parametres, right)
            new_right = sustitucion(r, parametres, right)
            return Aplicacion(new_left, new_right)
        case Letra(letra):
            if letra == parametres:
                return right
            else:
                return sub_terme


def b_reduction(terme, list_reductions):

    # Llevamos a cabo la beta reduccion

    match terme:

        case Aplicacion(left, right):
            new_terme = alfa_conversion(terme, list_reductions)

            if isinstance(left, Abstraccion):

                # Realizamos la conversion de los terminos si tenemos una abstraccion a la 
                #izquierda

                terme_result = sustitucion(
                    new_terme.left.sub_terme, new_terme.left.parametres, right)

                # Convertimos los terminos a strings y lo guardamos en la lista de reducciones

                original_terme_string = terme_to_string(new_terme)
                mod_terme_string = terme_to_string(terme_result)

                string_to_list = original_terme_string + \
                    ' → ' + ' β ' + ' → ' + mod_terme_string

                list_reductions.append(string_to_list)

                return b_reduction(terme_result, list_reductions)

            else:
                new_left = b_reduction(left, list_reductions)
                new_right = b_reduction(right, list_reductions)
                return Aplicacion(new_left, new_right)

        case Abstraccion(parametres, sub_terme):
            new_sub_terme = b_reduction(sub_terme, list_reductions)
            return Abstraccion(parametres, new_sub_terme)

        case Letra(letra):
            return terme


class TreeVisitor(lcVisitor):

    # Visitor
    def __init__(self):
        self.nivell = 0
        self.variables_disponibles = set()

    def visitParentesis(self, ctx):
        [_, terme, _] = list(ctx.getChildren())
        return self.visit(terme)

    def visitLetra(self, ctx):
        [letra] = list(ctx.getChildren())
        return Letra(letra.getText())

    def visitAplicacion(self, ctx):
        [terme1, terme2] = list(ctx.getChildren())
        t1 = self.visit(terme1)
        t2 = self.visit(terme2)
        return Aplicacion(t1, t2)

    def visitAbstraccion(self, ctx):

        parametres = ctx.Letra()
        terme = ctx.terme()
        t1 = self.visit(terme)
        l = "".join(reversed([parametres[i].getText()
                    for i in range(len(parametres))]))
        for elem in l:
            t1 = Abstraccion(elem, t1)
        return t1

    def visitDefmacro(self, ctx):
        [Nombre_macro, simbolo, terme] = list(ctx.getChildren())

        macros_dict[Nombre_macro.getText()] = self.visit(terme)

        return Vacio

    def visitMacro(self, ctx):
        [Nombre_macro] = list(ctx.getChildren())

        return macros_dict[Nombre_macro.getText()]

    def visitOperacion(self, ctx):
        [terme1, operador, terme2] = list(ctx.getChildren())
        t1 = self.visit(terme1)
        t2 = self.visit(terme2)
        return Aplicacion(Aplicacion(macros_dict[operador.getText()], t1), t2)
        return t1


def build_image_process(terme, graph, lista_nodos, identificador):

    match terme:
        case Aplicacion(left, right):

            # El identificador cómo string ha sido la solución que he encontrado para cree el 
            #gráfico sin ningun fallo (se han probado otras que funcionaban bien pero
            # alguna vez daba un grafo ligeramente incorrecto, como por ejemplo id(terme))

            id = identificador + "1"
            node = pydot.Node(id, label="@", penwidth=0)
            graph.add_node(node)

            graph.add_edge(pydot.Edge(
                id, build_image_process(left, graph, lista_nodos, id+"1")))

            graph.add_edge(pydot.Edge(
                id, build_image_process(right, graph, lista_nodos, id+"2")))

            return id

        case Abstraccion(parametres, sub_terme):

            id = identificador + "1"
            node = pydot.Node(id, label="λ" + parametres, penwidth=0)
            graph.add_node(node)

            lista_nodos.append(node)

            pos = len(lista_nodos) - 1

            # Si el termino es una abstraccion guardamos los parametros en una lista para 
            #luego crear las lineas discontinuas que expresan a que abstraccion está ligada 
            #(en el case Letra se entiende mejor esto)

            graph.add_edge(pydot.Edge(
                id, build_image_process(sub_terme, graph, lista_nodos, id)))

            # Cuando salimos de este nivel de recursion, borramos el nodo de la lista para si 
            # existe una variable igual en otra abstraccion que visitemos en un futuro, las 
            # lineas discontinuas no
            # apunten en diferentes direcciones ya que habría varios nodos en la lista que 
            # tendrian el mismo label

            if lista_nodos[pos] == node:
                del lista_nodos[pos]

            return id

        case Letra(letra):
            id = identificador + "1"
            node = pydot.Node(id, label=letra, penwidth=0)
            graph.add_node(node)

            # Creamos una linea discontinua entre la letra y la abstraccion a la que está 
            #ligada

            for elem in lista_nodos:

                # Comparamos si la letra de este nodo ya se encuentra en la lista de 
                #abstracciones que hemos recorrido para llegar aquí, si es asi, se traza una 
                #linea entre ambos nodos.

                if elem.get_label()[1] == letra:
                    edge = pydot.Edge(node, elem)
                    edge.set_style("dashed")
                    edge.set_color("blue")

                    graph.add_edge(edge)

            return id


def build_image(terme):

    # Creamos el grafico

    graph = pydot.Dot(graph_type='digraph')
    lista_nodos = []
    id_level = ""
    build_image_process(terme, graph, lista_nodos, id_level)
    graph.write_png('Graph.png')


async def executeLambda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Parte principal del programa

    input_stream = InputStream(update.message.text)
    lexer = lcLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = lcParser(token_stream)
    tree = parser.root()

    if parser.getNumberOfSyntaxErrors() == 0:
        visitor = TreeVisitor()

        terme = visitor.visit(tree)

        if (not terme == Vacio):

            try:

                stop = False
                terme_beta = terme
                list_reductions = []
                while not stop:

                    aux = b_reduction(terme_beta, list_reductions)

                    aux_string = terme_to_string(aux)

                    terme_beta_string = terme_to_string(terme_beta)

                    if len(aux_string) == len(terme_beta_string):
                        stop = True

                    terme_beta = aux

                arbre_message = "Arbre:\n" + terme_to_string(terme)
                await update.message.reply_text(arbre_message)
                graph_to_print = build_image(terme)

                await update.message.reply_photo("Graph.png")

                for elem in list_reductions:
                    await update.message.reply_text(elem)

                graph_to_print = build_image(terme_beta)

                await update.message.reply_photo("Graph.png")

                l_result = "Resultat:\n" + terme_to_string(terme_beta)
                await update.message.reply_text(l_result)

            except RecursionError:

                # En caso de que se cree una recursion infita salta esta excepcion en la cual 
                #imprimimos las primeras 15 beta reducciones (se realizan más pero usamos este 
                #cantidad de forma
                # arbitraria) y a continuación imprimimos "Nothing" para mostrar que no se ha 
                #llegado a ningun resultado

                aux_list_reductions = list_reductions[:15]
                for elem in aux_list_reductions:
                    await update.message.reply_text(elem)
                l_nothing = "Resultat:\n" + "Nothing"
                await update.message.reply_text(l_nothing)

    else:
        print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
        print(tree.toStringTree(recog=parser))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user
    message = "Hola " + user.mention_html() + "!\nBienvenido a AChurch_LambdaBot!"
    await update.message.reply_html(message)


async def macros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    message = ""

    for key, value in macros_dict.items():

        message += key + " ≡ " + terme_to_string(value) + "\n"

    await update.message.reply_text(message)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    message = "/start\n" + "/author\n" + "/help\n" + \
        "/macros\n" + "Expresión en λ-Cálculo"
    await update.message.reply_text(message)


async def author(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "AChurch_LambdaBot!\n" + "@ Richard Pie Sánchez. 2023"
    await update.message.reply_text(message)


app = Application.builder().token(
    " ").build() #Introduce el token que te ha dado el botfather entre las comillas


app.add_handler(CommandHandler("macros", macros))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("author", author))


app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, executeLambda))


app.run_polling()
