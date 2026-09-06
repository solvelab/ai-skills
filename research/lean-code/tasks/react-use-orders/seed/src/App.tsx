import { useUsers } from './hooks/useUsers';

export function App() {
  const users = useUsers();
  if (users.isPending) return <p>Loading…</p>;
  if (users.isError) return <p role="alert">{users.error.message}</p>;
  return (
    <ul>
      {users.data.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
}
