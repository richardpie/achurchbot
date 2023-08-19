// Gramàtica per expressions senzilles
grammar lc;
root : terme             // l'etiqueta ja és root
     | definir_macro
     ;
terme : '('terme')' 			#parentesis
     |terme Operador terme		#operacion
     |terme terme 			#aplicacion
     |('\\' | 'λ') Letra+ ('.') terme	#abstraccion
     |Letra           			#letra
     |(Nombre_macro|Operador)		#macro    
     ;
definir_macro : (Nombre_macro|Operador) ('='| '≡') terme #defmacro
     ;
Letra : [a-z] ;
Nombre_macro : [A-Z][A-Z0-9]*;
Operador : ('/' | '*' | '+' | '-' );
WS  : [ \t\n\r]+ -> skip ;
