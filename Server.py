import bottle
import json

from bottle import route, run, response, get, delete, put, post

goBack = """</br><form action="/database/main" method="post">
    <button type="submit" formmethod="post">Go back to previous page</button>
    </form>
    """
####################################################################################
#                                   GET                                            #
####################################################################################
@get("/show/all/<a>") #Le <a> permet de prendre la valeur et de l'utiliser plus bas (Donne toutes les donnée dont la valeur est a)
def showAll(a) :
    data = json.loads(open("students.json").read())
    datafinal = list()

    if("Name" in a):
        for x in range(0, len(data)):
            datafinal.append(data[x][a])

    else:
        for x in range(0, len(data)):
            datafinal.append("The value of " + str(a) + " for "+ str(data[x]["Name"]) + " is : "+ str(data[x][a])) #On doit convertir en str sinon ca peut renvoyer des int, ce que bottle n'aime pas afficher 

    dataformatter = '<br/><br/>'.join(map(str, datafinal))#Permet de convertire la list en une chaine caractere
    return dataformatter

@get("/show/all")#A COMPLETER OU ENLEVER
def showDB():

    data = json.loads(open("students.json").read())
    return data


@get("/show/everything/<name>") #Donne toutes les informations de la personne Name
def showEverything(name) :
    data = json.loads(open("students.json").read())

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            return data[x]

    response.status = 404
    return 'Name not found'

@get("/showRowNumber/<value>/<name>") #Pour avoir le row number de la personne ayant comme ID(value), 3(name) (exemple)
def showRowNumber(value, name) :
    data = json.loads(open("students.json").read())
    datafinal = list()

    for x in range(0, len(data)):
        if(name in data[x][value]):
            return str(x) #Il faut convertir x en character sinon bottle n'arrive pas a afficher le resultat

    response.status = 404
    return name +' not found'

@get("/count/all/<name>")#Retourne le nombre d'etudiants avec le meme nom name
def count(name):
    data = json.loads(open("students.json").read())
    count = 0

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            count = count + 1

    return str(count) #Erreur si on renvoi un int, donc on convertie en str

####################################################################################
#                                   GET(to launch other verbs)                     #
####################################################################################
@route("/student/add", method=['GET', 'POST'])
def getAdd() :
    formulaireStudentAdd = """
    <form method='post' action='/student/add/results'>
    <input type='text'  name='name' placeholder='Name'/>
    <input type='submit' value='Validez !'/>
    </form>
    """
    return formulaireStudentAdd

@get("/student/modify/<number>/<value>/<new>") #Pour modifier la valeur Value de new dans le row number
def getModify(number, value, new) :
    return modify(number, value, new)

@get("/student/remove/<name>") #Efface toutes les informations de <name>
def getDelete(name) :
    return delete(name)
####################################################################################
#                                   POST                                           #
####################################################################################
@post("/student/add/results") #Rajoute un nouvel utilisateur
def add() :
    name = bottle.request.forms.get('name')
    data = json.loads(open("students.json").read())

    modele = {
    "ID": (len(data)+1),
    "Name": name,
    "Gender": "0",
    "Class": "0",
    "Seat": "0",
    "Club": "0",
    "Student ID": "0",
    "Phone Number": "0",
    "GPA": "0",
    "Strength": "0",
    "Hairstyle": "0",
    "Color": "0",
    "Eyes": "0",
    "EyeType": "0",
    "Random data": "0",
    "Accessory": "0",
    "ScheduleTime": "0",
    "ScheduleDestination": "0",
    "ScheduleAction": "0",
    "Info": "0"
    }

    with open('students.json') as f:
        data = json.load(f)

    data.append(modele)

    with open('students.json', 'w') as f:
        json.dump(data, f)

    return 'Added ' + name, goBack

####################################################################################
#                                   PUT                                            #
####################################################################################
@put("/student/modify/<number>/<value>/<new>") #Pour modifier la valeur Value a New dans le row Number
def modify(number, value, new) :
    
    jsonFile = open("students.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    if(int(number) > len(data)):
        response.status = 404
        return "Row "+number+" not found"

    data[int(number)][value] = new

    jsonFile = open("students.json", "w")
    json.dump(data, jsonFile)
    jsonFile.close()
    return value + " has been successfully changed to "+new

####################################################################################
#                                   DELETE                                         #
####################################################################################
@delete("/student/remove/<name>") #Efface toutes les informations de <name>
def delete(name) :

    jsonFile = open("students.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            del data[x]
            temp = x
            break
        if(x == (len(data)-1)):
            response.status = 404
            return name +' not found'
    
    for x in range(temp, len(data)):
        data[x]["ID"] = x+1
    jsonFile = open("students.json", "w")
    json.dump(data, jsonFile)
    jsonFile.close()
    return 'All the informations related to '+name+' has been deleted'


####################################################################################
#                                   Main                                           #
####################################################################################
@route("/database/main", method=['GET', 'POST'])
def mainHTML():

    formulaire = """
    <form action="/show/all" method="post">
    <button type="submit" formmethod="post">Donne toutes les donées de la valeur entré</button>
    </form>

    <form action="/show/everything" method="post">
    <button type="submit" formmethod="post">Pour donnée toutes les informations de l'etudiant</button>
    </form>

    <form action="/showRowNumber" method="post">
    <button type="submit" formmethod="post">Pour chercher le row number</button>
    </form>

    <form action="/count/all" method="post">
    <button type="submit" formmethod="post">Pour compter le nombre d'etudiant ayant le meme nom</button>
    </form>

    <form action="/student/add" method="post">
    <button type="submit" formmethod="post">Rajoute un nouvel etudiant</button>
    </form>

    <form action="/student/modify" method="post">
    <button type="submit" formmethod="post">Pour modifier la valeur d'une case d'un etudiant</button>
    </form>

    <form action="/student/remove" method="post">
    <button type="submit" formmethod="post">Pour effacer un etudiant</button>
    </form>
    """
    

    formatt = "<h1 style=color:green;>::Server.py:: Choisir l'option desirer</h1>"
    
    return formatt + formulaire


@post("/show/all") #Pour enlever un etudiant via "GUI"
def postShowALL():

    a = bottle.request.forms.get('a')
    if(a is None):
        formulaireshowAll = """
        <form  action="/show/all" method='post'>
        <input type='text'  name='a' placeholder='Choisir une valeur dans la liste a afficher'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        informationPossible = """
        <ul>
        <li>ID</li>
        <li>Name</li>
        <li>Gender</li>
        <li>Class</li>
        <li>Seat</li>
        <li>Club</li>
        <li>Student ID</li>
        <li>Phone Number</li>
        <li>GPA</li>
        <li>Strength</li>
        <li>Color</li>
        <li>Eyes</li>
        <li>EyeType</li>
        <li>Random Data</li>
        <li>Accessory</li>
        <li>ScheduleTime</li>
        <li>ScheduleDestination</li>
        <li>ScheduleAction</li>
        <li>Info</li>
        <li>Hairstyle</li>
        </ul>
        """
        return formulaireshowAll, informationPossible
    else:
        return showAll(a), goBack


@post("/show/everything")
def postShowEverything():

    name = bottle.request.forms.get('name')
    if(name is None):
        formulaireShowEverything = """
        <form  action="/show/everything" method='post'>
        <input type='text'  name='name' placeholder='Name'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireShowEverything
    else:
        return showEverything(name), goBack


@post("/showRowNumber")
def postShowRowNumber():

    value = bottle.request.forms.get('value')
    name = bottle.request.forms.get('name')
    if(name is None): #Pas Besoin de tester les deux valeur, si une a changer, l'autre a forcement changer
        formulaireShowRowNumber = """
        <form  action="/showRowNumber" method='post'>
        <input type='text'  name='value' placeholder='La valeur'/>
        <input type='text'  name='name' placeholder='Name'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        informationPossible = """
        <ul>
        <li>ID</li>
        <li>Name</li>
        <li>Gender</li>
        <li>Class</li>
        <li>Seat</li>
        <li>Club</li>
        <li>Student ID</li>
        <li>Phone Number</li>
        <li>GPA</li>
        <li>Strength</li>
        <li>Color</li>
        <li>Eyes</li>
        <li>EyeType</li>
        <li>Random Data</li>
        <li>Accessory</li>
        <li>ScheduleTime</li>
        <li>ScheduleDestination</li>
        <li>ScheduleAction</li>
        <li>Info</li>
        <li>Hairstyle</li>
        </ul>
        """
        return formulaireShowRowNumber, informationPossible
    else:
        return showRowNumber(value, name), goBack

@post("/count/all")
def postCountAll():

    name = bottle.request.forms.get('name')
    if(name is None):
        formulaireCountAll = """
        <form  action="/count/all" method='post'>
        <input type='text'  name='name' placeholder='Le nom de l'etudiant/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireCountAll
    else:
        return count(name), goBack

@post("/student/modify")
def postREMOVE():

    number = bottle.request.forms.get('number')
    value = bottle.request.forms.get('value')
    new = bottle.request.forms.get('new')

    if(number is None):
        formulaireModify = """
        <form  action="/student/modify" method='post'>
        <input type='text'  name='number' placeholder='Number'/>
        <input type='text'  name='value' placeholder='Value'/>
        <input type='text'  name='new' placeholder='New'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        informationPossible = """
        <ul>
        <li>ID</li>
        <li>Name</li>
        <li>Gender</li>
        <li>Class</li>
        <li>Seat</li>
        <li>Club</li>
        <li>Student ID</li>
        <li>Phone Number</li>
        <li>GPA</li>
        <li>Strength</li>
        <li>Color</li>
        <li>Eyes</li>
        <li>EyeType</li>
        <li>Random Data</li>
        <li>Accessory</li>
        <li>ScheduleTime</li>
        <li>ScheduleDestination</li>
        <li>ScheduleAction</li>
        <li>Info</li>
        <li>Hairstyle</li>
        </ul>
        """
        return formulaireModify, informationPossible
    else:
        return modify(name), getBack

@post("/student/remove")
def postREMOVE():

    name = bottle.request.forms.get('name')
    if(name is None):
        formulaireStudentAdd = """
        <form  action="/student/remove" method='post'>
        <input type='text'  name='name' placeholder='Name'/>
        <input type='submit' value='Validez !'/>
        </form>
        """
        return formulaireStudentAdd
    else:
        return delete(name), goBack

bottle.run(bottle.app(), host='localhost', port=8080)
