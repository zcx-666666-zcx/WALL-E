const DB_NAME = 'walleModelCache';
const STORE_NAME = 'models';
const DB_VERSION = 1;

const memoryCache = new Map();

function canUseIndexedDB() {
  return typeof window !== 'undefined' && 'indexedDB' in window;
}

function openDb() {
  if (!canUseIndexedDB()) return Promise.resolve(null);

  return new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'key' });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function getCachedBlob(key) {
  if (memoryCache.has(key)) return memoryCache.get(key);

  const db = await openDb();
  if (!db) return null;

  return new Promise((resolve) => {
    const transaction = db.transaction(STORE_NAME, 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.get(key);

    request.onsuccess = () => {
      const blob = request.result?.blob || null;
      if (blob) memoryCache.set(key, blob);
      resolve(blob);
    };
    request.onerror = () => resolve(null);
    transaction.oncomplete = () => db.close();
    transaction.onerror = () => db.close();
  });
}

async function setCachedBlob(key, blob, metadata = {}) {
  memoryCache.set(key, blob);

  const db = await openDb();
  if (!db) return;

  await new Promise((resolve) => {
    const transaction = db.transaction(STORE_NAME, 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    store.put({
      key,
      blob,
      metadata,
      updatedAt: Date.now(),
    });

    transaction.oncomplete = () => {
      db.close();
      resolve();
    };
    transaction.onerror = () => {
      db.close();
      resolve();
    };
  });
}

export async function deleteCachedBlob(key) {
  memoryCache.delete(key);

  const db = await openDb();
  if (!db) return;

  await new Promise((resolve) => {
    const transaction = db.transaction(STORE_NAME, 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    store.delete(key);

    transaction.oncomplete = () => {
      db.close();
      resolve();
    };
    transaction.onerror = () => {
      db.close();
      resolve();
    };
  });
}

export async function loadModelBlobWithCache(url, options = {}) {
  const cacheKey = options.cacheKey || url;
  const onStatus = options.onStatus || (() => {});
  const forceRefresh = options.forceRefresh === true;
  const cached = forceRefresh ? null : await getCachedBlob(cacheKey);

  if (cached) {
    onStatus('cached');
    return { blob: cached, source: 'cache' };
  }

  onStatus('network');
  const response = await fetch(url, { cache: forceRefresh ? 'no-store' : 'force-cache' });
  if (!response.ok) {
    throw new Error(`Model request failed: ${response.status}`);
  }

  const blob = await response.blob();
  await setCachedBlob(cacheKey, blob, {
    url,
    size: blob.size,
  });

  onStatus('stored');
  return { blob, source: 'network' };
}
