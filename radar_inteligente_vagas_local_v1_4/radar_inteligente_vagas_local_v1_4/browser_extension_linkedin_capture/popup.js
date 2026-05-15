document.getElementById('copy').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  const [{result}] = await chrome.scripting.executeScript({
    target: {tabId: tab.id},
    func: () => document.body.innerText
  });
  document.getElementById('out').value = result || '';
  await navigator.clipboard.writeText(result || '');
});
