var requestURL = "/api/game";

var SUIT = [ 'Clubs', 'Diamonds', 'Hearts', 'Spades' ];
var VALUE = [ 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
              'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace' ];

                    

function card_to_string( i )
{
    var suit = Math.floor(i/13);
    if ( suit === 1 || suit === 2 ) {
        var color = 'red'
    }
    else {
        var color = 'black'
    }
    return '<font color="' + color + '">' + VALUE[i%13] + ' of ' +
        SUIT[Math.floor(i/13)] + '</font>';
}

function make_hand( hand, game_id, hand_id)
{
    var text = 'Trump: ' + ((hand.trump >= 0) ? card_to_string( hand.trump) : 'None');
    text += ' Dealer: ' + hand.players[hand.dealer_id][0] + '<br><br>\n';
    var cards = { };
    for( p in hand.players ) {
        cards[p] = []
    }
    var trick_text = '';
    for ( i in hand.tricks) {
        var trick = hand.tricks[i];
        for(j in trick ) {
            var play = trick[j];
            trick_text += hand.players[play.player_id][0] + ' played ' +
                          card_to_string(play.card) + '<br>\n';
            cards[play.player_id].push( play.card);
        }
        trick_text += '<br>\n';
    }

    text += '<table class="deal"><thead class="deal_players">';
    for( p in hand.players ) {
        cards[p].sort( function(x,y) { return x-y } );
        text += '<th class="deal_players">' + hand.players[p][0] + '</th>'
    }

    text += '</thead><tbody class="deal_cards">';
    for( i=0; i < hand.tricks.length; i++ ) {
        text += '<tr class="deal_cards">';
        for( p in hand.players ) {
            text += '<td class="deal_cards">' + card_to_string(cards[p][i]) + '</td>';
        }
        text += '</tr>';
    }
    text += '</tbody></table></br>';

    return text + trick_text;
}

function create_hand(hand, game_id, hand_id)
{
    var id = '_' + game_id + '_' + hand_id;
    var tr = $('#hand_tr' + id);
    var html =
        '<tr id="hand' + id + '"><td>&nbsp;</td><td colspan="'
        + (tr.children().length - 1) +
        '">' + make_hand(hand, game_id, hand_id) + "</td></tr>";
    tr.after( html);
}

function show_hand( game_id, hand_id )
{
    var button = $('#btn_' + game_id + '_' + hand_id);
    var hand_tr_id = '#hand_' + game_id + "_" + hand_id;
    if ( $(hand_tr_id).length  ) {
        console.log("toogle() for '" + hand_tr_id + "'");
        $(hand_tr_id).toggle();
    } else {
        console.log("Getting json for " + game_id + ", " + hand_id);
        $.getJSON( requestURL + '/' + game_id + '/' + hand_id, function(hand) {
            create_hand(hand, game_id, hand_id)
        });
    }
    if ( button.text() === '+' ) {
        button.text('-');
    } else {
        button.text('+');
    }
    
}

function make_scoresheet( game, id) {
    var players = game.players;
    var text = "Winner: " + game.winner + "\n<table>\n<tr><th>&nbsp;</th><th>Tricks</th>";
    var i, j, hand, trick, td_class;
    var button_id;

    players.forEach( function(player) {
        text += "<th>" + player.name + "</th>";
    });
    text += "</tr>\n";
    
    for( i = 0; i < game.hands.length; i++ ) {
        hand = game.hands[i];
        button_id = id + '_' + (i+1);
        text += '<tr id="hand_tr_' + button_id + '"><td><button type="button" id="btn_' + button_id +
            '" onclick="show_hand(' + id + ',' + (i+1) + ')">+</button></td><td>' +
            hand.num_cards + "</td>";
        for( j=0; j < hand.tricks.length; j++) {
            trick = hand.tricks[j];
            if ( i === 0 ) {
                td_class = (trick.score > 0) ? "up" : ((trick.score < 0) ? "down" : "same");
            } else {
                td_class = (trick.score > game.hands[i-1].tricks[j].score) ? "up" :
                    ((trick.score < game.hands[i-1].tricks[j].score) ? "down" : "same");
            }

            text += '<td class="' + td_class + '">(' + trick.bid + "," + trick.tricks + ") "
                + trick.score + "</td>";
        }
        text += "</tr>\n";
    }
    
    text += "</table>\n";

    return text;
}

function createGameTable( game, item, id) {
    item.append('<div id="scoresheet' + id + '">' + make_scoresheet(game, id) + "</div>");
}

function openGame( id ) {
    var item = $('#btn' + id);
    
    if ( $('#scoresheet' + id).length  ) {
        console.log("toogle() for '" + id + "'");
        $('#scoresheet' + id).toggle();
    } else {
        console.log("Getting json for " + id);
        $.getJSON( requestURL + '/' + id, function(game) {
            createGameTable(game, item.parent(), id)
        });
    }
    if ( item.text() === '+' ) {
        item.text('-');
    } else {
        item.text('+');
    }
}

var main = function () {
    "use strict";

    var colors = [
        {
            color:"#F7464A",
            highlight: "#FF5A5E",
        },
        {
            color: "#46BFBD",
            highlight: "#5AD3D1",
        },
        {
            color: "#FDB45C",
            highlight: "#FFC870",
        },
        {
            color: "#00F0F0",
            highlight: "#00FFFF",
        },
        {
            color: "#F030F0",
            highlight: "#FF3FFF",
        }
    ];

    $.getJSON(requestURL, function(games) {

        var players_dict = { };
        var data = [];
        var count = 0;
        games.players.forEach( function( player) {
            players_dict[player.id] = player;
            data.push( { value: player.wins,
                         color: colors[count%colors.length].color,
                         highlight: colors[count%colors.length].highlight,
                         label: player.name } );
            count++;
        });

        var ties = games.games.filter( function(item) { return item.winner_id === 0; }).length;

        console.log('# ties = ' + ties);
        data.push( { value: ties,
                     color: colors[count%colors.length].color,
                     highlight: colors[count%colors.length].highlight,
                     label: 'Ties' } );


        $(".games").append('<canvas id="myChart" width="400" height="400"></canvas>');

        // Get context with jQuery - using jQuery's .get() method.
        var ctx = $("#myChart").get(0).getContext("2d");
        // This will get the first returned node in the jQuery collection.
        var pie_chart = new Chart(ctx).Pie(data);

        games.games.sort(function(a, b){
            var keyA = new Date(a.timestamp.replace(' ','T'));
            var keyB = new Date(b.timestamp.replace(' ','T'));
            return (keyA < keyB) ? 1 : ( (keyA > keyB) ? -1 : 0);
        });

        games.games.forEach(function (item) {
            $(".games").append( '<div id="game' + item.id + '">  <button type="button" id="btn'
                                + item.id + '">+</button>' + item.timestamp + ' '
                                + (( item.winner_id > 0 ) ? players_dict[item.winner_id].name : 'Tie')
                                + '</div>');
            $("#btn" + item.id).click( function() { openGame(item.id) });
        });

    });
};


$(document).ready(main);
