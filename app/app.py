import time
import redis
from flask import Flask, render_template, url_for
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv() 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)



def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/titanic')
def titanic():
    table = pd.read_csv("static/titanic.csv")
    table = pd.DataFrame(table)
    
    plt.figure(figsize=(8, 6))
    
    d= pd.DataFrame(table.groupby(["Sex"])["Survived"].sum())
    d = d.reset_index()
    color_map = {'male': 'green', 'female': 'blue'}
    colors = [color_map[x] for x in d['Sex']]
    p = plt.bar(d['Sex'],d["Survived"],color = colors)
    plt.ylabel('Count')
    for bar, count in zip(p, d['Survived']):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(count), ha='center', va='bottom')

    plt.grid(True)
    plot_file = "static/titanic_survivors.png"
    plt.savefig('static/titanic_survivors.png')
    plot =  url_for('static', filename='titanic_survivors.png')
    table = table.head(10)
    table = table.to_html()
    fav = url_for('static', filename='favicon.ico')
    return render_template('titanic.html', name= "BIPM", fav = fav, table = table, plot = plot)

@app.route('/')
def hello():
    count = get_hit_count()
    imag = url_for('static', filename='big_data.png')
    fav = url_for('static', filename='favicon.ico')
    return render_template('hello.html', name= "BIPM", count = count, imag = imag, fav = fav)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)


