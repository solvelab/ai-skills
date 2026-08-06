# Reference — Points (Particle Systems)

Part of the `r3f-geometry` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Points (Particle Systems)

### Basic Points

```tsx
import { Points, Point, PointMaterial } from '@react-three/drei'

function ParticleField() {
  const count = 5000

  return (
    <Points limit={count}>
      <PointMaterial
        transparent
        vertexColors
        size={0.05}
        sizeAttenuation
        depthWrite={false}
      />
      {Array.from({ length: count }, (_, i) => (
        <Point
          key={i}
          position={[
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10,
          ]}
          color={`hsl(${Math.random() * 360}, 100%, 50%)`}
        />
      ))}
    </Points>
  )
}
```

### Buffer-Based Points (High Performance)

```tsx
import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function BufferParticles() {
  const count = 10000
  const pointsRef = useRef<THREE.Points>(null!)

  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(count * 3)
    const colors = new Float32Array(count * 3)

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10
      positions[i * 3 + 1] = (Math.random() - 0.5) * 10
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10

      colors[i * 3] = Math.random()
      colors[i * 3 + 1] = Math.random()
      colors[i * 3 + 2] = Math.random()
    }

    return { positions, colors }
  }, [])

  useFrame(({ clock }) => {
    pointsRef.current.rotation.y = clock.elapsedTime * 0.1
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.05} vertexColors sizeAttenuation />
    </points>
  )
}
```

## Lines

### Basic Line

```tsx
import { Line } from '@react-three/drei'

function BasicLine() {
  const points = [
    [0, 0, 0],
    [1, 1, 0],
    [2, 0, 0],
    [3, 1, 0],
  ]

  return (
    <Line
      points={points}
      color="red"
      lineWidth={2}
    />
  )
}
```

### Curved Line

```tsx
import { CatmullRomLine, QuadraticBezierLine, CubicBezierLine } from '@react-three/drei'

function CurvedLines() {
  return (
    <>
      {/* Smooth curve through points */}
      <CatmullRomLine
        points={[[0, 0, 0], [1, 1, 0], [2, 0, 0], [3, 1, 0]]}
        color="blue"
        lineWidth={2}
        segments={64}
      />

      {/* Quadratic bezier */}
      <QuadraticBezierLine
        start={[0, 0, 0]}
        mid={[1, 2, 0]}
        end={[2, 0, 0]}
        color="green"
        lineWidth={2}
      />

      {/* Cubic bezier */}
      <CubicBezierLine
        start={[0, 0, 0]}
        midA={[0.5, 2, 0]}
        midB={[1.5, -1, 0]}
        end={[2, 0, 0]}
        color="purple"
        lineWidth={2}
      />
    </>
  )
}
```

### Dashed Line

```tsx
// excerpt — not a complete module; see the surrounding section for context
<Line
  points={[[0, 0, 0], [5, 0, 0]]}
  color="white"
  lineWidth={2}
  dashed
  dashScale={50}
  dashSize={0.5}
  dashOffset={0}
  gapSize={0.2}
/>
```

## Edges and Wireframe

```tsx
import { Edges } from '@react-three/drei'

function BoxWithEdges() {
  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
      <Edges
        scale={1.1}
        threshold={15}  // Display edges with angle > 15 degrees
        color="black"
      />
    </mesh>
  )
}

// Wireframe material
function WireframeBox() {
  return (
    <mesh>
      <boxGeometry />
      <meshBasicMaterial color="cyan" wireframe />
    </mesh>
  )
}
```

## Text Geometry

### Using Drei Text3D

```tsx
import { Text3D, Center } from '@react-three/drei'

function Text3DExample() {
  return (
    <Center>
      <Text3D
        font="/fonts/helvetiker_regular.typeface.json"
        size={1}
        height={0.2}
        curveSegments={12}
        bevelEnabled
        bevelThickness={0.02}
        bevelSize={0.02}
        bevelOffset={0}
        bevelSegments={5}
      >
        Hello R3F
        <meshStandardMaterial color="gold" />
      </Text3D>
    </Center>
  )
}
```

## Geometry Utilities

### Center Geometry

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { Center } from '@react-three/drei'

function CenteredModel() {
  return (
    <Center>
      <mesh>
        <boxGeometry args={[2, 1, 0.5]} />
        <meshStandardMaterial />
      </mesh>
    </Center>
  )
}

// With options
<Center top left>  {/* Align to top-left */}
  <Model />
</Center>

// Get bounding info
<Center onCentered={({ width, height, depth, boundingBox }) => {
  console.log('Dimensions:', width, height, depth)
}}>
  <Model />
</Center>
```

### Compute Bounds

```tsx
import { useBounds, Bounds } from '@react-three/drei'

function FitToView() {
  return (
    <Bounds fit clip observe margin={1.2}>
      <SelectToZoom />
    </Bounds>
  )
}

function SelectToZoom() {
  const bounds = useBounds()

  return (
    <mesh
      onClick={(e) => {
        e.stopPropagation()
        bounds.refresh(e.object).fit()
      }}
    >
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

## Performance Tips

1. **Reuse geometries**: Same geometry instance = better batching
2. **Use Instances**: For many identical objects
3. **Merge static meshes**: Use `<Merged>` for static scenes
4. **Appropriate segment counts**: Balance quality vs performance
5. **Dispose unused geometry**: R3F handles this automatically

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Good segment counts
<sphereGeometry args={[1, 32, 32]} />   // Standard quality
<sphereGeometry args={[1, 64, 64]} />   // High quality
<sphereGeometry args={[1, 16, 16]} />   // Performance mode

// Reuse geometry
const sharedGeometry = useMemo(() => new THREE.BoxGeometry(), [])

<mesh geometry={sharedGeometry} position={[0, 0, 0]} />
<mesh geometry={sharedGeometry} position={[2, 0, 0]} />
<mesh geometry={sharedGeometry} position={[4, 0, 0]} />
```

