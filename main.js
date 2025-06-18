$(document).ready(function () {

  eel.init();
  // Animate header text
  $(".text").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  // Animate Siri message text
  $(".siri-message").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

  // SiriWave configuration
  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#ff0000",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });

  // Mic button click
  $("#MicBtn").click(function () {
    window.eel?.playAssistantSound();
    $("#Oval").hide();
    $("#SiriWave").show();
    window.eel?.takeAllCommands()();
  });

  // Cmd + J toggle SiriWave
  function doc_keyUp(e) {
    if (e.key === "j" && e.metaKey) {
      const isSiriWaveVisible = $("#SiriWave").is(":visible");

      if (isSiriWaveVisible) {
        $("#SiriWave").hide();
        $("#Oval").show();
      } else {
        window.eel?.playAssistantSound();
        $("#Oval").hide();
        $("#SiriWave").show();
        window.eel?.takeAllCommands();
      }
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);

  // Play assistant with message
  function PlayAssistant(message) {
    if (message !== "") {
      $("#Oval").hide();
      $("#SiriWave").show();
      eel.takeAllCommands(message);
      $("#chatbox").val("");
      $("#MicBtn").show();
      $("#SendBtn").hide();
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  // Toggle mic/send buttons based on input
  function ShowHideButton(message) {
    if (message.length === 0) {
      $("#MicBtn").show();
      $("#SendBtn").hide();
    } else {
      $("#MicBtn").hide();
      $("#SendBtn").show();
    }
  }

  // Input tracking
  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    console.log("Current chatbox input: ", message);
    ShowHideButton(message);
  });

  // Send message with Send button
  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  // Send message on Enter key
  $("#chatbox").keypress(function (e) {
    if (e.which === 13) {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });
});