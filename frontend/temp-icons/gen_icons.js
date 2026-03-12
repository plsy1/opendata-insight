const sharp = require('sharp');
const fs = require('fs');

const svgFile = '../src/assets/logo.svg';

const sizes = [192, 512]; // sizes requested in manifest

(async () => {
  for (const size of sizes) {
    const pngFile = `../src/assets/logo-${size}.png`;
    try {
      await sharp(svgFile)
        .resize(size, size)
        .png()
        .toFile(pngFile);
      console.log(`Created ${pngFile}`);
    } catch (e) {
      console.error(`Failed for size ${size}:`, e);
    }
  }
})();
