# Reference — State Management Performance

Part of the `r3f-animation` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Animation with Zustand State

```tsx
import { create } from 'zustand'
import { useFrame } from '@react-three/fiber'

const useStore = create((set) => ({
  isAnimating: false,
  speed: 1,
  toggleAnimation: () => set((state) => ({ isAnimating: !state.isAnimating })),
  setSpeed: (speed) => set({ speed })
}))

function AnimatedMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const { isAnimating, speed } = useStore()

  useFrame((state, delta) => {
    if (isAnimating) {
      meshRef.current.rotation.y += delta * speed
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}

// UI Component
function Controls() {
  const { toggleAnimation, setSpeed } = useStore()

  return (
    <div>
      <button onClick={toggleAnimation}>Toggle</button>
      <input
        type="range"
        min="0"
        max="5"
        step="0.1"
        onChange={(e) => setSpeed(parseFloat(e.target.value))}
      />
    </div>
  )
}
```

## State Management Performance

Critical patterns for high-performance state management in animations.

### getState() in useFrame

Use `getState()` instead of hooks inside useFrame for zero subscription overhead:

```tsx
import { create } from 'zustand'

const useGameStore = create((set) => ({
  playerPosition: [0, 0, 0],
  targetPosition: [0, 0, 0],
  setPlayerPosition: (pos) => set({ playerPosition: pos }),
}))

function Player() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((state, delta) => {
    // ✅ GOOD: getState() has no subscription overhead
    const { targetPosition } = useGameStore.getState()

    // Lerp towards target
    meshRef.current.position.lerp(
      new THREE.Vector3(...targetPosition),
      delta * 5
    )
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="blue" />
    </mesh>
  )
}
```

### Transient Subscriptions

Subscribe to state changes without triggering React re-renders:

```tsx
import { useEffect, useRef } from 'react'

function Enemy() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useEffect(() => {
    // Subscribe directly - updates mesh without re-rendering component
    const unsub = useGameStore.subscribe(
      (state) => state.playerPosition,
      (playerPos) => {
        // Look at player (runs on every state change, no re-render)
        meshRef.current.lookAt(...playerPos)
      }
    )
    return unsub
  }, [])

  return (
    <mesh ref={meshRef}>
      <coneGeometry args={[0.5, 1, 4]} />
      <meshStandardMaterial color="red" />
    </mesh>
  )
}
```

### Selective Subscriptions with Shallow

Subscribe to multiple values efficiently:

```tsx
import { shallow } from 'zustand/shallow'

function HUD() {
  // Only re-renders when health OR score actually changes
  const { health, score } = useGameStore(
    (state) => ({ health: state.health, score: state.score }),
    shallow
  )

  return (
    <Html>
      <div>Health: {health}</div>
      <div>Score: {score}</div>
    </Html>
  )
}

// For single values, no shallow needed
const health = useGameStore((state) => state.health)
```

### Isolate Animated Components

Separate state-dependent UI from animated 3D objects:

```tsx
// ❌ BAD: Parent re-renders cause animation jank
function BadPattern() {
  const [score, setScore] = useState(0)
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((_, delta) => {
    meshRef.current.rotation.y += delta  // Affected by score re-renders
  })

  return (
    <>
      <mesh ref={meshRef}>...</mesh>
      <ScoreDisplay score={score} />
    </>
  )
}

// ✅ GOOD: Isolated animation component
function GoodPattern() {
  return (
    <>
      <AnimatedMesh />      {/* Never re-renders from score */}
      <ScoreDisplay />      {/* Has its own state subscription */}
    </>
  )
}

function AnimatedMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((_, delta) => {
    meshRef.current.rotation.y += delta  // Smooth, uninterrupted
  })

  return <mesh ref={meshRef}>...</mesh>
}

function ScoreDisplay() {
  const score = useGameStore((state) => state.score)
  return <Html><div>Score: {score}</div></Html>
}
```

