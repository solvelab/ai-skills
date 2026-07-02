# Reference — the NUI bridge, both sides (production-extracted)

## React side (`hooks/useNUI.ts` — the essential hooks)

```tsx
interface NUIEvent { action: string; data?: any }
interface NUICallback { context: 'client' | 'server'; event: string; payload: any }

/** Listen to Lua -> NUI events (SendNUIMessage arrives as window `message`). */
export function useNUIEvent<T = any>(eventName: string, callback: (data: T) => void): void {
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const { action, data } = event.data as NUIEvent;
      if (action === eventName) callback(data);
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [eventName, callback]);
}

/** NUI -> Lua: everything through ONE endpoint, discriminated by context/event. */
export function useNUICallback() {
  const sendCallback = useCallback((cb: NUICallback) => {
    fetch(`https://${GetParentResourceName()}/nuiCallback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cb),
    });
  }, []);
  return { sendCallback };
}

/** Visibility: invisible by default; the game decides when the UI exists. */
export function useNUIVisibility(): { visible: boolean; data: any } {
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState<any>(null);
  useNUIEvent('showNUI', (d) => { setVisible(true); setData(d); });
  useNUIEvent('hideNUI', () => { setVisible(false); setData(null); });
  useNUIEvent('updateData', (d) => setData(d));
  return { visible, data };
}

/** uiReady handshake: Lua gates its FIRST SendNUIMessage on this. Sent once,
 *  after a settle delay so all listeners are mounted (data sent during CEF
 *  page load is silently lost). */
export function useUIReady() {
  const { sendCallback } = useNUICallback();
  const sent = useRef(false);
  useEffect(() => {
    if (sent.current) return;
    const timer = setTimeout(() => {
      sendCallback({ context: 'client', event: 'uiReady', payload: { status: true } });
      sent.current = true;
    }, 1000);
    return () => clearTimeout(timer);
  }, [sendCallback]);
}
```

Dev mock (in `main.tsx`, before render):

```ts
if (typeof GetParentResourceName === 'undefined') {
  (window as any).GetParentResourceName = () => 'dev-resource';
}
```

## Lua side (client)

```lua
local uiReady = false
local pendingShow = nil

local function toggleNUI(show, data)
  SetNuiFocus(show, show)
  SendNUIMessage({ action = show and "showNUI" or "hideNUI", data = data })
end

-- ONE callback endpoint; route by context/event (validate the payload — it is forgeable).
RegisterNUICallback("nuiCallback", function(body, cb)
  cb({ ok = true })
  if type(body) ~= "table" then return end
  if body.event == "uiReady" then
    uiReady = true
    if pendingShow then toggleNUI(true, pendingShow); pendingShow = nil end
    return
  end
  if body.context == "server" then
    TriggerServerEvent("res:nuiAction", body.event, body.payload)
  elseif body.event == "close" then
    toggleNUI(false)
  end
end)

-- Never SendNUIMessage before uiReady: queue the first show.
function OpenUI(data)
  if uiReady then toggleNUI(true, data) else pendingShow = data end
end

-- Focus cleanup on resource stop — a stuck cursor is the classic NUI bug.
AddEventHandler("onResourceStop", function(name)
  if name == GetCurrentResourceName() then toggleNUI(false) end
end)
```

## Test harness sketch (vitest + happy-dom)

```ts
export function mockNuiEvent(action: string, data?: unknown) {
  window.dispatchEvent(new MessageEvent('message', { data: { action, data } }));
}

const calls: Array<{ endpoint: string; body: any }> = [];
global.fetch = (async (url: string, init: any) => {
  const endpoint = new URL(url).pathname.slice(1);
  calls.push({ endpoint, body: JSON.parse(init.body) });
  return new Response('{}');
}) as any;
export const getNuiCalls = () => calls;
```

Assert the contract: `mockNuiEvent('showNUI', {...})` makes the app visible; a button click lands
in `getNuiCalls()` as `{ endpoint: 'nuiCallback', body: { context, event, payload } }`.
