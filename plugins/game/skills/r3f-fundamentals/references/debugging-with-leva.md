# Reference — Debugging with Leva

Part of the `r3f-fundamentals` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Common Patterns

### Fullscreen Canvas

```css
/* styles.css */
html, body, #root {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

// App.tsx
<Canvas style={{ width: '100%', height: '100%' }}>
```

### Responsive Canvas

```tsx
function ResponsiveScene() {
  const { viewport } = useThree()

  return (
    <mesh scale={Math.min(viewport.width, viewport.height) / 5}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### Forwarding Refs

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { forwardRef } from 'react'

const CustomMesh = forwardRef((props, ref) => {
  return (
    <mesh ref={ref} {...props}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
})

// Usage
const meshRef = useRef()
<CustomMesh ref={meshRef} position={[0, 1, 0]} />
```

## Debugging with Leva

Leva provides a GUI for tweaking parameters in real-time during development.

### Installation

```bash
npm install leva
```

### Basic Controls

```tsx
import { useControls } from 'leva'

function DebugMesh() {
  const { position, color, scale, visible } = useControls({
    position: { value: [0, 0, 0], step: 0.1 },
    color: '#ff0000',
    scale: { value: 1, min: 0.1, max: 5, step: 0.1 },
    visible: true,
  })

  return (
    <mesh position={position} scale={scale} visible={visible}>
      <boxGeometry />
      <meshStandardMaterial color={color} />
    </mesh>
  )
}
```

### Organized Folders

```tsx
import { useControls, folder } from 'leva'

function DebugScene() {
  const { lightIntensity, lightColor, shadowMapSize } = useControls({
    Lighting: folder({
      lightIntensity: { value: 1, min: 0, max: 5 },
      lightColor: '#ffffff',
      shadowMapSize: { value: 1024, options: [512, 1024, 2048, 4096] },
    }),
    Camera: folder({
      fov: { value: 75, min: 30, max: 120 },
      near: { value: 0.1, min: 0.01, max: 1 },
    }),
  })

  return (
    <directionalLight
      intensity={lightIntensity}
      color={lightColor}
      shadow-mapSize={[shadowMapSize, shadowMapSize]}
    />
  )
}
```

### Button Actions

```tsx
import { useControls, button } from 'leva'

function DebugActions() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useControls({
    'Reset Position': button(() => {
      meshRef.current.position.set(0, 0, 0)
    }),
    'Random Color': button(() => {
      meshRef.current.material.color.setHex(Math.random() * 0xffffff)
    }),
    'Log State': button(() => {
      console.log(meshRef.current.position)
    }),
  })

  return <mesh ref={meshRef}>...</mesh>
}
```

### Hide in Production

```tsx
import { Leva } from 'leva'

function App() {
  return (
    <>
      {/* Hide Leva panel in production */}
      <Leva hidden={process.env.NODE_ENV === 'production'} />

      <Canvas>
        <Scene />
      </Canvas>
    </>
  )
}
```

### Monitor Values (Read-Only)

```tsx
import { useControls, monitor } from 'leva'
import { useFrame } from '@react-three/fiber'

function PerformanceMonitor() {
  const [fps, setFps] = useState(0)

  useControls({
    FPS: monitor(() => fps, { graph: true, interval: 100 }),
  })

  useFrame((state) => {
    // Update FPS display
    setFps(Math.round(1 / state.clock.getDelta()))
  })

  return null
}
```

### Integration with useFrame

```tsx
function AnimatedDebugMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)

  const { speed, amplitude, enabled } = useControls('Animation', {
    enabled: true,
    speed: { value: 1, min: 0, max: 5 },
    amplitude: { value: 1, min: 0, max: 3 },
  })

  useFrame(({ clock }) => {
    if (!enabled) return
    meshRef.current.position.y = Math.sin(clock.elapsedTime * speed) * amplitude
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry />
      <meshStandardMaterial color="cyan" />
    </mesh>
  )
}
```

