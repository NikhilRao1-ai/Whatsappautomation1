const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { headless: true }
});

// Show QR Code for login
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    console.log('📱 Scan the QR code to log in to WhatsApp...');
});

// Once client is ready
client.on('ready', () => {
    console.log('✅ WhatsApp client is ready and listening for new messages...');
});

// Listen for new incoming messages
client.on('message', async (msg) => {
    try {
        const contact = await msg.getContact();
        const chat = await msg.getChat();
        const contactName = contact.pushname || contact.number || chat.name || msg.from;
        const timestamp = new Date(msg.timestamp * 1000).toISOString();
        const text = msg.body || '';
        const hasMedia = msg.hasMedia;

        console.log(`\n📩 New message from ${contactName} (${msg.from})`);
        console.log(`🕒 Timestamp: ${timestamp}`);
        console.log(`💬 Text: ${text}`);
        console.log(`📎 Has Media: ${hasMedia}`);

        // If the message has media, download and display info
        if (hasMedia) {
            const media = await msg.downloadMedia();

            if (media) {
                const extension = media.mimetype.split('/')[1].split(';')[0];
                const fileName = `media-${Date.now()}.${extension}`;
                const filePath = path.join(__dirname, 'downloads');

                // Create downloads directory if not exists
                if (!fs.existsSync(filePath)) fs.mkdirSync(filePath);

                // Save media to file
                fs.writeFileSync(path.join(filePath, fileName), media.data, 'base64');

                console.log(`📂 Saved Media: ${fileName}`);
                console.log(`📦 MIME Type: ${media.mimetype}`);
                console.log(`📏 Size: ${Buffer.from(media.data, 'base64').length} bytes`);
            } else {
                console.log('⚠️ Failed to download media (maybe expired)');
            }
        }

        console.log('---');

    } catch (err) {
        console.error('❌ Error processing message:', err.message);
    }
});

// Start the client
client.initialize();