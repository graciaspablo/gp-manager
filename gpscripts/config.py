#CONFIGURACIÓN

#-------------------------GENERAL------------------------- #
PLAYER_NAMES = ['Joaquín', 'Anton', 'Sergio', 'Aitor', 'Diego', 'Miranda', 'Paula', 'Laura', 'Aina', 'Nerea']

#-------------------------GP-ENGINE------------------------#
#Guarda un .csv con todos los datos en out.csv
MAKE_CSV = True
#Procesa todos los días en busca de faltas
RUN_DAYS = True
#Muestra en la terminal los resultados de run_days()
PRINT_SUMMARY = False
#Procesa solamente el primer dia para testear cosas
ONLY_ONE_RUN = False

#-------------------------GAMEPLAY-------------------------#
#Permite que se guarden TODAS las faltas en un día, independientemente de
#que solo se pueda obtener una.
RECORD_ALL_FOULS = False



#-------------------------MENSAJES-------------------------#
#Mensajes sagrados que deben aparecer literalmente en el MBD + algunos 
#mensajes puntuales legales.
MENSAJES = [
    '¡Muy Buenos Días a Todos! Recuerden que para tener un día extraordinario es necesario hacer un gran esfuerzo ¡Que tengan una mañana tranquila y llena de oportunidades!',
    'Esta es la oportunidad para salir de tu zona de confort y tener un hermoso día, recuérdalo cuando las dificultades lleguen a ti y debas superarlas ¡Que tengan un buen día, amigos!',
    'Amigos míos, tengan presente que caemos para levantarnos, nunca se queden en el suelo ni se conformen con menos, este es un día para ser mejor que ayer. Que tengas el mejor día.',
    'Querida familia, oro para que este día sea asombroso para cada uno de ustedes, productivo y lleno de alegría y que en cada paso que den hoy nunca se apague la llama de sus sueños. Buenos días.',
    'Nos proponemos metas para cumplirlas, cada paso que damos es un nuevo objetivo, no dejes pasar un día sin trabajar por tus sueños. Es el amanecer de un nuevo día, reúne tus fuerzas para luchar, sonreír y experimentar la vida ¡Que tengas un gran día!',
    'Que tus sueños te mantengan fuerte y lleno de motivación, que sus metas hagan de esta una excelente mañana, no te olvides de celebrar y disfrutar de la vida, no te preocupes en exceso por el mañana, porque los cambios están a la orden del día.',
    'Cada nuevo día es una oportunidad para lograr más, para alcanzar nuevos sueños y perseguirlos sin cansancio. Mientras trabajas pueden practicar la gran sonrisa que tendrán en la cima ¡Disfruten de este día!',
    'Molt Bon dia a Tots! Recordin que per a tenir un dia extraordinari és necessari fer un gran esforç. Que tinguin un matí tranquil i ple d\'oportunitats!',
    'Aquesta és l\'oportunitat per a sortir de la teva zona de confort i tenir un bell dia, recorda\'l quan les dificultats arribin a tu i hagis de superar-les. Que tinguin un bon dia, amics!',
    'Amics meus, tinguin present que caiem per a aixecar-nos, mai es quedin en el sòl ni es conformin amb menys, aquest és un dia per a ser millor que ahir. Que tinguis el millor dia.',
    'Benvolguda família, or perquè aquest dia sigui sorprenent per a cadascun de vostès, productiu i ple d\'alegria i que en cada pas que donin avui mai s\'apagui la flama dels seus somnis. Bon dia.',
    'Ens proposem metes per a complir-les, cada pas que donem és un nou objectiu, no deixis passar un dia sense treballar pels teus somnis. És l\'alba d\'un nou dia, reuneix les teves forces per a lluitar, somriure i experimentar la vida. Que tinguis un gran dia!',
    'Que els teus somnis et mantinguin fort i ple de motivació, que les seves metes facin d\'aquesta un excel·lent matí, no t\'oblidis de celebrar i gaudir de la vida, no et preocupis en excés pel demà, perquè els canvis estan a l\'ordre del dia.',
    'Cada nou dia és una oportunitat per a aconseguir més, per a aconseguir nous somnis i perseguir-los sense cansament. Mentre treballes poden practicar el gran somriure que tindran en el cim. Gaudeixin d\'aquest dia!',
    'bondiarodalies😚😚\nA quina hora passa el tren de Sant Vicent de Calders🤨🤨 no puc esperar més😫😫\nNen, porto aquí mitja hora i això no ve saps😡😡'
]