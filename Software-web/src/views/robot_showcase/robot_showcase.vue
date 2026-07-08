<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { deleteCachedBlob, loadModelBlobWithCache } from '@/utils/modelCache';

const canvasWrap = ref(null);
const loading = ref(true);
const loadError = ref('');
const loadHint = ref('正在准备模型...');
const autoRotate = ref(true);
const wireframe = ref(false);
const modelStats = ref({
  meshes: 0,
  vertices: 0,
  size: '',
});

let renderer;
let scene;
let camera;
let controls;
let model;
let frameId;
let resizeObserver;
let disposed = false;
let defaultCameraPosition = null;
let defaultControlsTarget = null;

const modelUrl = `${import.meta.env.BASE_URL}models/robot-draco.glb?v=draco-placement-fix-1`;
const modelCacheKey = 'robot-draco.glb:v1:step-assembly-placement-fix';

const rotateLabel = computed(() => (autoRotate.value ? '停止旋转' : '自动旋转'));
const wireframeLabel = computed(() => (wireframe.value ? '实体显示' : '线框显示'));

const initScene = () => {
  if (!canvasWrap.value) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf6f8fb);

  const wrap = canvasWrap.value;
  const width = wrap.clientWidth || 800;
  const height = wrap.clientHeight || 520;

  camera = new THREE.PerspectiveCamera(42, width / height, 0.01, 100);
  camera.position.set(3.6, 2.4, 4.2);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  wrap.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.autoRotate = autoRotate.value;
  controls.autoRotateSpeed = 1.6;
  controls.minDistance = 1.6;
  controls.maxDistance = 8;

  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x9ba8b5, 2.2);
  scene.add(hemiLight);

  const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
  keyLight.position.set(4, 5, 3);
  keyLight.castShadow = true;
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0xffd29a, 1.1);
  fillLight.position.set(-3, 2, -2);
  scene.add(fillLight);

  const grid = new THREE.GridHelper(4.4, 22, 0xc4ccd7, 0xdce2ea);
  grid.position.y = -1.18;
  scene.add(grid);
};

const fitModel = (object) => {
  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxAxis = Math.max(size.x, size.y, size.z) || 1;
  const scale = 2.15 / maxAxis;

  object.position.sub(center);
  object.scale.multiplyScalar(scale);

  const fittedBox = new THREE.Box3().setFromObject(object);
  const fittedCenter = fittedBox.getCenter(new THREE.Vector3());
  const fittedSize = fittedBox.getSize(new THREE.Vector3());
  controls.target.copy(fittedCenter);
  controls.update();

  modelStats.value.size = `${size.x.toFixed(1)} x ${size.y.toFixed(1)} x ${size.z.toFixed(1)} mm`;
  camera.position.set(fittedSize.x * 1.05, fittedSize.y * 0.78, fittedSize.z * 1.28);
  camera.lookAt(fittedCenter);
  defaultCameraPosition = camera.position.clone();
  defaultControlsTarget = fittedCenter.clone();
};

const countModel = (object) => {
  let meshes = 0;
  let vertices = 0;
  object.traverse((node) => {
    if (!node.isMesh) return;
    meshes += 1;
    vertices += node.geometry?.attributes?.position?.count || 0;
    node.castShadow = true;
    node.receiveShadow = true;
    if (node.material) {
      node.material.roughness = 0.58;
      node.material.metalness = 0.15;
      node.material.needsUpdate = true;
    }
  });
  modelStats.value.meshes = meshes;
  modelStats.value.vertices = vertices;
};

const parseLoadedModel = async (blob) => {
  const loader = new GLTFLoader();
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath(`${import.meta.env.BASE_URL}draco/`);
  loader.setDRACOLoader(dracoLoader);
  const arrayBuffer = await blob.arrayBuffer();
  const gltf = await loader.parseAsync(arrayBuffer, modelUrl);
  dracoLoader.dispose();
  model = gltf.scene;
  model.name = 'WALL-E';
  countModel(model);
  fitModel(model);
  scene.add(model);
};

const loadModel = async () => {
  try {
    const result = await loadModelBlobWithCache(modelUrl, {
      cacheKey: modelCacheKey,
      onStatus: (status) => {
        if (status === 'cached') loadHint.value = '正在从本地缓存读取模型...';
        if (status === 'network') loadHint.value = '首次加载模型中，完成后会自动缓存...';
        if (status === 'stored') loadHint.value = '模型已写入本地缓存...';
      },
    });
    loadHint.value = result.source === 'cache' ? '已命中本地缓存，正在渲染...' : '下载完成，正在渲染...';
    await parseLoadedModel(result.blob);
  } catch (error) {
    try {
      loadHint.value = '检测到缓存异常，正在重新下载模型...';
      await deleteCachedBlob(modelCacheKey);
      const fallback = await loadModelBlobWithCache(modelUrl, {
        cacheKey: modelCacheKey,
        forceRefresh: true,
        onStatus: (status) => {
          if (status === 'network') loadHint.value = '正在重新下载模型...';
          if (status === 'stored') loadHint.value = '新模型已写入本地缓存...';
        },
      });
      await parseLoadedModel(fallback.blob);
      loadError.value = '';
    } catch (retryError) {
      loadError.value = '模型加载失败，请确认 robot.glb 已生成并可以访问。';
      console.error(retryError);
    }
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const resize = () => {
  if (!renderer || !camera || !canvasWrap.value) return;
  const width = canvasWrap.value.clientWidth || 800;
  const height = canvasWrap.value.clientHeight || 520;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};

const animate = () => {
  if (disposed || !renderer || !scene || !camera || !controls) return;
  frameId = requestAnimationFrame(animate);
  controls.autoRotate = autoRotate.value;
  controls.update();
  renderer.render(scene, camera);
};

const toggleRotate = () => {
  autoRotate.value = !autoRotate.value;
};

const toggleWireframe = () => {
  wireframe.value = !wireframe.value;
  if (!model) return;
  model.traverse((node) => {
    if (node.isMesh && node.material) {
      node.material.wireframe = wireframe.value;
      node.material.needsUpdate = true;
    }
  });
};

const resetView = () => {
  if (!controls || !camera) return;
  if (defaultCameraPosition && defaultControlsTarget) {
    camera.position.copy(defaultCameraPosition);
    controls.target.copy(defaultControlsTarget);
  }
  controls.update();
};

onMounted(async () => {
  disposed = false;
  initScene();
  await loadModel();
  if (disposed || !canvasWrap.value) return;
  resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvasWrap.value);
  window.addEventListener('resize', resize);
  animate();
});

onUnmounted(() => {
  disposed = true;
  if (frameId) cancelAnimationFrame(frameId);
  resizeObserver?.disconnect();
  window.removeEventListener('resize', resize);
  controls?.dispose();
  renderer?.dispose();
  if (renderer?.domElement?.parentNode) {
    renderer.domElement.parentNode.removeChild(renderer.domElement);
  }
});
</script>

<template>
  <div class="robot-page">
    <section class="viewer-shell">
      <div class="viewer-toolbar">
        <div>
          <p class="eyebrow">WALL-E 3D MODEL</p>
          <h2>机器人展示</h2>
        </div>
        <div class="toolbar-actions">
          <button type="button" @click="toggleRotate" :title="rotateLabel">
            <el-icon><Refresh /></el-icon>
            <span>{{ rotateLabel }}</span>
          </button>
          <button type="button" @click="toggleWireframe" :title="wireframeLabel">
            <el-icon><Grid /></el-icon>
            <span>{{ wireframeLabel }}</span>
          </button>
          <button type="button" @click="resetView" title="重置视角">
            <el-icon><Aim /></el-icon>
            <span>重置视角</span>
          </button>
        </div>
      </div>

      <div ref="canvasWrap" class="viewer-canvas">
        <div v-if="loading" class="viewer-state">{{ loadHint }}</div>
        <div v-if="loadError" class="viewer-state viewer-state--error">{{ loadError }}</div>
      </div>
    </section>

    <aside class="model-panel">
      <div class="panel-section">
        <p class="panel-label">模型来源</p>
        <strong>Wall-e_Assembly_NotForPrinting.STEP</strong>
        <span>已转换为网页可加载的 GLB 展示模型。</span>
      </div>
      <div class="panel-section stats-grid">
        <div>
          <span>网格</span>
          <strong>{{ modelStats.meshes }}</strong>
        </div>
        <div>
          <span>顶点</span>
          <strong>{{ modelStats.vertices.toLocaleString() }}</strong>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.robot-page {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 16px;
  min-height: calc(100vh - 132px);
  color: #172033;
}

.viewer-shell,
.model-panel {
  border: 1px solid rgba(20, 35, 60, 0.08);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 12px 32px rgba(28, 43, 68, 0.08);
}

.viewer-shell {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 560px;
  overflow: hidden;
  border-radius: 8px;
}

.viewer-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(20, 35, 60, 0.08);
}

.eyebrow {
  margin: 0 0 4px;
  color: #637089;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.viewer-toolbar h2 {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
  color: #101828;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.toolbar-actions button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 12px;
  border: 1px solid rgba(40, 59, 84, 0.16);
  border-radius: 7px;
  background: #ffffff;
  color: #26364f;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.18s, background 0.18s, transform 0.18s;
}

.toolbar-actions button:hover {
  border-color: rgba(38, 112, 255, 0.42);
  background: #f2f6ff;
}

.toolbar-actions button:active {
  transform: translateY(1px);
}

.viewer-canvas {
  position: relative;
  flex: 1;
  min-height: 480px;
  background:
    linear-gradient(180deg, rgba(245, 248, 252, 0.96), rgba(232, 238, 246, 0.96)),
    radial-gradient(circle at 48% 38%, rgba(255, 213, 139, 0.36), transparent 36%);
}

.viewer-canvas :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

.viewer-state {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #4b5c73;
  font-size: 14px;
  background: rgba(246, 248, 251, 0.72);
  z-index: 2;
}

.viewer-state--error {
  color: #b42318;
}

.model-panel {
  align-self: stretch;
  border-radius: 8px;
  padding: 18px;
}

.panel-section {
  padding: 0 0 18px;
  margin: 0 0 18px;
  border-bottom: 1px solid rgba(20, 35, 60, 0.08);
}

.panel-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: 0;
}

.panel-label,
.panel-section span {
  display: block;
  margin: 0 0 8px;
  color: #637089;
  font-size: 12px;
}

.panel-section strong {
  display: block;
  color: #101828;
  font-size: 16px;
  line-height: 1.4;
  word-break: break-word;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stats-grid div {
  padding: 12px;
  border-radius: 7px;
  background: #f6f8fb;
}

@media (max-width: 1080px) {
  .robot-page {
    grid-template-columns: 1fr;
  }

  .model-panel {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .panel-section {
    margin: 0;
    padding: 0;
    border-bottom: 0;
  }
}

@media (max-width: 720px) {
  .robot-page {
    min-height: auto;
  }

  .viewer-shell {
    min-height: 520px;
  }

  .viewer-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .toolbar-actions {
    justify-content: flex-start;
    width: 100%;
  }

  .toolbar-actions button {
    flex: 1 1 120px;
    justify-content: center;
  }

  .viewer-canvas {
    min-height: 410px;
  }

  .model-panel {
    grid-template-columns: 1fr;
  }
}
</style>
