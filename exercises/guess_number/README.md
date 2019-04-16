Adivinar Número
------------------------

**Reglas**:
Python 3.5+

**Problema**:

Estamos pensando en un entero P dentro del rango (A, B], es decir, A <P ≤ B. Usted tiene N intentos para adivinar el número. Después de cada suposición que no sea correcta, le diremos si P es mayor o inferior a su conjetura.

**Entrada y salida**
Toda la información entra en su programa a través de entrada estándar; Todo lo que necesite para comunicarse debe enviarse a través de una salida estándar. Recuerde que muchos lenguajes de programación almacenan en búfer la salida por defecto, así que asegúrese de que su salida realmente se apague (por ejemplo, vaciando el búfer) antes de bloquear para esperar una respuesta. 

Inicialmente, su programa debería leer una sola línea que contenga un solo entero T que indique el número de casos de prueba. Entonces, necesitas procesar T casos de prueba.

Para cada caso de prueba, su programa leerá una sola línea con dos enteros A y B, que representan el límite inferior exclusivo y el límite superior inclusivo, como se describió anteriormente. En la siguiente línea, leerá un solo entero N, que representa el número máximo de adivinanzas que puede hacer. Su programa procesará hasta N intercambios con nuestro juez.

Para cada intercambio, su programa necesita usar la salida estándar para enviar una sola línea con un entero Q: su conjetura. En respuesta a su adivinanza, el juez imprimirá una sola línea con una palabra en su flujo de entrada, que su programa debe leer a través de la entrada estándar. La palabra será CORRECTA si su suposición es correcta, TOO_SMALL si su suposición es menor que la respuesta correcta, y TOO_BIG si su suposición es mayor que la respuesta correcta. Entonces, puedes comenzar otro intercambio.

Si su programa tiene algo incorrecto (por ejemplo, formato de salida incorrecto o valores fuera de límites), el juez enviará WRONG_ANSWER a su flujo de entrada y no enviará ninguna otra salida después de eso. Tenga en cuenta que es su responsabilidad hacer que su programa salga a tiempo para recibir el veredicto apropiado (Respuesta incorrecta, Error de tiempo de ejecución, etc.)

Si su caso de prueba se resuelve dentro de N intentos, recibirá el mensaje CORRECTO del juez, como se mencionó anteriormente, y luego continuará recibiendo la entrada (una nueva línea con dos enteros A y B, etc.) para el siguiente caso de prueba. Después de N intentos, si el caso de prueba no se resuelve, el juez imprimirá WRONG_ANSWER y luego dejará de enviar la salida a su flujo de entrada.

No debe enviar información adicional al juez después de resolver todos los casos de prueba. En otras palabras, si su programa continúa imprimiendo en la salida estándar después de recibir CORRECTO para el último caso de prueba, obtendrá un fallo de Respuesta incorrecta.

**Límites**
1 ≤ T ≤ 20.
A = 0. N = 30.
Límite de tiempo: 10 segundos por conjunto de prueba.

Conjunto de prueba 1
B = 30.

El pseudocódigo primero lee un entero t, que representa el número de casos de prueba. Entonces comienza el primer caso de prueba. Supongamos que la respuesta correcta P es 9 para el primer caso de prueba. El pseudocódigo lee primero tres enteros a, b y n, que representan el rango de adivinación y el número máximo de intentos, respectivamente, y luego genera una adivinanza: 30. Dado que 30 es mayor que 9, la cadena TOO_BIG se recibe del juez a través de la entrada estándar. Luego, el pseudocódigo adivina 5 y recibe TOO_SMALL en respuesta. La respuesta 10 se imprime posteriormente en la salida estándar, que de nuevo es demasiado grande. Finalmente, el pseudocódigo adivina 9 y recibe CORRECTO porque 9 es la respuesta correcta.

**Caso de Prueba**
2            # T Número de casos
1  15        # A y B, cota inferior y cota superior. En notación de intervalo sería: (1, 30]
5		     # N, Número de intentos posibles para adivinar el número 7
8		     # Primera respuesta del programa
TOO_BIG      # Respuesta del juez
5		     # Segundo Intento del programa por adivinar
TOO_SMALL    # Respuesta del programa
7		     # Tercer intento del programa
CORRECT      # Respuesta del juez, el programa pasa al siguiente caso
2 6 	     # Input del juez, (A,B]
2		     # Número de intentos posibles para adivinar el número 5
1            # Primera respuesta del programa
TOO_SMALL    # Respuesta del juez
4            # Primera respuesta del programa
WRONG_ANSWER # Respuesta del juez

**Contribuciones**
-----------------------

All work to improve performance is good

Enjoy it!