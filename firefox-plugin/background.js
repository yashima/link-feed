// Define the default endpoint URL
const DEFAULT_ENDPOINT_URL = 'https://tools.pieper.dev/links/add';

browser.browserAction.onClicked.addListener(async (tab) => {  
  const url = tab.url;
  const endpointUrl = await getEndpoint(); // Use await to get the resolved value of the Promise
  browser.tabs.update({ url: `${endpointUrl}?url=${encodeURIComponent(url)}` });
});

async function getEndpoint() {
  const result = await browser.storage.local.get('endpoint');
  const endpoint = result.endpoint;
  if (endpoint) {
    return endpoint;
  } else {
    return DEFAULT_ENDPOINT_URL;
  }
}
