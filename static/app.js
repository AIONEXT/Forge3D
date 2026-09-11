import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const $ = id => document.getElementById(id);
let PRINTERS = [], MATERIALS = [], lastBundle = null, autoRot = true, wire = false;

// ---------- 3D scene ----------
const canvas = $('c'), view = $('viewport');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
const scene = new THREE.Scene();
scene.background = null;
const cam = new THREE.PerspectiveCamera(42, 1, 1, 5000);
cam.position.set(220, 180, 260);
const ctl = new OrbitControls(cam, renderer.domElement);
ctl.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x223344, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(200, 300, 150); scene.add(key);
const fill = new THREE.DirectionalLight(0xf0883e, 0.5); fill.position.set(-200, 100, -150); scene.add(fill);
const grid = new THREE.GridHelper(400, 20, 0x30363d, 0x21262d); scene.add(grid);
let mesh = null;

function resize() {
  const w = view.clientWidth, h = view.clientHeight;
  renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(view); resize();

function showSTL(url, color = 0xf0883e) {
  new STLLoader().load(url, geo => {
    geo.computeVertexNormals();
    if (mesh) { scene.remove(mesh); mesh.geometry.dispose(); }
    const mat = new THREE.MeshStandardMaterial({ color, metalness: 0.15, roughness: 0.55, wireframe: wire });
    mesh = new THREE.Mesh(geo, mat);
    geo.computeBoundingBox();
    const c = geo.boundingBox.getCenter(new THREE.Vector3());
    mesh.position.sub(c); mesh.position.y += geo.boundingBox.getSize(new THREE.Vector3()).y / 2;
    scene.add(mesh);
    ctl.target.set(0, 60, 0); ctl.update();
  });
}
(function loop() { requestAnimationFrame(loop); if (autoRot && mesh) mesh.rotation.y += 0.008; ctl.update(); renderer.render(scene, cam); })();

$('rot').onclick = () => { autoRot = !autoRot; $('rot').textContent = autoRot ? '🔁 Auto-rotate' : '⏸ Paused'; };
$('wire').onclick = () => { wire = !wire; if (mesh) mesh.material.wireframe = wire; };
$('shot').onclick = () => {
  renderer.render(scene, cam);
  const a = document.createElement('a');
  a.download = (lastBundle?.listing.sku || 'product') + '-photo.png';
  a.href = renderer.domElement.toDataURL('image/png'); a.click();
};

// ---------- data ----------
async function init() {
  PRINTERS = await (await fetch('/api/printers')).json();
  MATERIALS = await (await fetch('/api/materials')).json();
  $('printer').innerHTML = PRINTERS.map(p =>
    `<option value="${p.id}">${p.name} — ${p.build.join('×')}mm ${p.enclosed ? '· enclosed' : ''}</option>`).join('');
  $('material').innerHTML = MATERIALS.map(m =>
    `<option value="${m.id}">${m.name} — $${m.price_usd_kg}/kg · ${m.finish}</option>`).join('');
  checkCompat();
  $('printer').onchange = $('material').onchange = checkCompat;
}
function checkCompat() {
  const p = PRINTERS.find(x => x.id === $('printer').value), m = MATERIALS.find(x => x.id === $('material').value);
  if (!p || !m) return;
  let ok = true, msg = 'Compatible.';
  if (m.id === 'resin' && p.tech !== 'MSLA') { ok = false; msg = `⛔ ${m.name} needs a resin printer — ${p.name} is ${p.tech}.`; }
  if (p.tech === 'MSLA' && m.id !== 'resin') { ok = false; msg = `⛔ ${p.name} is resin-only.`; }
  if (m.needs_enclosure && !p.enclosed) { ok = false; msg = `⚠️ ${m.name} wants enclosed (${p.name} is open). Use PLA/PETG or switch printer.`; }
  if (ok) msg = `✅ ${p.name} + ${m.name} · ${m.print_temp ? m.print_temp + '°C' : 'resin'} · ${m.desc}`;
  const el = $('compat'); el.textContent = msg; el.className = 'compat ' + (ok ? 'ok' : 'bad');
}

$('scale').oninput = e => $('scaleVal').textContent = Math.round(e.target.value * 100) + '%';
$('margin').oninput = e => $('marginVal').textContent = Math.round(e.target.value * 100) + '%';
document.querySelectorAll('[data-ex]').forEach(b => b.onclick = () => { $('desc').value = b.dataset.ex; });

const STEPS = ['Interpret', 'Generate mesh', 'Validate', 'Slice + cost', 'Commercial pack'];
function steps(state) {
  $('steps').innerHTML = STEPS.map((s, i) => {
    const cls = i < state ? 'step done' : i === state ? 'step on' : 'step';
    return `<span class="${cls}">${i < state ? '✓' : '●'} ${s}</span>`;
  }).join('');
}

// ---------- run ----------
$('run').onclick = async () => {
  steps(0);
  const body = {
    description: $('desc').value, printer_id: $('printer').value,
    material_id: $('material').value, quality_id: $('quality').value,
    scale: parseFloat($('scale').value), margin: parseFloat($('margin').value),
  };
  let prog = setInterval(() => steps(Math.min(4, Math.floor(Math.random() * 5))), 350);
  try {
    const r = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const b = await r.json();
    if (b.error) throw new Error(b.error);
    clearInterval(prog); steps(5); lastBundle = b;
    render(b);
  } catch (e) { clearInterval(prog); steps(0); alert('Error: ' + e.message); }
};

function render(b) {
  $('triCount').textContent = `${b.validation.triangles.toLocaleString()} triangles · ${b.validation.volume_cm3} cm³`;
  showSTL(b.files.stl);
  const v = b.validation;
  $('validation').innerHTML = `
    <div class="card">${v.compatible ? '<span class="pass">✓</span>' : '<span class="fail">✗</span>'} <b>Material check:</b> ${v.compat_msg}</div>
    <div class="card">${v.fits_bed ? '<span class="pass">✓</span>' : '<span class="fail">✗</span>'} <b>Size:</b> ${v.bed_msg} Final ${v.dims_final_mm.join(' × ')} mm</div>
    <div class="card">🧾 <b>Spec:</b> ${b.spec.category.replaceAll('_', ' ')} · style ${b.spec.style} · ${b.estimate.quality_label} · walls ${b.spec.wall_mm}mm · infill ${b.spec.infill_pct}%</div>`;
  const e = b.estimate, L = b.listing;
  $('price').innerHTML = `
    <div class="stat"><div class="v">$${L.price}</div><div class="k">SALE PRICE</div></div>
    <div class="stat"><div class="v">$${e.unit_cost}</div><div class="k">UNIT COST</div></div>
    <div class="stat"><div class="v">${e.weight_g}g</div><div class="k">${e.hours}h PRINT</div></div>
    <div class="stat"><div class="v">${Math.round(L.margin * 100)}%</div><div class="k">MARGIN · ${L.sku}</div></div>`;
  $('listing').innerHTML = `
    <div class="card"><h4>🏷️ ${L.title}</h4>
      <div>${L.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div></div>
    <div class="card"><h4>✨ Bullets</h4><ul>${L.bullets.map(x => `<li>${x}</li>`).join('')}</ul></div>
    <div class="card"><h4>📝 Description</h4>${L.description.replaceAll('\n', '<br>')}</div>
    <div class="card"><h4>✅ Sale checklist</h4>${L.checklist.map(c => `✓ ${c.item}`).join('<br>')}
      <br><br>💰 Material $${e.material_cost} + machine $${e.machine_cost} · compare-at $${L.compare_at} · slug <code>${L.seo_slug}</code></div>`;
  $('dlStl').disabled = $('dlJson').disabled = $('dlPage').disabled = false;
  $('dlStl').onclick = () => window.location = b.files.stl;
  $('dlJson').onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(b, null, 2)], { type: 'application/json' }));
    a.download = L.sku + '-listing.json'; a.click();
  };
  $('dlPage').onclick = () => {
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>${L.title}</title></head>
      <body style="font-family:system-ui;max-width:640px;margin:40px auto">
      <h1>${L.title}</h1><p><b>$${L.price}</b> <s>$${L.compare_at}</s> · SKU ${L.sku}</p>
      <ul>${L.bullets.map(x => `<li>${x}</li>`).join('')}</ul><p>${L.description.replaceAll('\n', '<br>')}</p>
      <p>${L.tags.map(t => `#${t.replaceAll(' ', '')}`).join(' ')}</p></body></html>`;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
    a.download = L.sku + '-sale-page.html'; a.click();
  };
}

$('boost').onclick = async () => {
  if (!lastBundle) return alert('Run the generator first.');
  $('boostOut').textContent = 'Contacting AI…';
  const r = await fetch('/api/copy-boost', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ listing: lastBundle.listing }) });
  const j = await r.json();
  $('boostOut').textContent = j.ok ? j.text : j.msg;
};

init();
steps(5);
