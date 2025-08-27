from flask import Flask, render_template, request, redirect
import sqlite3
import logging
import math


app = Flask(__name__)
log = app.logger
app.logger.setLevel(logging.DEBUG)



@app.route('/') #Home page
def home():

   #PAGE STATICS
    Header = "HCTCG Database"
    Title = "Home - HCTCG Database"
    Stylesheet = "hermit_details.css" 

    return render_template('home.html', Header = Header, Title = Title, Stylesheet = Stylesheet)


@app.route('/Card/Hermit/<name>/<rarity>') # Hermit stats page
def hermit_page(name, rarity):
    #initialise sql and cursor
    conn =  sqlite3.connect('card.db')
    cur = conn.cursor()

    #query the database to get the "head" stats
    cur.execute(f"SELECT * FROM Card WHERE Name = '{name}' AND Rarity = '{rarity}';")
    HeadStats = cur.fetchall()
    id = HeadStats[0][0] #extract the id from the headstats

    #query the database to get the "hermit" stats
    cur.execute(f"SELECT * FROM Hermit WHERE id = {id}")
    HermitStats = cur.fetchall()
    #extract certain stats for later use
    Health = int(HermitStats[0][3])
    A1Damage = int(HermitStats[0][6])
    A2Damage = int(HermitStats[0][10])

    #grab a list of cards that share the same "owner" as the selected card.
    cur.execute(f"SELECT ID, Name, Rarity FROM Card WHERE ID IN (SELECT ID FROM Hermit WHERE OwnerName='{HermitStats[0][2]}') AND NOT ID = {id};")
    SeeAlso = cur.fetchall()

    #generate word versions of the attack cost
    A1Worded = []
    A2Worded = []
    A1Cost = 0
    A2Cost = 0
    for i in HermitStats[0][4]:
        if i == "X":
            A1Worded.append(HermitStats[0][1]) # add the type of the hermit to the list
            A1Cost += 5
        else:
            A1Worded.append("Any") #add "any" if not an X (a wild)
            A1Cost += 4

    for i in HermitStats[0][8]:
        if i == "X":
            A2Worded.append(HermitStats[0][1]) # add the type of the hermit to the list
            A2Cost += 5
        else:
            A2Worded.append("Any") #add "any" if not an X (a wild)
            A2Cost += 4

    #Query the database for any rulings asociated with the card.
    cur.execute(f"SELECT * FROM CardRuling WHERE CardID = {id}")
    Rulings = cur.fetchall()
    if not Rulings:
        Rulings = ["", "", "", ""]

    #Generate the Ratings of the cards
    #Generate using the CAV method (Cost Accounted Value)
    CAV = 9 * ((Health - 200 + A1Damage + A2Damage) / ((A1Cost + 10) * (A2Cost + 40))) + 0.1
    CAV = round(CAV, 2)


    #generate data on clashes with other cards

    #query the database for clashes in which the hermit wins.
    cur.execute(f"SELECT * FROM CardClash WHERE WinnerID = {id}")
    clashwin = cur.fetchall()
    clashwinfixed = []
    #"fix" the data so that it is formatted with the loser's name, and reason
    for i in clashwin:
        cur.execute(f"SELECT Name, Rarity, CardType FROM Card WHERE ID = {i[1]}")
        loser = cur.fetchall()
        clashwinfixed += [[loser[0][0], loser[0][1], loser[0][2], i[2]]]

    #query the database for clashes in which the hermit loses
    cur.execute(f"SELECT * FROM CardClash WHERE LoserID = {id}")
    clashlose = cur.fetchall()
    clashlosefixed = []
    #"Fix" the data in above format
    for i in clashlose:
        cur.execute(f"SELECT Name, Rarity, CardType FROM Card WHERE ID = {i[0]}")
        winner = cur.fetchall()
        clashlosefixed += [[winner[0][0], winner[0][1], winner[0][2], i[2]]]


    
    
    #PAGE STATICS
    Header = f"#{id} {HeadStats[0][1]} - {HeadStats[0][2]}"
    title = f"{HeadStats[0][1]} {HeadStats[0][2]} - Details"
    stylesheet = "hermit_details.css"

    return render_template('hermit_details.html', HeadStats = HeadStats, HermitStats = HermitStats, SeeAlso = SeeAlso, title = title, Header = Header, stylesheet=stylesheet, A1Worded = A1Worded, A2Worded = A2Worded, CAV = CAV, Rulings = Rulings, clashwinfixed = clashwinfixed, clashlosefixed = clashlosefixed)

@app.route('/Searchbar', methods =['POST'])
def search_redirect():
    search = request.form.get('query')
    return  redirect(f"/Search/Name/{search}")

@app.route('/Search/<string:category>/<string:query>')
def search(category, query):
    #initialise sql and cursor
    conn = sqlite3.connect('card.db')
    cur = conn.cursor()

    Header = ""

    if category in["ID", "Rarity", "CardType", "Series"]:
        cur.execute(f"SELECT Name, Rarity, Art, CardType FROM Card WHERE {category} = '{query}' ORDER BY Name ASC")
        Cards = cur.fetchall()
        Header = f"{query} Cards"
    if category == "Name":
        NameFormatted = "%"
        for i in query:
            NameFormatted += f"{i}%"
        cur.execute(f"SELECT Name, Rarity, Art, CardType FROM Card WHERE Name LIKE '{NameFormatted}'")
        Cards = cur.fetchall()
        Header = f"Cards matching '{query}'"
    if category in["Type", "OwnerName"]:
        cur.execute(f"SELECT Name, Rarity, Art, CardType FROM Card WHERE ID IN(SELECT ID FROM Hermit WHERE {category} = '{query}')")
        Cards = cur.fetchall()
        if category == "OwnerName":
            Header = f"{query}'s Cards"
        else:
            Header = f"{query} Cards"
    

    #PAGE STATICS
    Title = "Card Search"
    stylesheet = "search.css"
    return render_template('search.html', Header = Header, title = Title, stylesheet = stylesheet, Cards = Cards, category = category)


@app.route('/Rules')
def rulebook():

    #PAGE STATICS
    Header = "Rulebook"
    Title = "Rulebook"
    stylesheet = "Rules.css"
    return render_template('rules.html', title = Title, Header = Header, stylesheet = stylesheet)


@app.route('/About')
def about():

    #PAGE STATICS
    Header = "About HCTCG"
    Title = "About HCTCG"
    stylesheet = "About.css"
    return render_template('about.html', title = Title, Header = Header, stylesheet = stylesheet)


@app.route('/Changes')
def changes():

    #PAGE STATICS
    Header = "Card Changes"
    Title = "Card Changes"
    stylesheet = "Changes.css"
    return render_template('changes.html', title = Title, Header = Header, stylesheet = stylesheet)


@app.route('/beemovie') #thinking bee
def beemovie():
    return render_template('beemovie.html')



if __name__ == "__main__":
    app.run(debug=True)