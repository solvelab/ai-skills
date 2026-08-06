# Reference — RigidBody

Part of the `r3f-physics` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'
import { Physics, RigidBody, CuboidCollider } from '@react-three/rapier'
import { Suspense } from 'react'

function Scene() {
  return (
    <Canvas>
      <Suspense fallback={null}>
        <Physics debug>
          {/* Falling box */}
          <RigidBody>
            <mesh>
              <boxGeometry />
              <meshStandardMaterial color="orange" />
            </mesh>
          </RigidBody>

          {/* Static ground */}
          <CuboidCollider position={[0, -2, 0]} args={[10, 0.5, 10]} />
        </Physics>
      </Suspense>

      <ambientLight />
      <directionalLight position={[5, 5, 5]} />
    </Canvas>
  )
}
```

## Installation

```bash
npm install @react-three/rapier
```

## Physics Component

The root component that creates the physics world.

```tsx
import { Physics } from '@react-three/rapier'

<Canvas>
  <Suspense fallback={null}>
    <Physics
      gravity={[0, -9.81, 0]}    // Gravity vector
      debug={false}               // Show collider wireframes
      timeStep={1/60}             // Fixed timestep (or "vary" for variable)
      paused={false}              // Pause simulation
      interpolate={true}          // Smooth rendering between physics steps
      colliders="cuboid"          // Default collider type for all RigidBodies
      updateLoop="follow"         // "follow" (sync with frame) or "independent"
    >
      {/* Physics objects */}
    </Physics>
  </Suspense>
</Canvas>
```

### On-Demand Rendering

For performance optimization with static scenes:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<Canvas frameloop="demand">
  <Physics updateLoop="independent">
    {/* Physics only triggers render when bodies are active */}
  </Physics>
</Canvas>
```

## RigidBody

Makes objects participate in physics simulation.

### Basic Usage

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { RigidBody } from '@react-three/rapier'

// Dynamic body (affected by forces/gravity)
<RigidBody>
  <mesh>
    <boxGeometry />
    <meshStandardMaterial color="red" />
  </mesh>
</RigidBody>

// Fixed body (immovable)
<RigidBody type="fixed">
  <mesh>
    <boxGeometry args={[10, 0.5, 10]} />
    <meshStandardMaterial color="gray" />
  </mesh>
</RigidBody>

// Kinematic body (moved programmatically)
<RigidBody type="kinematicPosition">
  <mesh>
    <sphereGeometry />
    <meshStandardMaterial color="blue" />
  </mesh>
</RigidBody>
```

### RigidBody Types

| Type | Description |
|------|-------------|
| `dynamic` | Affected by forces, gravity, collisions (default) |
| `fixed` | Immovable, infinite mass |
| `kinematicPosition` | Moved via setNextKinematicTranslation |
| `kinematicVelocity` | Moved via setNextKinematicRotation |

### RigidBody Properties

```tsx
// excerpt — not a complete module; see the surrounding section for context
<RigidBody
  // Transform
  position={[0, 5, 0]}
  rotation={[0, Math.PI / 4, 0]}
  scale={1}

  // Physics
  type="dynamic"
  mass={1}
  restitution={0.5}           // Bounciness (0-1)
  friction={0.5}              // Surface friction
  linearDamping={0}           // Slows linear velocity
  angularDamping={0}          // Slows angular velocity
  gravityScale={1}            // Multiplier for gravity

  // Collider generation
  colliders="cuboid"          // "cuboid" | "ball" | "hull" | "trimesh" | false

  // Constraints
  lockTranslations={false}    // Prevent all translation
  lockRotations={false}       // Prevent all rotation
  enabledTranslations={[true, true, true]}  // Lock specific axes
  enabledRotations={[true, true, true]}     // Lock specific axes

  // Sleeping
  canSleep={true}
  ccd={false}                 // Continuous collision detection (fast objects)

  // Naming (for collision events)
  name="player"
/>
```

