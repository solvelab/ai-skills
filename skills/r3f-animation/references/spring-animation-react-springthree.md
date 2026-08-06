# Reference — Spring Animation (@react-spring/three)

Part of the `r3f-animation` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Spring Animation (@react-spring/three)

Physics-based spring animations that integrate with R3F.

### Installation

```bash
npm install @react-spring/three
```

### Basic Spring

```tsx
import { useSpring, animated } from '@react-spring/three'

function AnimatedBox() {
  const [active, setActive] = useState(false)

  const { scale, color } = useSpring({
    scale: active ? 1.5 : 1,
    color: active ? '#ff6b6b' : '#4ecdc4',
    config: { mass: 1, tension: 280, friction: 60 }
  })

  return (
    <animated.mesh
      scale={scale}
      onClick={() => setActive(!active)}
    >
      <boxGeometry />
      <animated.meshStandardMaterial color={color} />
    </animated.mesh>
  )
}
```

### Spring Config Presets

```tsx
import { useSpring, animated, config } from '@react-spring/three'

function SpringPresets() {
  const { position } = useSpring({
    position: [0, 2, 0],
    config: config.wobbly  // Presets: default, gentle, wobbly, stiff, slow, molasses
  })

  // Or custom config
  const { rotation } = useSpring({
    rotation: [0, Math.PI, 0],
    config: {
      mass: 1,
      tension: 170,
      friction: 26,
      clamp: false,
      precision: 0.01,
      velocity: 0,
    }
  })

  return (
    <animated.mesh position={position} rotation={rotation}>
      <boxGeometry />
      <meshStandardMaterial />
    </animated.mesh>
  )
}
```

### Multiple Springs

```tsx
import { useSprings, animated } from '@react-spring/three'

function AnimatedBoxes({ count = 5 }) {
  const [springs, api] = useSprings(count, (i) => ({
    position: [i * 2 - count, 0, 0],
    scale: 1,
    config: { mass: 1, tension: 280, friction: 60 }
  }))

  const handleClick = (index) => {
    api.start((i) => {
      if (i === index) return { scale: 1.5 }
      return { scale: 1 }
    })
  }

  return springs.map((spring, i) => (
    <animated.mesh
      key={i}
      position={spring.position}
      scale={spring.scale}
      onClick={() => handleClick(i)}
    >
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </animated.mesh>
  ))
}
```

### Gesture Integration

Minimal spring-on-drag pattern — drag movement drives a spring target:

```tsx
const [spring, api] = useSpring(() => ({ position: [0, 0, 0] }))
const bind = useDrag(({ movement: [mx, my], down }) => {
  api.start({ position: down ? [mx / 100, -my / 100, 0] : [0, 0, 0] })
})
// <animated.mesh {...bind()} position={spring.position}>
```

Full drag/gesture patterns live in r3f-interaction.

### Chain Animations

```tsx
import { useSpring, animated, useChain, useSpringRef } from '@react-spring/three'

function ChainedAnimation() {
  const scaleRef = useSpringRef()
  const rotationRef = useSpringRef()

  const { scale } = useSpring({
    ref: scaleRef,
    from: { scale: 0 },
    to: { scale: 1 },
    config: { tension: 200, friction: 20 }
  })

  const { rotation } = useSpring({
    ref: rotationRef,
    from: { rotation: [0, 0, 0] },
    to: { rotation: [0, Math.PI * 2, 0] },
    config: { tension: 100, friction: 30 }
  })

  // Scale first (0-0.5), then rotation (0.5-1)
  useChain([scaleRef, rotationRef], [0, 0.5])

  return (
    <animated.mesh scale={scale} rotation={rotation}>
      <boxGeometry />
      <meshStandardMaterial color="cyan" />
    </animated.mesh>
  )
}
```

## Morph Targets

Blend between different mesh shapes.

```tsx
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function MorphingFace() {
  const { scene, nodes } = useGLTF('/models/face.glb')
  const meshRef = useRef<THREE.Object3D>(null!)

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()

    // Access morph target influences
    if (meshRef.current?.morphTargetInfluences) {
      // Animate smile
      const smileIndex = meshRef.current.morphTargetDictionary['smile']
      meshRef.current.morphTargetInfluences[smileIndex] = (Math.sin(t) + 1) / 2
    }
  })

  return (
    <primitive ref={meshRef} object={nodes.Face} />
  )
}
```

### Controlled Morph Targets

```tsx
function MorphControls({ morphInfluences }) {
  const { nodes } = useGLTF('/models/face.glb')
  const meshRef = useRef<THREE.Object3D>(null!)

  useFrame(() => {
    if (meshRef.current?.morphTargetInfluences) {
      Object.entries(morphInfluences).forEach(([name, value]) => {
        const index = meshRef.current.morphTargetDictionary[name]
        if (index !== undefined) {
          meshRef.current.morphTargetInfluences[index] = value
        }
      })
    }
  })

  return <primitive ref={meshRef} object={nodes.Face} />
}

// Usage
<MorphControls morphInfluences={{ smile: 0.5, blink: 1, angry: 0 }} />
```

