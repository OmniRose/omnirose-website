jQuery(function ($) {
  console.log('starting');


  var $compass_video_container = $("#compass_video_container");
  var $shadow_video_container  = $("#shadow_video_container");

  var compass_video = $compass_video_container.find("video")[0];
  var shadow_video  = $shadow_video_container.find("video")[0];

  var $synchronise_videos_button = $("#synchronise_videos");

  var stored_data = {
    "readings": [],
    "latitude": undefined,
    "longitude": undefined,
    "compass_video_start_time": undefined
  };

  // hide all but the first user steps
  $(".user_step").not(":first").hide();
  function go_to_next_user_step () {
    var $current_step = $(".user_step").filter(":visible");
    $current_step.hide();
    $current_step.next().show();

  }

  function seconds_to_hhssmmm (seconds) {
    var date = new Date(null);
    date.setMilliseconds(seconds * 1000);
    return date.toISOString().substr(14, 9);
  }

  function pause_video_and_correct_time (video) {
    video.pause();
    var correction = video.currentTime % 0.03125;
    video.currentTime -= correction;
  }

  function setup_video($video_container, controls_class) {
    var $input = $video_container.find("input");
    var video = $video_container.find("video")[0];
    var $video = $(video);
    var $video_current_time = $video_container.find(".current_time");

    var $video_controls = $("div." + controls_class);
    var $play_buttons = $video_controls.find(".play_button");
    var $step_buttons = $video_controls.find(".step_button");
    var $zoom_buttons = $video_controls.find(".panzoom_button");
    var $play_buttons_glyph_span = $play_buttons.find("span.glyphicon");
;

    $input.on('change', function (event) {
      var file = this.files[0];
      console.debug(file, file.type);

      // check that we can play this sort of file
      if (video.canPlayType(file.type)) {
        console.log('can play video');
        var fileURL = URL.createObjectURL(file);
        video.src = fileURL;

        $input.hide();

      } else {
        alert("can't play this kind of video");
      }
    });

    $video_current_time.text(seconds_to_hhssmmm(0));
    $video.on('timeupdate', function () {
      $video_current_time.text(seconds_to_hhssmmm(video.currentTime));
    });

    $video.on('play', function () {
      $play_buttons_glyph_span.removeClass("glyphicon-play");
      $play_buttons_glyph_span.addClass("glyphicon-pause");
    });

    $video.on('pause', function () {
      $play_buttons_glyph_span.addClass("glyphicon-play");
      $play_buttons_glyph_span.removeClass("glyphicon-pause");
    });

    $video.panzoom({
      // See https://github.com/timmywil/jquery.panzoom#options for details
      increment: 0.5,
      minScale: 1,
      maxScale: 8,
      contain: false
    });

    $zoom_buttons.on("click", function( e ) {
      e.preventDefault();

      var action = $(this).data("action");

      switch (action) {
        case 'zoomIn':
          $video.panzoom("zoom", false);
          break;
        case 'zoomOut':
          $video.panzoom("zoom", true);
          break;
        default:
          $video.panzoom(action);
      }

    });

    $play_buttons.on('click', function () {
      if (video.paused) {
        video.play();
      } else {
        pause_video_and_correct_time(video);
      }
    });

    $step_buttons.on("click", function () {
      var $button = $(this);
      var step_amount = $button.data('steps');

      pause_video_and_correct_time(video);
      video.currentTime = video.currentTime + step_amount;
    });
  }

  setup_video($compass_video_container, "compass_video_controls");
  setup_video($shadow_video_container,  "shadow_video_controls");

  $synchronise_videos_button.on('click', function (e) {
    e.preventDefault();

    // Make sure both videos are not playing
    pause_video_and_correct_time(compass_video);
    pause_video_and_correct_time(shadow_video);

    var video_delta = compass_video.currentTime - shadow_video.currentTime;
    console.log("video delta:", video_delta);

    // Add a bit of code to keep the two videos in sync
    $(compass_video).on('timeupdate', function () {
      var new_time = compass_video.currentTime - video_delta;
      shadow_video.currentTime = new_time;
    });

    // disable the shadow video controls
    $shadow_video_container.find(".play_button").prop('disabled', true);
    $shadow_video_container.find(".step_button").prop('disabled', true);

    // Our work is done!
    go_to_next_user_step();
  });


  function display_message_for_input ($input, message) {
    $input
      .closest(".form-group")
      .find(".where_when_input_parsed")
      .text(message);
  }

  (function () {
    var $where_when_form = $("#where_when_form");
    var $where_when_datetime    = $where_when_form.find("input[name='datetime']");
    var $where_when_submit      = $where_when_form.find("input[type='submit']");
    var $where_when_latitude    = $where_when_form.find("input[name='latitude']");
    var $where_when_longitude   = $where_when_form.find("input[name='longitude']");
    var $where_when_coordinates = $where_when_latitude.add( $where_when_longitude );

    function parse_datetime_from_input ($input) {
      var millis = Date.parse($input.val());
      var $span = $("#where_when_datetime_parsed");
      if ( millis ) {
        return new Date(millis);
      } else {
        return null;
      }
    }

    function parse_coordinate_from_input ($input) {
      var parsed = magellan($input.val());
      var valid = parsed[$input.prop("name")]();
      return valid;
    }

    function parse_dd_from_input ($input) {
      var coordinate = parse_coordinate_from_input($input);
      if (coordinate) {
        return parseFloat(coordinate.toDD());
      } else {
        return null;
      }
    }

    $where_when_datetime.on('input', function (e) {
      var $input = $(this);
      var date = parse_datetime_from_input($input);
      if ( date ) {
        display_message_for_input($input, date.toUTCString());
      } else {
        display_message_for_input($input, 'Could not parse date - try format "yyyy/mm/dd hh:mm:ss GMT"');
      }
    });

    // When entering the lat and long give the user a running conversion
    $where_when_coordinates.on('input', function (e) {
      var $input = $(this);
      var valid = parse_coordinate_from_input($input);

      if (valid) {
        display_message_for_input($input, valid.toDM(" ") + ' or ' + valid.toDMS(" "));
      } else {
        display_message_for_input($input, "Could not parse the coordinate - try 'DD MM.mmm' or 'DD MM SS.sss'");
      }
    });

    $where_when_form.on("submit", function (e) {
      e.preventDefault();

      var $form = $(this);
      var date = parse_datetime_from_input($where_when_datetime);
      var lat  = parse_dd_from_input($where_when_latitude);
      var lon  = parse_dd_from_input($where_when_longitude);

      console.log(date, lat, lon);
      if (date && lat && lon) {
        stored_data.latitude = lat;
        stored_data.longitude = lon;
        stored_data.compass_video_start_time = date.getTime() / 1000 - compass_video.currentTime;
        console.log(stored_data);
        go_to_next_user_step();

      } else {
        display_message_for_input($where_when_submit, "Please ensure all of the above are filled in correctly.");
      }

    });
  })();

  (function () {
    var $correction_form  = $("#azimuth_correction_form");
    var $correction_input  = $correction_form.find("input[name='correction']");

    function parse_float_from_input ($input) {
      var value = $input.val();
      var float = parseFloat(value);
      if ( float ) {
        return float;
      } else {
        return null;
      }
    }

    $correction_form.on("submit", function (e) {
      e.preventDefault();

      var $form = $(this);
      var correction = parse_float_from_input($correction_input);

      console.log(correction);

      if (correction) {
        stored_data.azimuth_correction = correction;
        console.log(stored_data);
        go_to_next_user_step();


      } else {
        display_message_for_input($correction_input, "We require a value...");
      }

    });
  })();


  (function () {
    var readings = stored_data.readings;

    var $form = $("#reading_enter_form");
    var $table_body = $("#reading_enter_table").find("tbody");

    var $inputs = $form.find('input');
    var $compass_input = $form.find('input[name="compass"]');
    var $shadow_input  = $form.find('input[name="shadow"]');

    var $control_buttons = $form.find(".compass_video_controls");


    $inputs.on("keypress", function (e) {
      if (e.which == 13) { // return key pressed
        e.preventDefault();
        $form.submit();
      }
    });

    $control_buttons.on("click", function (e) {
      e.preventDefault();
      // focus on suitable field
      $compass_input.val() ? $shadow_input.focus() : $compass_input.focus();
    });

    $form.on('submit', function (e) {
      e.preventDefault();

      compass_reading = parseFloat($compass_input.val());
      shadow_reading  = parseFloat($shadow_input.val());
      video_time = compass_video.currentTime;

      var reading = {
        "compass": compass_reading,
        "shadow":  shadow_reading,
        "time": video_time,
      };

      // store the reading
      readings.push(reading);

      // clear the form and focus on the first field
      $compass_input.val("").focus();
      $shadow_input.val("");

      // if possible guess the next compass value
      if (readings.length >= 2) {
        var last_readings = readings.slice(-2).map(function (i) {return parseFloat(i.compass);});
        var delta = last_readings[1] - last_readings[0];
        var next = (last_readings[1] + delta + 360) % 360;
        if (!isNaN(next)) {
          $compass_input.val(next);
          $shadow_input.focus();
        }
      }

      // display the reading in the table
      var $row = $("<tr />");
      $("<td />").text(seconds_to_hhssmmm(video_time)).appendTo($row);
      $("<td />").text(compass_reading + '°').appendTo($row);
      $("<td />").text(shadow_reading + '°').appendTo($row);
      $("<td />").text('').appendTo($row);
      $table_body.prepend($row);

    });



  })();



  $("#all_readings_entered").on("click", function (e) {
    e.preventDefault();

    var $button = $(this);

    $.ajax({
      type: "POST",
      url: $button.data("postUrl"),
      data: JSON.stringify(stored_data),
      success: function (data) { console.log("response: ", data); },
      // dataType: "json",
      beforeSend: function(xhr) {
        xhr.setRequestHeader("X-CSRFToken", $button.data("csrfToken"));
      }
    });
  });



});
