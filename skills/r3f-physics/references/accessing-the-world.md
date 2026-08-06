# Reference — Accessing the World

Part of the `r3f-physics` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Instanced Physics

Efficient physics for many identical objects:

```tsx
import { InstancedRigidBodies, RapierRigidBody } from '@react-three/rapier'
import { useRef, useMemo } from 'react'

function InstancedBalls() {
  const COUNT = 100
  const rigidBodies = useRef<RapierRigidBody[]>(null)

  const instances = useMemo(() => {
    return Array.from({ length: COUNT }, (_, i) => ({
      key: `ball-${i}`,
      position: [
        (Math.random() - 0.5) * 10,
        Math.random() * 10 + 5,
        (Math.random() - 0.5) * 10,
      ] as [number, number, number],
      rotation: [0, 0, 0] as [number, number, number],
    }))
  }, [])

  return (
    <InstancedRigidBodies
      ref={rigidBodies}
      instances={instances}
      colliders="ball"
    >
      <instancedMesh args={[undefined, undefined, COUNT]}>
        <sphereGeometry args={[0.5]} />
        <meshStandardMaterial color="orange" />
      </instancedMesh>
    </InstancedRigidBodies>
  )
}
```

## Accessing the World

```tsx
import { useRapier } from '@react-three/rapier'
import { useEffect } from 'react'

function WorldAccess() {
  const { world, rapier } = useRapier()

  useEffect(() => {
    // Change gravity
    world.setGravity({ x: 0, y: -20, z: 0 })

    // Iterate over bodies
    world.bodies.forEach((body) => {
      console.log(body.translation())
    })
  }, [world])

  return null
}
```

### Manual Stepping

```tsx
function ManualStep() {
  const { step } = useRapier()

  const advancePhysics = () => {
    step(1 / 60)  // Advance by one frame
  }

  return <button onClick={advancePhysics}>Step</button>
}
```

### World Snapshots

Save and restore physics state:

```tsx
function SnapshotSystem() {
  const { world, setWorld, rapier } = useRapier()
  const snapshot = useRef<Uint8Array>()

  const saveState = () => {
    snapshot.current = world.takeSnapshot()
  }

  const loadState = () => {
    if (snapshot.current) {
      setWorld(rapier.World.restoreSnapshot(snapshot.current))
    }
  }

  return (
    <>
      <button onClick={saveState}>Save</button>
      <button onClick={loadState}>Load</button>
    </>
  )
}
```

## Attractors

From `@react-three/rapier-addons`:

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { Attractor } from '@react-three/rapier-addons'

// Attract nearby bodies
<Attractor
  position={[0, 0, 0]}
  range={10}
  strength={5}
  type="linear"        // "static" | "linear" | "newtonian"
/>

// Repel bodies
<Attractor range={10} strength={-5} position={[5, 0, 0]} />

// Selective attraction (only affect certain groups)
<Attractor
  range={10}
  strength={10}
  collisionGroups={interactionGroups(0, [2, 3])}
/>
```

## Debug Visualization

```tsx
// excerpt — not a complete module; see the surrounding section for context
<Physics debug>
  {/* All colliders shown as wireframes */}
</Physics>

// Conditional debug
<Physics debug={process.env.NODE_ENV === 'development'}>
  ...
</Physics>
```

## Performance Tips

1. **Use appropriate collider types**: `cuboid` and `ball` are fastest
2. **Avoid `trimesh` for dynamic bodies**: Use `hull` instead
3. **Enable sleeping**: Bodies at rest stop computing
4. **Use collision groups**: Reduce collision checks
5. **Limit active bodies**: Too many dynamic bodies hurts performance
6. **Use instanced bodies**: For many identical objects
7. **Fixed timestep**: More stable than variable

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Performance-optimized setup
<Physics
  timeStep={1/60}
  colliders="cuboid"
  gravity={[0, -9.81, 0]}
>
  {/* Use collision groups to limit checks */}
  <RigidBody collisionGroups={interactionGroups(0, [0, 1])}>
    ...
  </RigidBody>
</Physics>
```

