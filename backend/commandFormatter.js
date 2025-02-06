// backend/commandFormatter.js

function formatCommand(command) {
  // Pretpostavljeni Bosch protokol:
  // [Header][CommandID][PayloadLength][Payload][Checksum]
  // Primjer: za komandu 'move' i 'adjustKL'

  // Header – primjer, 0xAA
  const header = Buffer.from([0xAA]);
  let commandId;
  let payload = Buffer.alloc(0);

  switch (command.type) {
    case 'move': {
      // Komanda kretanja – CommandID 0x01 (hipotetički)
      commandId = Buffer.from([0x01]);
      // Mapiranje smjera (npr. 'W', 'A', 'S', 'D')
      const directions = { 'W': 0x57, 'A': 0x41, 'S': 0x53, 'D': 0x44 };
      const directionCode = directions[command.direction] || 0x00;
      // Pretpostavimo da brzina (speed) ide kao jedan bajt (0-100)
      payload = Buffer.from([directionCode, command.speed]);
      break;
    }
    case 'adjustKL': {
      // Komanda za promjenu KL vrijednosti – CommandID 0x02 (hipotetički)
      commandId = Buffer.from([0x02]);
      // Pretvaranje vrijednosti u broj i slanje kao dva bajta
      let klValue = parseInt(command.value, 10);
      payload = Buffer.from([ (klValue >> 8) & 0xFF, klValue & 0xFF ]);
      break;
    }
    default:
      throw new Error('Nepoznata komanda');
  }

  // PayloadLength – broj bajtova u payloadu
  const payloadLength = Buffer.from([payload.length]);

  // Jednostavan checksum: suma svih prethodnih bajtova modulo 256
  let checksumVal = header[0] + commandId[0] + payloadLength[0] + payload.reduce((sum, byte) => sum + byte, 0);
  const checksum = Buffer.from([checksumVal % 256]);

  // Spajanje svih segmenata
  return Buffer.concat([header, commandId, payloadLength, payload, checksum]);
}

module.exports = { formatCommand };
