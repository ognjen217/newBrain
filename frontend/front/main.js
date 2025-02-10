// Periodično dohvataj telemetriju
function fetchTelemetry() {
  fetch('/telemetry')
    .then(response => response.json())
    .then(data => {
      document.getElementById('motorSpeed').innerText = data.motorSpeed || '-';
      document.getElementById('steeringAngle').innerText = data.steeringAngle || '-';
      document.getElementById('command').innerText = data.command || '-';
    })
    .catch(error => console.error('Greška pri dobijanju telemetrije:', error));
}

// Osveži video feed (dodaj query parametar da se izbegne keširanje)
function updateVideoFeed() {
  var img = document.getElementById("cameraFeed");
  img.src = "latest.jpg?timestamp=" + new Date().getTime();
}

// Dodaj osluškivanje tastera za WASD (manual control)
document.addEventListener('keydown', function(event) {
  var key = event.key.toLowerCase();
  if (['w', 'a', 's', 'd'].includes(key)) {
    fetch('/manual-control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: key })
    })
    .then(response => response.json())
    .then(data => console.log("Manual control:", data))
    .catch(error => console.error("Error:", error));
  }
});

// Pokrećemo osvežavanje svakih 2 sekunde za telemetriju i svakih 100 ms za video feed
setInterval(fetchTelemetry, 2000);
setInterval(updateVideoFeed, 100);
