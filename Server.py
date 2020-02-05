import bottle
import json

from bottle import route, run, response, get, delete, put, post

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
            datafinal.append("The value of " + a + " for "+ data[x]["Name"] + " is : "+ data[x][a])

    dataformatter = '<br/><br/>'.join(map(str, datafinal))#Permet de convertire la list en une chaine caractere
    return dataformatter

@get("/show/everything/<name>") #Donne toutes les informations de la personne Name
def showEverything(name) :
    data = json.loads(open("students.json").read())
    datafinal = list()

    for x in range(0, len(data)):
        if(name in data[x]["Name"]):
            return data[x]

    response.status = 404
    return 'Name not found'

@get("/showRowNumber/<value>/<name>") #Pour avoir le row number de la valeur chercher
def showRowNumber(value, name) :
    data = json.loads(open("students.json").read())
    datafinal = list()

    for x in range(0, len(data)):
        if(name in data[x][value]):
            return str(x) #Il faut convertir x en character sinon bottle n'arrive pas a afficher le resultat

    response.status = 404
    return name +' not found'

@get("/count/all/<name>")
def count(name):
    return name

####################################################################################
#                                   GET(to launch other verbs)                     #
####################################################################################
@get("/student/add")
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

    return 'Added ' + name

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
    
bottle.run(bottle.app(), host='localhost', port=8080)
