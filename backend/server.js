// backend/server.js

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const SerialPort = require('serialport');
const { formatCommand } = require('./commandFormatter');
const logger = require('./logger');

// Import monitor broadcast funkcije (putanja prilagoditi stvarnoj strukturi)
const { broadcastLog } = require('../monitor/firmware/monitor');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Konfiguracija serijske komunikacije – prilagodi port i brzinu prema hardveru
const portName = '/dev/ttyUSB0';
const serialPort = new SerialPort(portName, { baudRate: 115200 });

serialPort.on('open', () => {
  logger.info(`Serial port ${portName} otvoren`);
});

serialPort.on('error', (err) => {
  logger.error(`Greška na serijskom portu: ${err.message}`);
});

wss.on('connection', (ws) => {
  logger.info('Nova WebSocket konekcija uspostavljena');

  ws.on('message', (message) => {
    logger.info(`Primljena poruka: ${message}`);
    try {
      // Očekujemo JSON format od frontenda
      const command = JSON.parse(message);

      // Formatiraj komandu prema Bosch protokolu
      const formattedCommand = formatCommand(command);

      // Pošalji formatiranu komandu na serijski port
      serialPort.write(formattedCommand, (err) => {
        if (err) {
          logger.error(`Greška pri slanju komande: ${err.message}`);
          ws.send(JSON.stringify({ error: 'Neuspješno slanje komande na hardver' }));
        } else {
          ws.send(JSON.stringify({ status: 'Komanda uspješno poslana' }));
          broadcastLog(`Poslana komanda: ${command.type}`);
        }
      });
    } catch (err) {
      logger.error(`Greška pri obradi poruke: ${err.message}`);
      ws.send(JSON.stringify({ error: 'Neispravan format komande' }));
    }
  });
});

// Poslužuje statičke fajlove iz frontend foldera
app.use(express.static('frontend'));

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  logger.info(`Server sluša na portu ${PORT}`);
});
