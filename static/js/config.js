async function loadConfig() {
    const configResponse = await fetch('/config');
    const config = await configResponse.json();
    return config;
}

async function initialize() {
    const config = await loadConfig();
    window.serverUrl = config.serverUrl;
}

initialize();
