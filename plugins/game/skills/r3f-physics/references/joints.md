# Reference — Joints

Part of the `r3f-physics` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Joints

Connect rigid bodies together.

### Fixed Joint

Bodies don't move relative to each other:

```tsx
import { useFixedJoint, RapierRigidBody } from '@react-three/rapier'

function FixedJointExample() {
  const bodyA = useRef<RapierRigidBody>(null)
  const bodyB = useRef<RapierRigidBody>(null)

  useFixedJoint(bodyA, bodyB, [
    [0, 0, 0],      // Position in bodyA's local space
    [0, 0, 0, 1],   // Orientation in bodyA's local space (quaternion)
    [0, -1, 0],     // Position in bodyB's local space
    [0, 0, 0, 1],   // Orientation in bodyB's local space
  ])

  return (
    <>
      <RigidBody ref={bodyA} position={[0, 5, 0]}>
        <mesh><boxGeometry /><meshStandardMaterial color="red" /></mesh>
      </RigidBody>
      <RigidBody ref={bodyB} position={[0, 4, 0]}>
        <mesh><boxGeometry /><meshStandardMaterial color="blue" /></mesh>
      </RigidBody>
    </>
  )
}
```

### Revolute Joint (Hinge)

Rotation around one axis:

```tsx
import { useRevoluteJoint } from '@react-three/rapier'

function HingeDoor() {
  const frame = useRef<RapierRigidBody>(null)
  const door = useRef<RapierRigidBody>(null)

  useRevoluteJoint(frame, door, [
    [0.5, 0, 0],    // Joint position in frame's local space
    [-0.5, 0, 0],   // Joint position in door's local space
    [0, 1, 0],      // Rotation axis
  ])

  return (
    <>
      <RigidBody ref={frame} type="fixed">
        <mesh><boxGeometry args={[0.1, 2, 0.1]} /></mesh>
      </RigidBody>
      <RigidBody ref={door}>
        <mesh><boxGeometry args={[1, 2, 0.1]} /></mesh>
      </RigidBody>
    </>
  )
}
```

### Spherical Joint (Ball-Socket)

Rotation in all directions:

```tsx
import { useSphericalJoint } from '@react-three/rapier'

function BallJoint() {
  const bodyA = useRef<RapierRigidBody>(null)
  const bodyB = useRef<RapierRigidBody>(null)

  useSphericalJoint(bodyA, bodyB, [
    [0, -0.5, 0],   // Position in bodyA's local space
    [0, 0.5, 0],    // Position in bodyB's local space
  ])

  return (
    <>
      <RigidBody ref={bodyA} type="fixed" position={[0, 3, 0]}>
        <mesh><sphereGeometry args={[0.2]} /></mesh>
      </RigidBody>
      <RigidBody ref={bodyB} position={[0, 2, 0]}>
        <mesh><boxGeometry /></mesh>
      </RigidBody>
    </>
  )
}
```

### Prismatic Joint (Slider)

Translation along one axis:

```tsx
import { usePrismaticJoint } from '@react-three/rapier'

function Slider() {
  const track = useRef<RapierRigidBody>(null)
  const slider = useRef<RapierRigidBody>(null)

  usePrismaticJoint(track, slider, [
    [0, 0, 0],      // Position in track's local space
    [0, 0, 0],      // Position in slider's local space
    [1, 0, 0],      // Axis of translation
  ])

  return (
    <>
      <RigidBody ref={track} type="fixed">
        <mesh><boxGeometry args={[5, 0.1, 0.1]} /></mesh>
      </RigidBody>
      <RigidBody ref={slider}>
        <mesh><boxGeometry args={[0.5, 0.5, 0.5]} /></mesh>
      </RigidBody>
    </>
  )
}
```

### Spring Joint

Elastic connection:

```tsx
import { useSpringJoint } from '@react-three/rapier'

function SpringConnection() {
  const anchor = useRef<RapierRigidBody>(null)
  const ball = useRef<RapierRigidBody>(null)

  useSpringJoint(anchor, ball, [
    [0, 0, 0],      // Position in anchor's local space
    [0, 0, 0],      // Position in ball's local space
    2,              // Rest length
    1000,           // Stiffness
    10,             // Damping
  ])

  return (
    <>
      <RigidBody ref={anchor} type="fixed" position={[0, 5, 0]}>
        <mesh><sphereGeometry args={[0.1]} /></mesh>
      </RigidBody>
      <RigidBody ref={ball} position={[0, 3, 0]}>
        <mesh><sphereGeometry args={[0.5]} /></mesh>
      </RigidBody>
    </>
  )
}
```

### Rope Joint

Maximum distance constraint:

```tsx
import { useRopeJoint } from '@react-three/rapier'

function RopeConnection() {
  const anchor = useRef<RapierRigidBody>(null)
  const weight = useRef<RapierRigidBody>(null)

  useRopeJoint(anchor, weight, [
    [0, 0, 0],      // Position in anchor's local space
    [0, 0, 0],      // Position in weight's local space
    3,              // Max distance (rope length)
  ])

  return (
    <>
      <RigidBody ref={anchor} type="fixed" position={[0, 5, 0]}>
        <mesh><sphereGeometry args={[0.1]} /></mesh>
      </RigidBody>
      <RigidBody ref={weight} position={[0, 2, 0]}>
        <mesh><sphereGeometry args={[0.5]} /></mesh>
      </RigidBody>
    </>
  )
}
```

### Motorized Joints

```tsx
import { useRevoluteJoint } from '@react-three/rapier'
import { useFrame } from '@react-three/fiber'

function MotorizedWheel({ bodyA, bodyB }) {
  const joint = useRevoluteJoint(bodyA, bodyB, [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 1],  // Rotation axis
  ])

  useFrame(() => {
    if (joint.current) {
      // Configure motor: velocity, damping
      joint.current.configureMotorVelocity(10, 2)
    }
  })

  return null
}
```

