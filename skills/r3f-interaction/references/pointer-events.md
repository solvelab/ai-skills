# Reference — Pointer Events

Part of the `r3f-interaction` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'

function InteractiveMesh() {
  return (
    <mesh
      onClick={(e) => console.log('Clicked!', e.point)}
      onPointerOver={(e) => console.log('Hover')}
      onPointerOut={(e) => console.log('Unhover')}
    >
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}

export default function App() {
  return (
    <Canvas>
      <ambientLight />
      <InteractiveMesh />
      <OrbitControls />
    </Canvas>
  )
}
```

## Pointer Events

R3F provides built-in pointer events on mesh elements.

### Available Events

```tsx
// excerpt — not a complete module; see the surrounding section for context
<mesh
  // Click events
  onClick={(e) => {}}           // Click (pointerdown + pointerup on same object)
  onDoubleClick={(e) => {}}     // Double click
  onContextMenu={(e) => {}}     // Right click

  // Pointer events
  onPointerDown={(e) => {}}     // Pointer pressed
  onPointerUp={(e) => {}}       // Pointer released
  onPointerMove={(e) => {}}     // Pointer moved while over object
  onPointerOver={(e) => {}}     // Pointer enters object
  onPointerOut={(e) => {}}      // Pointer leaves object
  onPointerEnter={(e) => {}}    // Pointer enters object (no bubbling)
  onPointerLeave={(e) => {}}    // Pointer leaves object (no bubbling)
  onPointerMissed={(e) => {}}   // Click that missed all objects

  // Wheel
  onWheel={(e) => {}}           // Mouse wheel

  // Touch
  onPointerCancel={(e) => {}}   // Touch cancelled
>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>
```

### Event Object

```tsx
function InteractiveMesh() {
  const handleClick = (event) => {
    // Stop propagation to parent objects
    event.stopPropagation()

    // Event properties
    console.log({
      object: event.object,           // The mesh that was clicked
      point: event.point,             // World coordinates of intersection
      distance: event.distance,       // Distance from camera
      face: event.face,               // Intersected face
      faceIndex: event.faceIndex,     // Face index
      uv: event.uv,                   // UV coordinates at intersection
      normal: event.normal,           // Face normal
      camera: event.camera,           // Current camera
      ray: event.ray,                 // Ray used for intersection
      intersections: event.intersections, // All intersections
      nativeEvent: event.nativeEvent, // Original DOM event
      delta: event.delta,             // Click distance (useful for drag detection)
    })
  }

  return (
    <mesh onClick={handleClick}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### Hover Effects

```tsx
import { useState } from 'react'

function HoverableMesh() {
  const [hovered, setHovered] = useState(false)

  return (
    <mesh
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={(e) => {
        setHovered(false)
        document.body.style.cursor = 'default'
      }}
      scale={hovered ? 1.2 : 1}
    >
      <boxGeometry />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

### Selective Raycasting

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Disable raycasting for specific objects
<mesh raycast={() => null}>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>

// Or use layers
<mesh
  layers={1}  // Only raycast against layer 1
  onClick={() => console.log('clicked')}
>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>
```

