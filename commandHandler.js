// backend/commandHandler.js
const SerialPort = require('serialport');

// Open the port – adjust the device path/baudRate as needed.
const port = new SerialPort('/dev/ttyUSB0', { baudRate: 115200 }, (err) => {
  if (err) {
    console.error('Error opening port:', err);
  } else {
    console.log('Serial port opened successfully.');
  }
});

/**
 * Converts a keyboard command (e.g., 'w', 'a', 's', 'd')
 * to the protocol format expected by the Nucleo.
 *
 * Protocol example (per Bosch docs):
 *   [STX] <command> [ETX]
 * where STX = 0x02 and ETX = 0x03.
 */
function convertCommand(key) {
  // Define mapping – adjust letters as needed based on Bosch documentation.
  const commandMap = {
    'w': 'F', // Forward
    'a': 'L', // Left
    's': 'B', // Backward/Stop (modify if needed)
    'd': 'R'  // Right
  };

  const cmdLetter = commandMap[key.toLowerCase()];
  if (!cmdLetter) return null;

  // Create a Buffer with start and end markers.
  return Buffer.from([0x02, cmdLetter.charCodeAt(0), 0x03]);
}

/**
 * Sends the given keyboard command by converting it
 * and then writing it out via the serial port.
 */
function sendCommand(key) {
  const commandBuffer = convertCommand(key);
  if (!commandBuffer) {
    console.error('Invalid command received:', key);
    return;
  }
  port.write(commandBuffer, (err) => {
    if (err) {
      console.error('Error sending command:', err);
    } else {
      console.log('Command sent:', commandBuffer);
    }
  });
}

module.exports = { sendCommand };
