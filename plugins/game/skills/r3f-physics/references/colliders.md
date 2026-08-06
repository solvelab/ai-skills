# Reference — Colliders

Part of the `r3f-physics` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Colliders

### Automatic Colliders

RigidBody auto-generates colliders from child meshes:

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Global default
<Physics colliders="hull">
  <RigidBody>
    <Torus />  {/* Gets hull collider */}
  </RigidBody>
</Physics>

// Per-body override
<Physics colliders={false}>
  <RigidBody colliders="cuboid">
    <Box />
  </RigidBody>

  <RigidBody colliders="ball">
    <Sphere />
  </RigidBody>
</Physics>
```

### Collider Types

| Type | Description | Best For |
|------|-------------|----------|
| `cuboid` | Box shape | Boxes, crates |
| `ball` | Sphere shape | Balls, spherical objects |
| `hull` | Convex hull | Complex convex shapes |
| `trimesh` | Triangle mesh | Concave/complex static geometry |

### Manual Colliders

```tsx
// excerpt — not a complete module; see the surrounding section for context
import {
  CuboidCollider,
  BallCollider,
  CapsuleCollider,
  CylinderCollider,
  ConeCollider,
  HeightfieldCollider,
  TrimeshCollider,
  ConvexHullCollider
} from '@react-three/rapier'

// Standalone collider (static)
<CuboidCollider position={[0, -2, 0]} args={[10, 0.5, 10]} />

// Inside RigidBody (compound collider)
<RigidBody position={[0, 5, 0]}>
  <mesh>
    <boxGeometry />
    <meshStandardMaterial />
  </mesh>

  {/* Additional colliders */}
  <BallCollider args={[0.5]} position={[0, 1, 0]} />
  <CapsuleCollider args={[0.5, 1]} position={[0, -1, 0]} />
</RigidBody>

// Collider args reference
<CuboidCollider args={[halfWidth, halfHeight, halfDepth]} />
<BallCollider args={[radius]} />
<CapsuleCollider args={[halfHeight, radius]} />
<CylinderCollider args={[halfHeight, radius]} />
<ConeCollider args={[halfHeight, radius]} />
```

### Mesh Colliders

For complex shapes:

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { MeshCollider } from '@react-three/rapier'

<RigidBody colliders={false}>
  <MeshCollider type="trimesh">
    <mesh geometry={complexGeometry}>
      <meshStandardMaterial />
    </mesh>
  </MeshCollider>
</RigidBody>

// Convex hull for dynamic bodies
<RigidBody colliders={false}>
  <MeshCollider type="hull">
    <mesh geometry={someGeometry} />
  </MeshCollider>
</RigidBody>
```

## Applying Forces

### Using Refs

```tsx
import { RigidBody, RapierRigidBody } from '@react-three/rapier'
import { useRef, useEffect } from 'react'

function ForcefulBox() {
  const rigidBody = useRef<RapierRigidBody>(null)

  useEffect(() => {
    if (rigidBody.current) {
      // One-time impulse (instantaneous)
      rigidBody.current.applyImpulse({ x: 0, y: 10, z: 0 }, true)

      // Continuous force (apply each frame)
      rigidBody.current.addForce({ x: 0, y: 10, z: 0 }, true)

      // Torque (rotation)
      rigidBody.current.applyTorqueImpulse({ x: 0, y: 5, z: 0 }, true)
      rigidBody.current.addTorque({ x: 0, y: 5, z: 0 }, true)
    }
  }, [])

  return (
    <RigidBody ref={rigidBody}>
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="red" />
      </mesh>
    </RigidBody>
  )
}
```

### In useFrame

```tsx
import { useFrame } from '@react-three/fiber'

function ContinuousForce() {
  const rigidBody = useRef<RapierRigidBody>(null)

  useFrame(() => {
    if (rigidBody.current) {
      // Apply force every frame
      rigidBody.current.addForce({ x: 0, y: 20, z: 0 }, true)
    }
  })

  return (
    <RigidBody ref={rigidBody} gravityScale={0.5}>
      <mesh>
        <sphereGeometry />
        <meshStandardMaterial color="blue" />
      </mesh>
    </RigidBody>
  )
}
```

### Getting/Setting Position

```tsx
import { vec3, quat, euler } from '@react-three/rapier'

function PositionControl() {
  const rigidBody = useRef<RapierRigidBody>(null)

  const teleport = () => {
    if (rigidBody.current) {
      // Get current transform
      const position = vec3(rigidBody.current.translation())
      const rotation = quat(rigidBody.current.rotation())

      // Set new transform
      rigidBody.current.setTranslation({ x: 0, y: 10, z: 0 }, true)
      rigidBody.current.setRotation({ x: 0, y: 0, z: 0, w: 1 }, true)

      // Set velocities
      rigidBody.current.setLinvel({ x: 0, y: 0, z: 0 }, true)
      rigidBody.current.setAngvel({ x: 0, y: 0, z: 0 }, true)
    }
  }

  return (
    <RigidBody ref={rigidBody}>
      <mesh onClick={teleport}>
        <boxGeometry />
        <meshStandardMaterial />
      </mesh>
    </RigidBody>
  )
}
```

