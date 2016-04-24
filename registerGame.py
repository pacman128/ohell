#!/usr/bin/python
import sys, GameState, ohhellquery, database

if len(sys.argv) < 2:
  print 'Usage: registerGame.py <xml files>'
  sys.exit(1)

db = database.open_database('localhost', 'oh_hell', 'db_config.txt')

for f in sys.argv[1:]:
  parser = GameState.GameXMLParser()
  gameState = parser.parse(f)

  ohhellquery.add_game_to_db(db, gameState)
