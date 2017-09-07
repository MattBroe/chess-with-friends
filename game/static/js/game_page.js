/* jshint jquery: true, strict: false */

$(document).ready(function() {

  //Extract Django template variable values from the game_page template

  var long_fen = $("#current_game_long_fen").val(),
  short_fen = $("#current_game_short_fen").val(),
  current_pgn = $("#current_game_pgn").val(),
  current_status = $("#current_game_status").val(),
  game_over = $("#current_game_game_over").val(),
  draw_offered = $("#current_game_draw_offered").val(),
  color = $("#color").val(),
  csrf_token = $("#csrf_token").val();


  //game over is the string representation of a Python boolean: have to convert it to js boolean
  if (game_over === "True") {
    game_over = true;
  } else {
    game_over = false;
  }

  //Initialize vars related to the board and status display
  var board,
  game = new Chess(long_fen),
  statusEl = $('#status'),
  fenEl = $('#fen'),
  pgnEl = $('#pgn');

  game.load_pgn(current_pgn);
  statusEl.html(current_status);

  var update_draw_btn= function() {

    $("#decline-draw-btn").hide();

    if (draw_offered === "") {
      $("#draw-btn").html("Draw");

    } else if (draw_offered === color) {
      $("#draw-btn").html("Draw offered");

    } else {
      $("#draw-btn").html("Accept draw");
      $("#decline-draw-btn").show();
    }

  };

  var draw = function() {

    if (game_over) {
      return false;
    }

    $.ajax({

        url: $("#draw_url").val(),
        type: "GET",
        dataType: "json"

      }).done(function(data) {

        if (data.drawn) {
          statusEl.html("Game drawn by agreement");
          game_over = true;
        } else {
          draw_offered = color;
          update_draw_btn();
        }
      });
  };

  var decline_draw = function() {

    if (game_over) {
      return false;
    }

    $.ajax({
        url: $("#decline_draw_url").val(),
        type: "GET"
      });

    draw_offered = "";
    update_draw_btn();
  };

  var resign = function() {

      if (game_over) {
        return false;
      }

      $.ajax({
        url: $("#resign_url").val(),
        type: "GET"
      });

      var resign_status;
      if (color === "w"){
        resign_status = "Black wins by resignation";
      }
      if (color === "b") {
        resign_status = "White wins by resignation";
      }

      game_over = true;
      statusEl.html(resign_status);

  };

  $("#draw-btn").click(draw);

  $("#decline-draw-btn").click(decline_draw);

  $("#resign-btn").click(resign);
  

  update_draw_btn();

  var intervalID;

  var get_current_game_info = function() {
    $.ajax({

      url: $("#get_current_game_info_url").val(),

      type: "GET",

      dataType: "json"

      }).done(function(data) {
                //If it's your turn, the other player has already moved and posted it to the server
                if (color == data.color_to_play) {
                  //Update the board with the opponent's move
                  onDrop(data.move_source, data.move_target);
                  onSnapEnd();
                }
                statusEl.html(data.status); 
                game_over = data.game_over;

                if (game_over) {
                  clearInterval(intervalID);
                }

                draw_offered = data.draw_offered;
                update_draw_btn();

              });
  };

  //Poll the server to check for game updates resulting from the other player's actions.

  intervalID = setInterval(get_current_game_info, 5000);

  get_current_game_info();

  // post_move_data is called whenever the player makes a valid move.
  // It syncs the game on the server with the local game state.
  
  var post_move_data = function(source, target) {
    $.ajax({
          url: $("#post_move_url").val(),
          type: "POST",
          data: {
            "move_source": source,
            "move_target": target,
            "fen": game.fen(),
            "pgn": game.pgn(),
            "status": statusEl.html(),
            "game_over": game_over,
            csrfmiddlewaretoken: csrf_token
          }
      });
  };



  // do not pick up pieces if the game is over
  // only pick up pieces for the side to move
  var onDragStart = function(source, piece, position, orientation) {
    //This line prevents a user from making a move after the game has ended
    //via a draw or resignation.
    get_current_game_info();

    if (game.game_over() === true ||
        (game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1) ||
        color !== game.turn() ||
        game_over === true) {
      return false;
    }

  };

  var onDrop = function(source, target) {
    // see if the move is legal
    var move = game.move({
      from: source,
      to: target,
      //TODO: Allow any promotion
      promotion: 'q' // NOTE: always promote to a queen for example simplicity
    });

    // illegal move
    if (move === null) return 'snapback';

    updateStatus();
    
    game_over = game.game_over();

    // Posting the move to the server
    if (color !== game.turn()) {
      post_move_data(source, target);
    }
  };

  // update the board position after the piece snap 
  // for castling, en passant, pawn promotion
  var onSnapEnd = function() {
    board.position(game.fen());
  };

  var updateStatus = function() {
    var status = '';

    var moveColor = 'White';
    if (game.turn() === 'b') {
      moveColor = 'Black';
    }

    // checkmate?
    if (game.in_checkmate() === true) {
      status = 'Game over, ' + moveColor + ' is in checkmate.';
    }

    // draw?
    else if (game.in_draw() === true) {
      status = 'Game over, drawn position';
    }

    // game still on
    else {
      status = moveColor + ' to move';

      // check?
      if (game.in_check() === true) {
        status += ', ' + moveColor + ' is in check';
      }
    }

    statusEl.html(status);
    fenEl.html(game.fen());
    pgnEl.html(game.pgn());
  };
  
  var orientation;

  if (color === "w") {
    orientation = "white";
    } 

  else if (color === "b") {
        orientation = "black";
        }


  //chessboard.js uses a different FEN format than chess.js. Game.fen uses the chess.js format, which you have to split to get the chessboard.js format.

  var cfg = {
    draggable: true,
    position: short_fen,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    orientation: orientation
  };
          
  board = ChessBoard('board', cfg);

  updateStatus();

  statusEl.html(status);

});