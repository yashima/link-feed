const DEFAULT_ENDPOINT_URL = 'https://tools.pieper.dev/links/add';

function storeEndpoint() {

  function getEndpoint() {
    const endpoint = document.querySelector("#endpoint-url");
    return endpoint.value;
  }
  browser.storage.local.set({ endpoint: getEndpoint() });

}

function resetEndpoint(){
  browser.storage.local.set({ endpoint: DEFAULT_ENDPOINT_URL });
  const endpoint = document.querySelector("#endpoint-url");  
  endpoint.value = DEFAULT_ENDPOINT_URL;
}


function updateUI(restoredSettings) {
  const endpoint = document.querySelector("#endpoint-url");  
  if (restoredSettings.hasOwnProperty("endpoint")) {
    // Use the stored value
    endpoint.value = restoredSettings.endpoint;
  } else {
    // Use a default value
    endpoint.value = DEFAULT_ENDPOINT_URL;
  }
}

function onError(e) {
  console.error(e);
}

const gettingStoredSettings = browser.storage.local.get();
gettingStoredSettings.then(updateUI, onError);

const saveButton = document.querySelector("#save-button");
saveButton.addEventListener("click", storeEndpoint);

const resetButton = document.querySelector("#reset-button");
resetButton.addEventListener("click", resetEndpoint);