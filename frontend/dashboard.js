// frontend/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
  // Uspostavi WebSocket konekciju prema backend serveru (prilagodi port ako je potrebno)
  const ws = new WebSocket(`ws://${window.location.hostname}:8080`);
  const statusDiv = document.getElementById('status');
  const logContainer = document.getElementById('log-container');
  
  ws.onopen = () => {
    statusDiv.innerText = 'Povezano na backend';
  };

  ws.onerror = (error) => {
    console.error('WebSocket greška:', error);
    statusDiv.innerText = 'WebSocket greška';
  };

  ws.onmessage = (event) => {
    let data = JSON.parse(event.data);
    console.log('Primljeno:', data);
    if (data.log) {
      // Ako poruka sadrži log, prikaži ga
      addLogEntry(data.log);
    } else if (data.status) {
      statusDiv.innerText = data.status;
    } else if (data.error) {
      statusDiv.innerText = `Greška: ${data.error}`;
    }
  };

  function addLogEntry(entry) {
    const p = document.createElement('p');
    p.innerText = entry;
    logContainer.appendChild(p);
  }

  // Rukovanje klikovima na dugmad za manuelnu kontrolu
  document.querySelectorAll('.controls button').forEach(button => {
    button.addEventListener('click', () => {
      const command = button.getAttribute('data-command');
      sendMoveCommand(command, 50); // zadana brzina 50
    });
  });

  // Rukovanje tipkovnicom – WASD za kontrolu
  document.addEventListener('keydown', (e) => {
    const validKeys = ['W', 'A', 'S', 'D'];
    if (validKeys.includes(e.key.toUpperCase())) {
      sendMoveCommand(e.key.toUpperCase(), 50);
    }
  });

  // Rukovanje promjenom KL vrijednosti
  document.getElementById('kl-update-btn').addEventListener('click', () => {
    const klValue = document.getElementById('kl-input').value;
    sendKLCommand(klValue);
  });

  function sendMoveCommand(direction, speed) {
    const command = {
      type: 'move',
      direction: direction,
      speed: speed
    };
    ws.send(JSON.stringify(command));
  }

  function sendKLCommand(value) {
    const command = {
      type: 'adjustKL',
      value: value
    };
    ws.send(JSON.stringify(command));
  }

  // Navigacija između kartica (Manual Control / Logs)
  document.getElementById('manual-control-tab').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('manual-control').style.display = 'block';
    document.getElementById('logs').style.display = 'none';
  });

  document.getElementById('logs-tab').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('manual-control').style.display = 'none';
    document.getElementById('logs').style.display = 'block';
  });
});
