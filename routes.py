from flask import Flask, render_template, request
import sqlite3
import logging


app = Flask(__name__)
log = app.logger
app.logger.setLevel(logging.DEBUG)



def removepluses(item):
    #Ah yes Perry, you are just in time to witness my latest invention, the DEPLUS-INATOR!!!!!

    rebuild = "" #Initialise DEPLUS-INATOR

    #REMOVE ALL PLUSES IN THE TRI-STATE AREA!!!
    for i in item:
        if i == '+':
            i = ' '
        rebuild += i
    #GIVE THEM BACK THEIR PLUSLESS WORLD!!! MWAH HA HA!!!!
    return rebuild


def addpluses(item):
    #Ah but there is MORE perry, here is the REPLUS-INATOR!!!

    rebuild = "" #Initialise REPLUS-INATOR

    #MAKE ALL SPACES PLUSES IN THE TRI-STATE AREA!!!
    for i in item:
        if i == ' ':
            i = '+'
        rebuild += i
    #GIVE THEM BACK THEIR PLUSLESS WORLD!  MWAH HA HA!!!
    return rebuild



@app.route('/card/hermit/<name>/<rarity>') # Hermit stats page
def hermit_page(name, rarity):
    #initialise sql and cursor
    conn =  sqlite3.connect('card.db')
    cur = conn.cursor()

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


    #generate the Header of the page
    Header = f"#{id} {HeadStats[0][1]} - {HeadStats[0][2]}"

    #set the deddicated stylesheeet
    stylesheet = "hermit_details.css"

    return render_template('hermit_details.html', HeadStats = HeadStats, HermitStats = HermitStats, SeeAlso = SeeAlso, title = title, Header = Header, stylesheet=stylesheet)


@app.route('/search')
def search():
    return render_template('layout.html')


@app.route('/beemovie') #thinking bee
def beemovie():
    return render_template('beemovie.html')



if __name__ == "__main__":
    app.run(debug=True)