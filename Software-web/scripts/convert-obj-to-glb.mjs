import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';

globalThis.FileReader = class {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then((buffer) => {
      this.result = buffer;
      this.onloadend?.();
    });
  }

  readAsDataURL(blob) {
    blob.arrayBuffer().then((buffer) => {
      this.result = `data:${blob.type || 'application/octet-stream'};base64,${Buffer.from(buffer).toString('base64')}`;
      this.onloadend?.();
    });
  }
};

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');
const inputPath = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.resolve(projectRoot, 'public', 'models', 'robot-full.obj');
const outputPath = process.argv[3]
  ? path.resolve(process.argv[3])
  : path.resolve(projectRoot, 'public', 'models', 'robot.glb');

const objText = await fs.readFile(inputPath, 'utf8');
const loader = new OBJLoader();
const model = loader.parse(objText);

const robotMaterial = new THREE.MeshStandardMaterial({
  color: 0xd2a03c,
  roughness: 0.68,
  metalness: 0.12,
  side: THREE.DoubleSide,
});

let meshes = 0;
let vertices = 0;
model.traverse((node) => {
  if (!node.isMesh) return;
  meshes += 1;
  vertices += node.geometry?.attributes?.position?.count || 0;
  node.material = robotMaterial;
  node.castShadow = true;
  node.receiveShadow = true;
});

const sourceBox = new THREE.Box3().setFromObject(model);
const sourceSize = sourceBox.getSize(new THREE.Vector3());
const sourceCenter = sourceBox.getCenter(new THREE.Vector3());
const scale = 2.4 / Math.max(sourceSize.x, sourceSize.y, sourceSize.z || 1);

model.position.sub(sourceCenter);
model.scale.setScalar(scale);
model.name = 'WALL-E Robot STEP Assembly';

const scene = new THREE.Scene();
scene.add(model);

const exporter = new GLTFExporter();
const glb = await exporter.parseAsync(scene, { binary: true });
await fs.writeFile(outputPath, Buffer.from(glb));

const stat = await fs.stat(outputPath);
console.log(`Read ${inputPath}`);
console.log(`Meshes: ${meshes}, vertices: ${vertices}`);
console.log(`Source size: ${sourceSize.x.toFixed(1)} x ${sourceSize.y.toFixed(1)} x ${sourceSize.z.toFixed(1)} mm`);
console.log(`Wrote ${outputPath} (${(stat.size / 1024 / 1024).toFixed(2)} MB)`);
