from flask import Flask, render_template
import sqlite3
import logging


app = Flask(__name__)
log = app.logger
app.logger.setLevel(logging.DEBUG)



def removehyphens(item):
    #Ah yes Perry, you are just in time to witness my latest invention, the DEHYPHEN-INATOR!!!!!

    rebuild = "" #Initialise DEHYPHEN-INATOR

    #REMOVE ALL HYPHENS IN THE TRI-STATE AREA!!!
    for i in item:
        if i == '-':
            i = ' '
        rebuild += i
    #GIVE THEM BACK THEIR HYPHENLESS WORLD!!! MWAH HA HA!!!!
    return rebuild


def addhyphens(item):
    #Ah but there is MORE perry, here is the REHYPHEN-INATOR!!!

    rebuild = "" #Initialise REHYPHEN-INATOR

    #MAKE ALL SPACES HYPHENS IN THE TRI-STATE AREA!!!
    for i in item:
        if i == ' ':
            i = '-'
        rebuild += i
    #GIVE THEM BACK THEIR SPACELESS WORLD!  MWAH HA HA!!!
    return rebuild

 

@app.route('/card/hermit/<name>/<rarity>') # Hermit stats page
def hermit_page(name, rarity):
    #initialise sql and cursor
    conn =  sqlite3.connect('card.db')
    cur = conn.cursor()

    #remove all hyphens from the url to query the database
    name = removehyphens(name)
    rarity = removehyphens(rarity)

    #query the database to get the "head" stats
    cur.execute(f"SELECT * FROM Card WHERE Name = '{name}' AND Rarity = '{rarity}';")
    HeadStats = cur.fetchall()
    id = HeadStats[0][0] #extract the id from the headstats
    title = f"{HeadStats[0][1]} {HeadStats[0][2]} - Details"
    #query the database to get the "hermit" stats
    cur.execute(f"SELECT * FROM Hermit WHERE id = {id}")
    HermitStats = cur.fetchall()

    #grab a list of cards that share the same "owner" as the selected card.
    cur.execute(f"SELECT ID, Name, Rarity FROM Card WHERE ID IN (SELECT ID FROM Hermit WHERE OwnerName='{HermitStats[0][2]}') AND NOT ID = {id};")
    SeeAlso = cur.fetchall()


    return render_template('hermit_details.html', HeadStats = HeadStats, HermitStats = HermitStats, SeeAlso = SeeAlso, title = title)


@app.route('/beemovie')
def beemovie():
    return render_template('beemovie.html')



if __name__ == "__main__":
    app.run(debug=True)