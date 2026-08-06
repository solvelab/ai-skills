# Reference — useFrame Hook

Part of the `r3f-fundamentals` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function RotatingBox() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta
    meshRef.current.rotation.y += delta * 0.5
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}

export default function App() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />
      <RotatingBox />
    </Canvas>
  )
}
```

## Canvas Component

The root component that creates the WebGL context, scene, camera, and renderer.

```tsx
import { Canvas } from '@react-three/fiber'

function App() {
  return (
    <Canvas
      // Camera configuration
      camera={{
        position: [0, 5, 10],
        fov: 75,
        near: 0.1,
        far: 1000,
      }}
      // Or use orthographic
      orthographic
      camera={{ zoom: 50, position: [0, 0, 100] }}

      // Renderer settings
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance',
        preserveDrawingBuffer: true,  // For screenshots
      }}
      dpr={[1, 2]}  // Pixel ratio min/max

      // Shadows
      shadows  // or shadows="soft" | "basic" | "percentage"

      // Color management
      flat  // Disable automatic sRGB color management

      // Frame loop control
      frameloop="demand"  // 'always' | 'demand' | 'never'

      // Event handling
      eventSource={document.getElementById('root')}
      eventPrefix="client"  // 'offset' | 'client' | 'page' | 'layer' | 'screen'

      // Callbacks
      onCreated={(state) => {
        console.log('Canvas ready:', state.gl, state.scene, state.camera)
      }}
      onPointerMissed={() => console.log('Clicked background')}

      // Styling
      style={{ width: '100%', height: '100vh' }}
    >
      <Scene />
    </Canvas>
  )
}
```

### Canvas Defaults

R3F sets sensible defaults:
- Renderer: antialias, alpha, outputColorSpace = SRGBColorSpace
- Camera: PerspectiveCamera at [0, 0, 5]
- Scene: Automatic resize handling
- Events: Pointer events enabled

## useFrame Hook

Subscribe to the render loop. Called every frame (typically 60fps).

```tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function AnimatedMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((state, delta, xrFrame) => {
    // state: Full R3F state (see useThree)
    // delta: Time since last frame in seconds
    // xrFrame: XR frame if in VR/AR mode

    // Animate rotation
    meshRef.current.rotation.y += delta

    // Access clock
    const elapsed = state.clock.elapsedTime
    meshRef.current.position.y = Math.sin(elapsed) * 2

    // Access pointer position (-1 to 1)
    const { x, y } = state.pointer
    meshRef.current.rotation.x = y * 0.5
    meshRef.current.rotation.z = x * 0.5
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

### useFrame with Priority

Control render order with priority (higher = later).

```tsx
// Default priority is 0
useFrame((state, delta) => {
  // Runs first
}, -1)

useFrame((state, delta) => {
  // Runs after priority -1
}, 0)

// Manual rendering with positive priority
useFrame((state, delta) => {
  // Take over rendering
  state.gl.render(state.scene, state.camera)
}, 1)
```

### Conditional useFrame

```tsx
function ConditionalAnimation({ active }) {
  useFrame((state, delta) => {
    if (!active) return  // Skip when inactive
    meshRef.current.rotation.y += delta
  })
}
```

