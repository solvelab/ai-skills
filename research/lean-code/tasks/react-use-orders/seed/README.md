# orders-console

Vite + React + TypeScript. Data access conventions:

- `src/api/client.ts` exports `apiClient`, the one HTTP client (axios under the hood, envelope
  unwrapped, errors normalised to `ApiException`). Feature code never calls `axios` or `fetch`.
- one zod parser per domain in `src/api/<domain>.ts`; the fetcher returns parsed data.
- hooks in `src/hooks/` wrap TanStack Query (`useQuery`) around a fetcher, with a `<domain>Keys`
  object for the query keys. `useUsers.ts` is the model.

```
npm install
npm run dev
```
