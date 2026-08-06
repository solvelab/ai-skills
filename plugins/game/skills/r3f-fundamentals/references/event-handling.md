# Reference — Event Handling

Part of the `r3f-fundamentals` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Event Handling

R3F provides React-style events on 3D objects.

```tsx
function InteractiveBox() {
  const [hovered, setHovered] = useState(false)
  const [clicked, setClicked] = useState(false)

  return (
    <mesh
      onClick={(e) => {
        e.stopPropagation()  // Prevent bubbling
        setClicked(!clicked)

        // Event properties:
        console.log(e.object)      // THREE.Mesh
        console.log(e.point)       // Vector3 - intersection point
        console.log(e.distance)    // Distance from camera
        console.log(e.face)        // Intersected face
        console.log(e.faceIndex)   // Face index
        console.log(e.uv)          // UV coordinates
        console.log(e.normal)      // Face normal
        console.log(e.pointer)     // Normalized pointer coords
        console.log(e.ray)         // Raycaster ray
        console.log(e.camera)      // Camera
        console.log(e.delta)       // Distance moved (drag events)
      }}
      onContextMenu={(e) => console.log('Right click')}
      onDoubleClick={(e) => console.log('Double click')}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={(e) => {
        setHovered(false)
        document.body.style.cursor = 'default'
      }}
      onPointerDown={(e) => console.log('Pointer down')}
      onPointerUp={(e) => console.log('Pointer up')}
      onPointerMove={(e) => console.log('Moving over mesh')}
      onWheel={(e) => console.log('Wheel:', e.deltaY)}
      scale={hovered ? 1.2 : 1}
    >
      <boxGeometry />
      <meshStandardMaterial color={clicked ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

### Event Propagation

Events bubble up through the scene graph:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<group onClick={(e) => console.log('Group clicked')}>
  <mesh onClick={(e) => {
    e.stopPropagation()  // Stop bubbling to group
    console.log('Mesh clicked')
  }}>
    <boxGeometry />
    <meshStandardMaterial />
  </mesh>
</group>
```

## primitive Element

Use existing Three.js objects directly:

```tsx
import * as THREE from 'three'

// Existing object
const geometry = new THREE.BoxGeometry()
const material = new THREE.MeshStandardMaterial({ color: 'red' })
const mesh = new THREE.Mesh(geometry, material)

function Scene() {
  return <primitive object={mesh} position={[0, 1, 0]} />
}

// Common with loaded models
function Model({ gltf }) {
  return <primitive object={gltf.scene} />
}
```

## extend Function

Register custom Three.js classes for JSX use:

```tsx
import { extend } from '@react-three/fiber'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

// Extend once (usually at module level)
extend({ OrbitControls })

// Now use as JSX
function Scene() {
  const { camera, gl } = useThree()
  return <orbitControls args={[camera, gl.domElement]} />
}

// TypeScript declaration (v9 pattern)
import { ThreeElement } from '@react-three/fiber'

declare module '@react-three/fiber' {
  interface ThreeElements {
    orbitControls: ThreeElement<typeof OrbitControls>
  }
}
```

## Refs and Imperative Access

```tsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function MeshWithRef() {
  const meshRef = useRef<THREE.Mesh>(null)
  const materialRef = useRef<THREE.MeshStandardMaterial>(null)

  useEffect(() => {
    if (meshRef.current) {
      // Direct Three.js access
      meshRef.current.geometry.computeBoundingBox()
      console.log(meshRef.current.geometry.boundingBox)
    }
  }, [])

  useFrame(() => {
    if (materialRef.current) {
      materialRef.current.color.setHSL(Math.random(), 1, 0.5)
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial ref={materialRef} />
    </mesh>
  )
}
```

## Performance Patterns

### Avoiding Re-renders

```tsx
// excerpt — not a complete module; see the surrounding section for context
// BAD: Creates new object every render
<mesh position={[x, y, z]} />

// GOOD: Mutate existing position
const meshRef = useRef<THREE.Mesh>(null!)
useFrame(() => {
  meshRef.current.position.x = x
})
<mesh ref={meshRef} />

// GOOD: Use useMemo for static values
const position = useMemo(() => [x, y, z], [x, y, z])
<mesh position={position} />
```

### Component Isolation

```tsx
// Isolate animated components to prevent parent re-renders
function Scene() {
  return (
    <>
      <StaticEnvironment />
      <AnimatedObject />  {/* Only this re-renders on animation */}
    </>
  )
}

function AnimatedObject() {
  const ref = useRef<THREE.Mesh>(null!)
  useFrame((_, delta) => {
    ref.current.rotation.y += delta
  })
  return <mesh ref={ref}><boxGeometry /></mesh>
}
```

### Dispose

R3F auto-disposes geometries, materials, and textures. Override with:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<mesh dispose={null}>  {/* Prevent auto-dispose */}
  <boxGeometry />
  <meshStandardMaterial />
</mesh>
```

