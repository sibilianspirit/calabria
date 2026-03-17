#!/usr/bin/env node
/**
 * generate-image.js — kie.ai image generation + WP upload (bestofcalabria.com)
 * Usage: node generate-image.js --prompt "..." --slug "page-slug" --alt "alt text" [--caption "..."] [--lang pl|en]
 *
 * Flow:
 *   1. POST kie.ai createTask → taskId (resolution: 1K)
 *   2. Poll recordInfo co 5s (maks. 12 prób)
 *   3. Pobierz obraz → /tmp/boc_[slug].jpg
 *   4. Resize → 1024x576 WebP → /tmp/boc_[slug].webp
 *   5. Upload do WP media
 *   6. Wypisz gotowy blok Gutenberg do wklejenia w treść
 */

const https = require('https');
const http  = require('http');
const fs    = require('fs');
const path  = require('path');

// ── Config ──────────────────────────────────────────────────────────────────
const KIE_API_KEY   = '57e720524cb22add43026bd6ba52ad1a';
const KIE_BASE      = 'https://api.kie.ai/api/v1/jobs';
const WP_HOST       = 'bestofcalabria.com';
const WP_BASE       = `https://${WP_HOST}/wp-json/wp/v2`;
const WP_USER       = 'admin';
const WP_PASS       = 'JwGw oBQ1 yaHo hXeg oadm Kx86';
const WP_AUTH       = 'Basic ' + Buffer.from(`${WP_USER}:${WP_PASS}`).toString('base64');
const SHARP_PATH    = '/home/sibilian/.npm-global/lib/node_modules/sharp';
const POLL_INTERVAL = 5000;
const MAX_ATTEMPTS  = 12;
// ────────────────────────────────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { lang: 'pl' };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--prompt')    result.prompt    = args[++i];
    if (args[i] === '--slug')      result.slug      = args[++i];
    if (args[i] === '--alt')       result.alt       = args[++i];
    if (args[i] === '--caption')   result.caption   = args[++i];
    if (args[i] === '--lang')      result.lang      = args[++i];
    if (args[i] === '--edit-from') result.editFrom  = args[++i]; // URL obrazu do edycji
  }
  if (!result.prompt || !result.slug || !result.alt) {
    console.error('Użycie:');
    console.error('  Generowanie: node generate-image.js --prompt "..." --slug "slug" --alt "alt" [--caption "..."]');
    console.error('  Edycja:      node generate-image.js --prompt "..." --slug "slug" --alt "alt" --edit-from "URL" [--caption "..."]');
    process.exit(1);
  }
  return result;
}

function kieRequest(method, endpoint, body) {
  return new Promise((resolve, reject) => {
    const url  = new URL(KIE_BASE + endpoint);
    const data = body ? JSON.stringify(body) : null;
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        'Authorization': `Bearer ${KIE_API_KEY}`,
        'Content-Type': 'application/json',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {})
      }
    };
    const req = https.request(options, res => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try { resolve(JSON.parse(raw)); }
        catch { reject(new Error('Błąd parsowania odpowiedzi kie.ai: ' + raw)); }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const proto = url.startsWith('https') ? https : http;
    const file  = fs.createWriteStream(dest);
    proto.get(url, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close();
        return downloadFile(res.headers.location, dest).then(resolve).catch(reject);
      }
      res.pipe(file);
      file.on('finish', () => file.close(resolve));
    }).on('error', err => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function createTask(prompt, editFrom = null) {
  if (editFrom) {
    // Tryb edycji — google/nano-banana-edit
    console.log('→ Tworzę task kie.ai (edycja obrazu)...');
    console.log('  Źródło:', editFrom);
    const res = await kieRequest('POST', '/createTask', {
      model: 'google/nano-banana-edit',
      input: {
        prompt,
        image_urls: [editFrom],
        output_format: 'jpeg',
        image_size: '16:9'
      }
    });
    if (res.code !== 200) throw new Error('kie.ai createTask error: ' + (res.msg || JSON.stringify(res)));
    console.log('  taskId:', res.data.taskId);
    return res.data.taskId;
  } else {
    // Tryb generowania — nano-banana-2
    console.log('→ Tworzę task kie.ai (generowanie 1K)...');
    const res = await kieRequest('POST', '/createTask', {
      model: 'nano-banana-2',
      input: { prompt, aspect_ratio: '16:9', resolution: '1K', output_format: 'jpg' }
    });
    if (res.code !== 200) throw new Error('kie.ai createTask error: ' + (res.msg || JSON.stringify(res)));
    console.log('  taskId:', res.data.taskId);
    return res.data.taskId;
  }
}

async function pollUntilDone(taskId) {
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    await sleep(POLL_INTERVAL);
    process.stdout.write(`  Polling ${attempt}/${MAX_ATTEMPTS}... `);
    let res;
    try {
      res = await kieRequest('GET', `/recordInfo?taskId=${taskId}`);
    } catch (networkErr) {
      // Ignoruj przejściowe błędy sieci (ETIMEDOUT, ECONNRESET itp.) i kontynuuj
      process.stdout.write(`błąd sieci (${networkErr.code || networkErr.message}), próba ponowna...\n`);
      continue;
    }
    const state = res.data?.state || res.data?.status || 'unknown';
    process.stdout.write(`stan: ${state}\n`);

    if (['success','completed','SUCCESS','COMPLETED'].includes(state)) {
      let imageUrl = '';
      try {
        const parsed = typeof res.data.resultJson === 'string'
          ? JSON.parse(res.data.resultJson)
          : res.data.resultJson;
        imageUrl = parsed.resultUrls?.[0] || parsed.images?.[0] || '';
      } catch {}
      if (!imageUrl) throw new Error('Brak imageUrl w odpowiedzi kie.ai');
      return imageUrl;
    }
    if (['failed','FAILED','error','ERROR'].includes(state)) {
      throw new Error('kie.ai task failed: ' + state);
    }
  }
  // Zwróć taskId do ręcznego sprawdzenia
  throw new Error(`Timeout po ${MAX_ATTEMPTS} próbach. Sprawdź ręcznie:\nGET ${KIE_BASE}/recordInfo?taskId=${taskId}`);
}

async function processImage(srcPath, destPath) {
  const sharp = require(SHARP_PATH);
  // 1K = 1024x576 (16:9)
  await sharp(srcPath)
    .resize(1024, 576, { fit: 'cover' })
    .webp({ quality: 85 })
    .toFile(destPath);
  console.log('  Obraz gotowy:', destPath);
}

async function uploadToWP(filePath, slug) {
  const fileName = `boc-${slug}.webp`;
  const fileData = fs.readFileSync(filePath);

  return new Promise((resolve, reject) => {
    const options = {
      hostname: WP_HOST,
      path: '/wp-json/wp/v2/media',
      method: 'POST',
      headers: {
        'Authorization': WP_AUTH,
        'Content-Type': 'image/webp',
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'Content-Length': fileData.length
      }
    };
    const req = https.request(options, res => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(raw);
          if (json.id) {
            console.log(`  Upload OK: media ID ${json.id}`);
            resolve(json);
          } else {
            reject(new Error('WP upload error: ' + raw));
          }
        } catch { reject(new Error('WP upload parse error: ' + raw)); }
      });
    });
    req.on('error', reject);
    req.write(fileData);
    req.end();
  });
}

async function getMediaSizes(mediaId) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: WP_HOST,
      path: `/wp-json/wp/v2/media/${mediaId}`,
      method: 'GET',
      headers: { 'Authorization': WP_AUTH }
    };
    const req = https.request(options, res => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try { resolve(JSON.parse(raw)); }
        catch { reject(new Error('WP media parse error: ' + raw)); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function buildGutenbergBlock(mediaId, imageUrl, alt, caption) {
  const cap = caption ? `\n<figcaption class="wp-element-caption"><em>${caption}</em></figcaption>` : '';
  return [
    `<!-- wp:image {"id":${mediaId},"sizeSlug":"large","linkDestination":"none","align":"center"} -->`,
    `<figure class="wp-block-image aligncenter size-large"><img src="${imageUrl}" alt="${alt}" class="wp-image-${mediaId}"/>${cap}</figure>`,
    `<!-- /wp:image -->`
  ].join('\n');
}

async function main() {
  const { prompt, slug, alt, caption, lang, editFrom } = parseArgs();
  const tmpJpg  = `/tmp/boc_${slug}.jpg`;
  const tmpWebp = `/tmp/boc_${slug}.webp`;

  try {
    // 1. Utwórz task
    const taskId = await createTask(prompt, editFrom);

    // 2. Polling
    console.log('→ Czekam na wygenerowanie obrazu...');
    const imageUrl = await pollUntilDone(taskId);
    console.log('  URL źródłowy:', imageUrl);

    // 3. Pobierz
    console.log('→ Pobieram obraz...');
    await downloadFile(imageUrl, tmpJpg);

    // 4. Resize → WebP 1024×576
    console.log('→ Konwertuję do WebP 1024×576...');
    await processImage(tmpJpg, tmpWebp);
    fs.unlinkSync(tmpJpg);

    // 5. Upload do WP
    console.log('→ Uploading do WordPress...');
    const media = await uploadToWP(tmpWebp, slug);

    // 6. Pobierz sizes (large URL)
    const mediaData = await getMediaSizes(media.id);
    const largeUrl  = mediaData.media_details?.sizes?.large?.source_url
                   || mediaData.media_details?.sizes?.full?.source_url
                   || mediaData.source_url;

    // 7. Wypisz blok Gutenberg
    const block = buildGutenbergBlock(media.id, largeUrl, alt, caption);

    console.log('\n✅ GOTOWE');
    console.log('   Media ID:', media.id);
    console.log('   URL:', largeUrl);
    console.log('\n── BLOK GUTENBERG ──────────────────────────────────────');
    console.log(block);
    console.log('────────────────────────────────────────────────────────\n');

    // Sprzątanie
    try { fs.unlinkSync(tmpWebp); } catch {}

  } catch (err) {
    console.error('❌ Błąd:', err.message);
    process.exit(1);
  }
}

main();
