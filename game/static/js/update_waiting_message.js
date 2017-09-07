/* jshint jquery: true, strict: false */
$(document).ready(function() {
    var intervalID = setInterval(function() {

        $.ajax({

            url: $("#check_if_matched_url").val(),

            type: "GET",

            dataType: "json",

            success: function(data) {
                if (data.in_game) {
                    if ($("#wait_message").css("display") !== "none") {
                        $("#current_game_btn").toggle();
                        $("#start_game_btn").toggle();
                        $("#wait_message").toggle();
                    }
                    clearInterval(intervalID);
                }
            }



        });
    }, 5000);
});