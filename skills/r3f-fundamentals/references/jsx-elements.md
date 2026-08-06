# Reference — JSX Elements

Part of the `r3f-fundamentals` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## useThree Hook

Access the R3F state store.

```tsx
import { useThree } from '@react-three/fiber'

function CameraInfo() {
  // Get full state (triggers re-render on any change)
  const state = useThree()

  // Selective subscription (recommended)
  const camera = useThree((state) => state.camera)
  const gl = useThree((state) => state.gl)
  const scene = useThree((state) => state.scene)
  const size = useThree((state) => state.size)

  // Available state properties:
  // gl: WebGLRenderer
  // scene: Scene
  // camera: Camera
  // raycaster: Raycaster
  // pointer: Vector2 (normalized -1 to 1)
  // mouse: Vector2 (deprecated, use pointer)
  // clock: Clock
  // size: { width, height, top, left }
  // viewport: { width, height, factor, distance, aspect }
  // performance: { current, min, max, debounce, regress }
  // events: Event handlers
  // set: State setter
  // get: State getter
  // invalidate: Trigger re-render (for frameloop="demand")
  // advance: Advance one frame (for frameloop="never")

  return null
}
```

### Common useThree Patterns

```tsx
// Responsive to viewport
function ResponsiveObject() {
  const viewport = useThree((state) => state.viewport)
  return (
    <mesh scale={[viewport.width / 4, viewport.height / 4, 1]}>
      <planeGeometry />
      <meshBasicMaterial color="blue" />
    </mesh>
  )
}

// Manual render trigger
function TriggerRender() {
  const invalidate = useThree((state) => state.invalidate)

  const handleClick = () => {
    // Trigger render when using frameloop="demand"
    invalidate()
  }
}

// Update camera
function CameraController() {
  const camera = useThree((state) => state.camera)
  const set = useThree((state) => state.set)

  useEffect(() => {
    camera.position.set(10, 10, 10)
    camera.lookAt(0, 0, 0)
  }, [camera])
}
```

## JSX Elements

All Three.js objects are available as JSX elements (camelCase).

### Meshes

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Basic mesh structure
<mesh
  position={[0, 0, 0]}       // x, y, z
  rotation={[0, Math.PI, 0]} // Euler angles in radians
  scale={[1, 2, 1]}          // x, y, z or single number
  visible={true}
  castShadow
  receiveShadow
>
  <boxGeometry args={[1, 1, 1]} />
  <meshStandardMaterial color="red" />
</mesh>

// With ref
const meshRef = useRef<THREE.Mesh>(null!)
<mesh ref={meshRef} />
// meshRef.current is the THREE.Mesh
```

### Geometry args

Constructor arguments via `args` prop:

```tsx
// excerpt — not a complete module; see the surrounding section for context
// BoxGeometry(width, height, depth, widthSegments, heightSegments, depthSegments)
<boxGeometry args={[1, 1, 1, 1, 1, 1]} />

// SphereGeometry(radius, widthSegments, heightSegments)
<sphereGeometry args={[1, 32, 32]} />

// PlaneGeometry(width, height, widthSegments, heightSegments)
<planeGeometry args={[10, 10]} />

// CylinderGeometry(radiusTop, radiusBottom, height, radialSegments)
<cylinderGeometry args={[1, 1, 2, 32]} />
```

### Groups

```tsx
// excerpt — not a complete module; see the surrounding section for context
<group position={[5, 0, 0]} rotation={[0, Math.PI / 4, 0]}>
  <mesh position={[-1, 0, 0]}>
    <boxGeometry />
    <meshStandardMaterial color="red" />
  </mesh>
  <mesh position={[1, 0, 0]}>
    <boxGeometry />
    <meshStandardMaterial color="blue" />
  </mesh>
</group>
```

### Nested Properties

Use dashes for nested properties:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<mesh
  position-x={5}
  rotation-y={Math.PI}
  scale-z={2}
>
  <meshStandardMaterial
    color="red"
    metalness={0.8}
    roughness={0.2}
  />
</mesh>

// Shadow camera properties
<directionalLight
  castShadow
  shadow-mapSize={[2048, 2048]}
  shadow-camera-left={-10}
  shadow-camera-right={10}
  shadow-camera-top={10}
  shadow-camera-bottom={-10}
/>
```

### attach Prop

Control how children attach to parents:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<mesh>
  <boxGeometry />
  {/* Default: attaches as 'material' */}
  <meshStandardMaterial />
</mesh>

{/* Explicit attach */}
<mesh>
  <boxGeometry attach="geometry" />
  <meshStandardMaterial attach="material" />
</mesh>

{/* Array attachment */}
<mesh>
  <boxGeometry />
  <meshStandardMaterial attach="material-0" color="red" />
  <meshStandardMaterial attach="material-1" color="blue" />
</mesh>

{/* Custom attachment with function */}
<someObject>
  <texture
    attach={(parent, self) => {
      parent.map = self
      return () => { parent.map = null }  // Cleanup
    }}
  />
</someObject>
```

