// monitor/firmware/monitor.js

const WebSocket = require('ws');
const logger = require('../../backend/logger');

// Kreiraj WebSocket server na zasebnom portu (npr. 8081)
const wssMonitor = new WebSocket.Server({ port: 8081 }, () => {
  logger.info('Monitor server sluša na portu 8081');
});

wssMonitor.on('connection', (ws) => {
  logger.info('Monitor: nova konekcija uspostavljena');
  ws.on('message', (message) => {
    logger.info(`Monitor primio poruku: ${message}`);
  });
});

// Funkcija za broadcast log poruka svim spojenim monitor klijentima
function broadcastLog(logMessage) {
  wssMonitor.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ log: logMessage }));
    }
  });
}

module.exports = { broadcastLog };
