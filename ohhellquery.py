import _mysql
from MySQLdb.constants import FIELD_TYPE
import card
import database
import GameState

debug = False

class PlayerDictGenerator(database.DBDictGenerator):
  def __init__(self, db, id):
    database.DBDictGenerator.__init__(self, db,
      "SELECT * FROM player WHERE player_id = " + str(int(id)) + ";")

  
       
class GameDictGenerator(database.DBDictGenerator):
  def __init__(self, db, id):
    database.DBDictGenerator.__init__(self, db,
      "SELECT * FROM game WHERE game_id = " + str(int(id)) + ";")


def get_deals( db, game_id ):
  players = database.get_table(db, 'player', 'player_id')

  game_players = database.get_table_with_composite_key(db, 'game_players', ('game_id', 'player_id'),
                                              'WHERE game_id = ' + str(game_id))
  num_players = len(game_players)
  player_list = num_players*[0]
  for i in range(num_players):
    gp = game_players[(game_id,i+1)]
    player_list[gp.game_order-1] = players[ gp.player_id]
    
  deals = []
  for player in player_list:
    deal = database.get_table(db, 'deal, bid', 'deal_id', 'WHERE deal.deal_id = bid.deal_id'
                                  + ' AND game_id = ' + str(game_id)
                                  + ' AND player_id = ' + str(player.player_id) + ' ORDER BY deal',
                                  'bid.deal_id, dealer_id, deal, num_cards, bid_id, bid'   )
    deals.append(deal)
    
  return player_list, deals
  
def get_tricks_won_in_deal( db, deal_id, player_ids):
  tricks_won = {}
  for id in player_ids:
    tricks_won[id] = 0
    
  tricks = database.get_table(db, 'trick', 'trick_id', 'WHERE deal_id = ' + str(deal_id)
                                              + ' ORDER BY trick_num')

  for t in tricks.values():
    id = t.winner_id
    tricks_won[id] = tricks_won[id] + 1
  
  return tricks_won

def calc_points( bid, tricks_won):
  if tricks_won == bid:
    return bid*bid + 10
  elif tricks_won > bid:
    return 0
  else:
    return 5*(tricks_won - bid)

def add_game_to_db(db, gameState):
  player_map = create_xml_id_to_db_id_map(db, gameState)
  game_id = add_game_entry( db, gameState, player_map)
  add_player_entries( db, gameState, player_map, game_id)
  add_hands_to_db(db, gameState, player_map, game_id)
  
def create_xml_id_to_db_id_map( db, gameState):
  """
    Create a list that maps XML id numbers to database player_id values
    
    Params:
      db        : open database connection
      gameState : game state 
      
    Returns:
      list with database player ids in order of listing in XML file
  """
  player_map = []
  xml_players = gameState.getPlayers()
  for p in xml_players:
    t = database.get_table(db, "player", "player_id", "WHERE first_name = '" + p[1] + "'")
    player_map.append( t.values()[0].player_id)
  
  #print "player_map =", player_map
  return player_map


def add_game_entry( db, gameState, player_map):
  """
    Add entry for a game into Game database table
    
    Params:
      db - Open database connection
      gameState - GameState of game
      player_map - map of xml player ids to database ids
      
    Returns:
      key of added game entry
  """
  scores = gameState.currentScores()
  winner_index = 0
  high_score = scores[0]
  for i in range(1,len(scores)):
    if scores[i] > high_score:
      winner_index = i
      high_score = scores[i]
  
  n_high_scores = 0
  for s in scores:
    if s == high_score:
      n_high_scores = n_high_scores + 1

  tie = n_high_scores > 1
  
  if not tie:
    winner_id = player_map[winner_index]
  else:
    winner_id = 0
    
  query = ("INSERT INTO game VALUES ( NULL, '"
          + gameState.time + "', " + str(winner_id) + " );")

  if debug:
    print query
    game_id = -1
  else:
    db.query( query )
    game_id = db.insert_id()
  return game_id
  
def add_player_entries( db, gameState, player_map, game_id):
  n_players = len(player_map)
  query = "INSERT INTO game_players VALUES "
  for i in range(n_players):
    query = query + "( " + str(game_id) + ", " + str(player_map[i]) + ", " + str(i+1) + ")"
    if i != n_players - 1:
      query = query + ", "
  
  query = query + ";"
  
  if debug:
    print query
  else:
    db.query( query)

def add_hands_to_db( db, gameState, player_map, game_id):
  hands = gameState.getHands()
  
  for i in range(len(hands)):
    query = ("INSERT INTO deal VALUES ( NULL, "
          + str(game_id) + ", " + str(i+1) + ", " + str(hands[i].getNumCards()) +
          ", " + str(player_map[hands[i].getDealer()]) + ", "
          + str(hands[i].getTrump()) + ");")
    if debug:
      print query
      deal_id = -2
    else:
      db.query( query)
      deal_id = db.insert_id()
    
    bids = hands[i].getBids()
    query = "INSERT INTO bid VALUES "
    for p in range(len(player_map)):
      query = query + ( "( NULL, " + str(bids[p]) + ", "
                      + str(deal_id) + ", " + str(player_map[p]) + ")" )
      if p < len(player_map) - 1:
        query = query + ', '
    query = query + ';'
    
    if debug:
      print query
    else:
      db.query( query)
    
    tricks = hands[i].getTricks()
    trump = hands[i].getTrump()
    for j in range(len(tricks)):
      cards = tricks[j].getCards()
      #print 'cards:', cards
      query = ("INSERT INTO trick VALUES ( NULL, "
          + str(j+1) + ", "
          + str(player_map[tricks[j].getWinner(trump)]) +
          ", " + str(deal_id) + ");")
          
      if debug:
        print query
        trick_id = -3
      else:
        db.query( query)
        trick_id = db.insert_id()
    
      query = "INSERT INTO trick_cards VALUES "
      for j in range(len(cards)):
        player_num, card_played = cards[j]
        
        query = (query + "( " + str(trick_id) + ", "
                 + str(player_map[player_num])
                 + ", " + str(j+1) + ", " + str(card_played) + ")")
        if j < len(cards) - 1:
          query = query + ', '
      
      query = query + ';'
      
      if debug:
        print query
      else:
        db.query( query)
        
    

class GameStateCreator:
  """
    Reads a game out of the database and creates a GameState object from it
  """
  def __init__(self, db):
    """
      Constructor:
      
      Parameters:
        db - Database connection to use
    """
    self.db = db
    
  def create( self, game_id):
    """
      Create a GameState object from the database
      
      Parameters:
        game_id - ID of game in database
    """
    game_state = GameState.GameState()
    game_stats = database.get_table( self.db, 'game', 'game_id', 
                                     'where game_id = ' + str(game_id) )
    player_list, deals = get_deals(self.db, game_id)
    game_state.init_new( len(player_list), game_stats[game_id].time) 
    
    # player_map maps the database player_id to the game_state 
    # player_id value
    player_map = {}
    i = 0
    for player in player_list:
      game_state.addPlayer(i, player.first_name, None)
      player_map[player.player_id] = i
      i = i + 1
      #print 'Added player id', player.player_id
      
    deal_ids = deals[0].keys()
    deal_ids.sort()
    
    deals_table = database.get_table(self.db, 'deal', 'deal_id', 'where game_id = ' 
        + str(game_id) + ' order by deal')

    for i in deal_ids:
      hand = GameState.HandState(len(player_list), deals[0][i].num_cards, 
                                 deals_table[i].trump, player_map[deals_table[i].dealer_id])
      
      
      tricks = database.get_table( self.db, 'trick', 'trick_id',
                                   'where deal_id = ' + str(i) )
      
      trick_ids = tricks.keys()
      trick_ids.sort()

      trick_set = str(trick_ids).replace('[', '(').replace(']',')')
      where_cause = 'where trick_id in ' + trick_set  
      tricks_made = {}
      for j in player_list:
        tricks_made[j.player_id] = 0
        cards = database.get_table_with_composite_key( self.db, 
                                                       'trick_cards', 
                                                       ['trick_id', 'player_id'],
                                                       where_cause +
                                                       ' and player_id = ' + str(j.player_id))
        card_codes = [ x.card for x in cards.values() ]
        card_codes.sort()
        #print j, card_codes
        hand.setHand( player_map[j.player_id], card_codes)
        
      for j in range(len(player_list)):
        hand.setBid( player_map[player_list[j].player_id], deals[j][i].bid)
       
      # Need to add cards dealt to hand first
      for j in trick_ids:
        trick = tricks[j]
        tricks_made[trick.winner_id] = tricks_made[trick.winner_id] + 1
        trick_state = GameState.TrickState()
        cards = database.get_table_with_composite_key( self.db, 
                                                      'trick_cards',
                                                      ['trick_id', 'player_id'],
                                                      'where trick_id = ' + str(j))
        card_list = [ (x, cards[x]) for x in cards.keys() ]
        card_list.sort( cmp = lambda x,y : cmp(x[1].card_num, y[1].card_num) )
        for c in card_list:
          trick_state.addCard(player_map[c[0][1]], c[1].card)
        
        hand.addTrick(trick_state)
      
      for p in tricks_made.keys():
        hand.setTricksMade(player_map[p], tricks_made[p])
          
      game_state.addHand(hand)
    
    return game_state
  
