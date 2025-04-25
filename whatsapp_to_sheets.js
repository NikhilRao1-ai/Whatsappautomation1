const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

// Google Sheets Setup
const SHEET_ID = '1c2qwMEFSx_XwnN7sBb5mcEq1GGYYK_omxAtEW9o7VUc';  // Your Google Sheets ID
const auth = new google.auth.GoogleAuth({
  keyFile: 'credentials.json',  // Path to your Google credentials file
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});
const sheets = google.sheets({ version: 'v4', auth });

// Append data to Google Sheets
async function appendToSheet(data) {
  const sheetName = '97477361067';  // Replace with your sheet name if different
  await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: `${sheetName}!A1`,
    valueInputOption: 'RAW',
    resource: { values: [data] },
  });
}

// WhatsApp Client Setup
const client = new Client({
  authStrategy: new LocalAuth(),
});

client.on('qr', (qr) => {
  qrcode.generate(qr, { small: true });
});

client.on('ready', async () => {
  console.log('✅ WhatsApp bot is ready!');
  
  // Get all chats
  const chats = await client.getChats();
  
  // Specify the contacts you want to fetch messages from
  const targetContacts = [
    '+971582763078',
    '+971522544032',
    '+919580274820',
    '+917022204772',
    // Add more contacts here...
  ];

  // Iterate over each chat
  for (let chat of chats) {
    if (targetContacts.includes(chat.id._serialized)) {
      console.log(`Fetching messages from ${chat.name || chat.id._serialized}...`);
      
      // Fetch messages
      const messages = await chat.fetchMessages({ limit: 1000 });

      // Process each message
      for (let msg of messages) {
        let logData = [new Date(msg.timestamp * 1000).toLocaleString(), chat.name || 'Unknown', msg.body || 'Media', ''];

        // If the message has media, download it
        if (msg.hasMedia) {
          try {
            const media = await msg.downloadMedia();
            const filename = `${Date.now()}_${msg.from}.${media.mimetype.split('/')[1]}`;
            const filePath = path.join(__dirname, 'downloads', filename);

            // Ensure 'downloads' folder exists
            if (!fs.existsSync(path.join(__dirname, 'downloads'))) {
              fs.mkdirSync(path.join(__dirname, 'downloads'));
            }

            // Save media to disk
            fs.writeFileSync(filePath, media.data, 'base64');
            logData[3] = `Saved: downloads/${filename}`;
          } catch (error) {
            console.error('Error downloading media:', error);
          }
        }

        // Log the message and media info to Google Sheets
        await appendToSheet(logData);
      }
    }
  }
});

client.initialize();
