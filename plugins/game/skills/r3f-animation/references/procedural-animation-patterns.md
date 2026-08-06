# Reference — Procedural Animation Patterns

Part of the `r3f-animation` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Skeletal Animation

### Accessing Bones

```tsx
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useEffect, useRef } from 'react'

function SkeletalCharacter() {
  const { scene } = useGLTF('/models/character.glb')
  const headBoneRef = useRef()

  useEffect(() => {
    // Find skeleton
    scene.traverse((child) => {
      if (child.isSkinnedMesh) {
        const skeleton = child.skeleton
        const headBone = skeleton.bones.find(b => b.name === 'Head')
        headBoneRef.current = headBone
      }
    })
  }, [scene])

  // Animate bone
  useFrame(({ clock }) => {
    if (headBoneRef.current) {
      headBoneRef.current.rotation.y = Math.sin(clock.elapsedTime) * 0.3
    }
  })

  return <primitive object={scene} />
}
```

### Bone Attachments

```tsx
function CharacterWithWeapon() {
  const { scene } = useGLTF('/models/character.glb')
  const weaponRef = useRef<THREE.Mesh>(null!)
  const handBoneRef = useRef()

  useEffect(() => {
    scene.traverse((child) => {
      if (child.isSkinnedMesh) {
        const handBone = child.skeleton.bones.find(b => b.name === 'RightHand')
        if (handBone && weaponRef.current) {
          handBone.add(weaponRef.current)
          handBoneRef.current = handBone
        }
      }
    })

    return () => {
      // Cleanup
      if (handBoneRef.current && weaponRef.current) {
        handBoneRef.current.remove(weaponRef.current)
      }
    }
  }, [scene])

  return (
    <>
      <primitive object={scene} />
      <mesh ref={weaponRef} position={[0, 0, 0.5]}>
        <boxGeometry args={[0.1, 0.1, 1]} />
        <meshStandardMaterial color="gray" />
      </mesh>
    </>
  )
}
```

## Procedural Animation Patterns

### Smooth Damping

```tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

function SmoothFollow({ target }) {
  const meshRef = useRef<THREE.Mesh>(null!)
  const currentPos = useRef(new THREE.Vector3())

  useFrame((state, delta) => {
    // Lerp towards target
    currentPos.current.lerp(target, delta * 5)
    meshRef.current.position.copy(currentPos.current)
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5]} />
      <meshStandardMaterial color="blue" />
    </mesh>
  )
}
```

### Spring Physics (Manual)

```tsx
function SpringMesh({ target = 0 }) {
  const meshRef = useRef<THREE.Mesh>(null!)
  const spring = useRef({
    position: 0,
    velocity: 0,
    stiffness: 100,
    damping: 10
  })

  useFrame((state, delta) => {
    const s = spring.current
    const force = -s.stiffness * (s.position - target)
    const dampingForce = -s.damping * s.velocity

    s.velocity += (force + dampingForce) * delta
    s.position += s.velocity * delta

    meshRef.current.position.y = s.position
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="green" />
    </mesh>
  )
}
```

### Oscillation Patterns

```tsx
function OscillatingMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame(({ clock }) => {
    const t = clock.elapsedTime

    // Sine wave
    meshRef.current.position.y = Math.sin(t * 2) * 0.5

    // Circular motion
    meshRef.current.position.x = Math.cos(t) * 2
    meshRef.current.position.z = Math.sin(t) * 2

    // Bouncing
    meshRef.current.position.y = Math.abs(Math.sin(t * 3)) * 2

    // Figure 8
    meshRef.current.position.x = Math.sin(t) * 2
    meshRef.current.position.z = Math.sin(t * 2) * 1
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.3]} />
      <meshStandardMaterial color="purple" />
    </mesh>
  )
}
```

## Drei Animation Helpers

### Float

```tsx
import { Float } from '@react-three/drei'

function FloatingObject() {
  return (
    <Float
      speed={1}            // Animation speed
      rotationIntensity={1} // Rotation intensity
      floatIntensity={1}   // Float intensity
      floatingRange={[-0.1, 0.1]} // Range of y-axis float
    >
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="gold" />
      </mesh>
    </Float>
  )
}
```

### MeshWobbleMaterial / MeshDistortMaterial

MeshWobbleMaterial / MeshDistortMaterial are documented in r3f-materials.

### Trail

```tsx
import { Trail } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function TrailingMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    meshRef.current.position.x = Math.sin(t) * 3
    meshRef.current.position.y = Math.cos(t * 2) * 2
  })

  return (
    <Trail
      width={2}
      length={8}
      color="hotpink"
      attenuation={(t) => t * t}
    >
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.2]} />
        <meshStandardMaterial color="white" />
      </mesh>
    </Trail>
  )
}
```

