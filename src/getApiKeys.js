let apiKey;
let keys;

async function initializeKeys() {
    const { invoke } = window.__TAURI__.tauri;
    keys = await invoke('get_keys');
    apiKey = keys[0].key;
}

export { apiKey, keys, initializeKeys };
