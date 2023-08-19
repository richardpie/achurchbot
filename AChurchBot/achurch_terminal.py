from __future__ import annotations
from antlr4 import *
from lcLexer import lcLexer
from lcParser import lcParser
from lcVisitor import lcVisitor
from dataclasses import dataclass
import random
import string


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

    # Genera un set con las variables posibles por las que podemos sustituir para hacer la alfa reducción

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

    # Sustituimos la variables y sus apariciones en la expresion por la variable "new_variable"

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

            # Elegimos una variable aleatoria y la sustiuimos por la variable que provoca la colisión
            # Luego lo ponemos en formato string y lo metemos en la lista de reducciones

            new_var = random.choice(list(set_posible))
            new_terme = sustituir_variable_en_terme(terme, var, new_var)

            original_terme_string = terme_to_string(terme.left)
            mod_terme_string = terme_to_string(new_terme.left)
            list_reductions.append("α-conversió: " + var + ' → ' + new_var + "\n" +
                                   original_terme_string + ' → ' + original_terme_string)

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
                # izquierda

                terme_result = sustitucion(
                    new_terme.left.sub_terme, new_terme.left.parametres, right)

                # Convertimos los terminos a strings y lo guardamos en la lista de reducciones

                original_terme_string = terme_to_string(new_terme)
                mod_terme_string = terme_to_string(terme_result)

                string_to_list = "β-reducció:\n" + original_terme_string + ' → ' + mod_terme_string

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


while True:

    input_stream = InputStream(input('? '))
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
                print(arbre_message)

                for elem in list_reductions:
                    print(elem)

                l_result = "Resultat:\n" + terme_to_string(terme_beta)
                print(l_result)

            except RecursionError:

                # En caso de que se cree una recursion infita salta esta excepcion en la cual
                # imprimimos las primeras 15 beta reducciones (se realizan más pero usamos este
                # cantidad de forma
                # arbitraria) y a continuación imprimimos "Nothing" para mostrar que no se ha
                # llegado a ningun resultado

                aux_list_reductions = list_reductions[:15]
                for elem in aux_list_reductions:
                    print(elem)
                l_nothing = "Resultat:\n" + "Nothing"
                print(l_nothing)

        else:
            for key, value in macros_dict.items():
                print(key + " ≡ " + terme_to_string(value))

    else:
        print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
        print(tree.toStringTree(recog=parser))
