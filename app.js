// backend/app.js
const express = require('express');
const bodyParser = require('body-parser');
const { sendCommand } = require('./commandHandler');

const app = express();
const PORT = 3000;

// Middleware to parse JSON bodies.
app.use(bodyParser.json());

// Serve static files from your dashboard folder.
app.use(express.static('dashboard'));

// Endpoint to receive commands from the web dashboard.
app.post('/api/command', (req, res) => {
  const { command } = req.body;
  if (!command) {
    return res.status(400).json({ error: 'No command provided' });
  }

  // Send the command to the hardware.
  sendCommand(command);
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log(`Backend server is running on port ${PORT}`);
});
