document.getElementById('capture').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  chrome.scripting.executeScript({
    target: {tabId: tab.id},
    func: () => document.body.innerText
  }, (results) => {
    const text = results && results[0] ? results[0].result : '';
    document.getElementById('out').value = text;
    navigator.clipboard.writeText(text);
  });
});
