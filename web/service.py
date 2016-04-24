#!/usr/bin/env python

from bottle import Bottle, run, template, route, static_file
import time
import sys
import json
sys.path.append('/home/pcarter/projects/trunk/oh-hell')
import _mysql
from MySQLdb.constants import FIELD_TYPE
import card
import database
import GameState
import ohhellquery
from pprint import pprint

app = Bottle()

def create_player_stat(id, name, wins):
  return { 'id' : id, 'name' : name, 'wins' : wins}

def create_game_stat( id, timestamp, winner):
  return { 'id' : id, 'timestamp' : timestamp, 'winner_id' : winner }


def get_query_results( db, query):
  db.query( query)
  result = db.store_result()
  done = False
  rows = []
  while not done:
    row = result.fetch_row(1,0)
    done = len(row) == 0
    if not done:
      rows.append(row[0])
  return rows


@app.route('/api/game')
def api_game_list( id = None):
  try:
    db = database.open_database('localhost', 'oh_hell', 'db_config.txt')

    players = database.get_table(db, 'player', 'player_id')

    games = database.get_table(db, 'game', 'game_id')

    jsonRep = { 'games' : [], 'players' : [] }
    count = {}
    for k in players.keys():
      count[k] = 0

    tieCount = 0
    for id in games.keys():
      game = games[id]
      if game.winner_id > 0:
        winner = players[game.winner_id].first_name
        count[game.winner_id] = count[game.winner_id] + 1
      else:
        winner = 'Tie'
        tieCount = tieCount + 1

      jsonRep['games'].append( create_game_stat(id, game.time, game.winner_id))

    for k in count.keys():
      jsonRep['players'].append( create_player_stat(k, players[k].first_name, count[k]))
    
    return jsonRep
  finally:
    if db != None:
      db.close()

@app.route('/api/game/<game_id:int>/<deal:int>')
def api_game_hand_summary( game_id, deal):
  try:
    db = database.open_database('localhost', 'oh_hell', 'db_config.txt')

    deal_infos = database.get_table( db, 'deal', 'deal_id',
                                     'where game_id = %d and deal = %d' % (game_id, deal))
    deal_info = deal_infos[deal_infos.keys()[0]]

    tricks = get_query_results(db,
                               'select trick_id from trick where deal_id = '
                               + str(deal_info.deal_id) + ' order by trick_id')
    trick_list = []
    for (trick_id,) in tricks:
      cards = get_query_results(db,
                                'select player_id, card from trick_cards '
                                + 'where trick_id = ' + str(trick_id) + ' order by card_num')
      trick_list.append( [ { 'player_id' : c[0], 'card' : c[1] }  for c in cards ])

    player_ids = [ "'" + str(trick['player_id']) + "'" for trick in trick_list[0] ]
    players = database.get_table( db, 'player', 'player_id',
                                  'where player_id in ( ' + ','.join(player_ids) + ')' )

    player_map = {}
    for player_id, row in players.iteritems():
      player_map[player_id] = (row.first_name, row.last_name)

    jsonRep = { 'deal_id' : deal_info.deal_id,
                'players' : player_map,
                'dealer_id' : deal_info.dealer_id,
                'num_cards' : deal_info.num_cards,
                'trump' : deal_info.trump,
                'tricks' : trick_list }

    return jsonRep
  finally:
    if db is not None:
      db.close()

@app.route('/api/game/<id:int>')
def api_game_summary( id ):
  try:
    db = database.open_database('localhost', 'oh_hell', 'db_config.txt')

    players = database.get_table(db, 'player', 'player_id')
    games = database.get_table(db, 'game', 'game_id', 'WHERE game_id = ' + str(id))
    game = games[id]

    gsc = ohhellquery.GameStateCreator(db)
    gs = gsc.create(id)

    if game.winner_id > 0:
      winner = players[game.winner_id].first_name
    else:
      winner = 'Tie'
    
    jsonRep = { 'winner' : winner, 'players' : [], 'hands' : []}
    gsPlayers = gs.getPlayers()

    scores = gs.currentScores()

    for player in gsPlayers:
      jsonRep['players'].append( { 'id' : player[0], 'name' : player[1], 'ip' : player[2] })
    nPlayers = len(gsPlayers)

    scoreSheet = gs.getScoreSheet()
    for hand in scoreSheet:
      hand_info =  { 'num_cards' : hand[0], 'tricks' : [] }
      for player in hand[1]:
        hand_info['tricks'].append( { 'bid' : player[0], 'tricks' : player[1], 'score': player[2] })
      jsonRep['hands'].append( hand_info)

    return jsonRep

  finally:
    if db != None:
      db.close()



@app.route('/game')
def gameList( id = None):
  try:
    db = database.open_database('localhost', 'oh_hell', 'db_config.txt')

    players = database.get_table(db, 'player', 'player_id')

    games = database.get_table(db, 'game', 'game_id')
  
    text = ''
    count = {}
    for k in players.keys():
      count[k] = 0

    tieCount = 0
    for id in reversed(games.keys()):
      game = games[id]
      if game.winner_id > 0:
        winner = players[game.winner_id].first_name
        count[game.winner_id] = count[game.winner_id] + 1
      else:
        winner = 'Tie'
        tieCount = tieCount + 1
    
      link = '<a href="/game/%d">%s</a>' % ( id, game.time[:10])
      text += (str(id) + ": " + link + " : " + winner + "<BR>\n")
  
    text += ('<p>\n')

    for k in count.keys():
      text += (players[k].first_name + ": " + str(count[k]) + "<BR>\n")
  
    if tieCount > 0:
      text += ( 'Ties : ' + str(tieCount) + "<BR>\n")
    
    return "<html><head><title>Oh Hell Games</title></head><body>\n" + text + "\n</body></html>\n"
  finally:
    if db != None:
      db.close()

@app.route('/static/<path:path>')
def static( path ):
  return static_file(path, root='/home/pcarter/projects/oh-hell-bottle-service/static')

@app.route('/game_new')
def game_new():
  return template( 'game_template')

@app.route('/game/<id:int>')
def gameSummary( id ):
  try:
    db = database.open_database('localhost', 'oh_hell', 'db_config.txt')

    players = database.get_table(db, 'player', 'player_id')
    games = database.get_table(db, 'game', 'game_id', 'WHERE game_id = ' + str(id))
    game = games[id]

    gsc = ohhellquery.GameStateCreator(db)
    gs = gsc.create(id)

    if game.winner_id > 0:
      winner = players[game.winner_id].first_name
    else:
      winner = 'Tie'
    text = """
<html>
<head>
<title>Oh Hell game on """ + game.time[:10] + """</title>
</head>
<body>
<table>
<tr>
<td>Game Id:</td><td> """ + str(id) + """ </td>
</tr>
<tr>
<td>Date :</td><td>""" + game.time[:10] + """</td>
</tr>
<tr>
<td>Winner :</td><td>""" + winner + """ </td>
</tr>
</table>
<p>
<p>
<table border=1 cellspacing=5 cellpadding=5>
"""
    gsPlayers = gs.getPlayers()
    scores = gs.currentScores()

    text += '<tr>\n<td>&nbsp;</td>'
    for player in gsPlayers:
      text += '<th>' + player[1] + '</th>'
    text += ('</tr>\n')
    nPlayers = len(gsPlayers)

    scoreSheet = gs.getScoreSheet()
    oldScores = len(gsPlayers)*[0,]
    for hand in scoreSheet:
      text += '<tr><td>%d</td>'% ( hand[0])
      i = 0
      for player in hand[1]:
        text += "<td>"
        font = False
        if oldScores[i] < player[2]:
          text += "<font color='green'>"
          font = True
        elif oldScores[i] > player[2]:
          text += "<font color='red'>"
          font = True
        text += "(%d, %d) %d" % player
        if font:
          text += "</font>"
        text += "</td>"
        oldScores[i] = player[2]
        i = i + 1
      text +=  '</tr>\n'

    return text + "</table>\n</body>\n</html>"

  finally:
    if db != None:
      db.close()

run(app, host='0.0.0.0', port=8080)
  
