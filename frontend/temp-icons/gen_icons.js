const sharp = require('sharp');
const fs = require('fs');

const svgFile = '../src/assets/logo.svg';

const sizes = [
  { size: 180, name: 'apple-touch-icon' },
  { size: 192, name: 'logo-192' },
  { size: 512, name: 'logo-512' }
];

(async () => {
  try {
    // Read SVG and strip the border-radius for solid square iOS background requirement
    let svgContent = fs.readFileSync(svgFile, 'utf8');
    // Remove rx="128" to produce a solid square background
    svgContent = svgContent.replace(/rx="128"/g, '');
    const svgBuffer = Buffer.from(svgContent);

    for (const { size, name } of sizes) {
      const pngFile = `../src/assets/${name}.png`;
      await sharp(svgBuffer)
        .resize(size, size)
        .png()
        .toFile(pngFile);
      console.log(`Created ${pngFile}`);
    }
  } catch (e) {
    console.error(`Failed icon generation:`, e);
  }
})();
