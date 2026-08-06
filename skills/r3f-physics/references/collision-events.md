# Reference — Collision Events

Part of the `r3f-physics` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Collision Events

### On RigidBody

```tsx
// excerpt — not a complete module; see the surrounding section for context
<RigidBody
  name="player"
  onCollisionEnter={({ manifold, target, other }) => {
    console.log('Collision with', other.rigidBodyObject?.name)
    console.log('Contact point', manifold.solverContactPoint(0))
  }}
  onCollisionExit={({ target, other }) => {
    console.log('Collision ended with', other.rigidBodyObject?.name)
  }}
  onContactForce={({ totalForce }) => {
    console.log('Contact force:', totalForce)
  }}
  onSleep={() => console.log('Body went to sleep')}
  onWake={() => console.log('Body woke up')}
>
  <mesh>
    <boxGeometry />
    <meshStandardMaterial />
  </mesh>
</RigidBody>
```

### On Colliders

```tsx
// excerpt — not a complete module; see the surrounding section for context
<CuboidCollider
  args={[1, 1, 1]}
  onCollisionEnter={(payload) => console.log('Collider hit')}
  onCollisionExit={(payload) => console.log('Collider exit')}
/>
```

## Sensors

Detect overlaps without physical collision:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<RigidBody>
  {/* Visible mesh */}
  <mesh>
    <boxGeometry />
    <meshStandardMaterial />
  </mesh>

  {/* Invisible sensor trigger */}
  <CuboidCollider
    args={[2, 2, 2]}
    sensor
    onIntersectionEnter={() => console.log('Entered trigger zone')}
    onIntersectionExit={() => console.log('Exited trigger zone')}
  />
</RigidBody>

// Goal detection example
<RigidBody type="fixed">
  <GoalPosts />
  <CuboidCollider
    args={[5, 5, 1]}
    sensor
    onIntersectionEnter={() => console.log('Goal!')}
  />
</RigidBody>
```

## Collision Groups

Control which objects can collide:

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { interactionGroups } from '@react-three/rapier'

// Group 0, interacts with groups 0, 1, 2
<CuboidCollider collisionGroups={interactionGroups(0, [0, 1, 2])} />

// Group 12, interacts with all groups
<CuboidCollider collisionGroups={interactionGroups(12)} />

// Groups 0 and 5, only interacts with group 7
<CuboidCollider collisionGroups={interactionGroups([0, 5], 7)} />

// On RigidBody (applies to all auto-generated colliders)
<RigidBody collisionGroups={interactionGroups(1, [1, 2])}>
  <mesh>...</mesh>
</RigidBody>
```

