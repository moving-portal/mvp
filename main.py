from flask import Flask, current_app, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
import logging
app = Flask(__name__)

@app.route("/")
def index():
  return current_app.send_static_file('index.html')

@app.route("/providers")
def providers():
  dawa = request.args.get("dawa")
  street = request.args.get("street")
  number = request.args.get("number")
  postalcode = request.args.get("postalcode")

  telia_results = []
  try:
    telia_results = telia(street, number, postalcode)
  except:
    logging.exception("Request to Telia failed")

  yousee_results = []
  try:
    yousee_results = yousee(dawa)
  except:
    logging.exception("Request to YouSee failed")
  
  stofa_results = []
  try:
    stofa_results = stofa(dawa)
  except:
    logging.exception("Request to YouSee failed")

  return jsonify(telia_results + yousee_results + stofa_results)

def yousee(dawa):
  url = "https://odinapi.yousee.dk/yousee/sales/pdsmdialog/productsandprices/broadband?addressId=" + dawa.replace("-", "").upper()
  content = requests.get(url).json()
  result = []
  speed_pattern = '([1-9][0-9]*)\/([1-9][0-9]*)'
  for p in content["products"]:
    speeds = re.search(speed_pattern, p["name"])
    result.append({
      'provider': "YouSee",
      'link': "https://yousee.dk/bredbaand/overblik.aspx",
      'description': p["originalName"],
      'price': p["priceInfo"]["product"]["price"],
      'speed': p["name"],
      'downstream': int(speeds.group(1)),
      'upstream': int(speeds.group(2))
      })
  return result

def stofa(dawa):
  url = "https://tzqx2ytgs1.execute-api.eu-central-1.amazonaws.com/prod/getBBProducts?env=prod&platform=stofa_privat_jlm&dawa_id=" + dawa
  content = requests.get(url).json()
  result = []
  for key in content["products"]:
    p = content["products"][key]
    result.append({
      'provider': "Stofa",
      'link': "https://stofa.dk/internet",
      'description': p["name"].replace("Stofa", ""),
      'technology': p["technology"],
      'price': p["price"]["recurrent"],
      'speed': str(p["down_speed"]) + "/" + str(p["up_speed"]) + " Mbit",
      'downstream': p["down_speed"],
      'upstream': p["up_speed"]
      })
  return result

def telia(street, number, postalcode):
  url = "https://www.telia.dk/teliadk/accessofferingblock/availableproducts?blockid=67999&streetName=" + street + "&streetNumber=" + number + "&floorNumber=&floorSide=&postCode=" + postalcode
  content = requests.get(url).json()
  result = []
  for p in content["products"]:
    for v in p["variants"]:
      result.append({
        'provider': "Telia",
        'link': "https://www.telia.dk/privat/abonnementer/bredbaand/",
        'description': p["productDescription"],
        'price': v["monthlyPrice"],
        'speed': str(v["downstreamSpeed"]) + "/" + str(v["upstreamSpeed"])  + " Mbit",
        'downstream': v["downstreamSpeed"],
        'upstream': v["upstreamSpeed"]
        })
  return result


if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0')