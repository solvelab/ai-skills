# Reference — Custom BufferGeometry

Part of the `r3f-geometry` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Custom BufferGeometry

### Basic Custom Geometry

```tsx
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

function CustomTriangle() {
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()

    // Vertices (3 floats per vertex: x, y, z)
    const vertices = new Float32Array([
      -1, -1, 0,  // vertex 0
       1, -1, 0,  // vertex 1
       0,  1, 0,  // vertex 2
    ])

    // Normals (pointing toward camera)
    const normals = new Float32Array([
      0, 0, 1,
      0, 0, 1,
      0, 0, 1,
    ])

    // UVs
    const uvs = new Float32Array([
      0, 0,
      1, 0,
      0.5, 1,
    ])

    geo.setAttribute('position', new THREE.BufferAttribute(vertices, 3))
    geo.setAttribute('normal', new THREE.BufferAttribute(normals, 3))
    geo.setAttribute('uv', new THREE.BufferAttribute(uvs, 2))

    return geo
  }, [])

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="cyan" side={THREE.DoubleSide} />
    </mesh>
  )
}
```

### Indexed Geometry

```tsx
function CustomQuad() {
  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()

    // 4 vertices for a quad
    const vertices = new Float32Array([
      -1, -1, 0,  // 0: bottom-left
       1, -1, 0,  // 1: bottom-right
       1,  1, 0,  // 2: top-right
      -1,  1, 0,  // 3: top-left
    ])

    // Indices to form 2 triangles
    const indices = new Uint16Array([
      0, 1, 2,  // triangle 1
      0, 2, 3,  // triangle 2
    ])

    const normals = new Float32Array([
      0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1,
    ])

    const uvs = new Float32Array([
      0, 0,  1, 0,  1, 1,  0, 1,
    ])

    geo.setAttribute('position', new THREE.BufferAttribute(vertices, 3))
    geo.setAttribute('normal', new THREE.BufferAttribute(normals, 3))
    geo.setAttribute('uv', new THREE.BufferAttribute(uvs, 2))
    geo.setIndex(new THREE.BufferAttribute(indices, 1))

    return geo
  }, [])

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="lime" side={THREE.DoubleSide} />
    </mesh>
  )
}
```

### Dynamic Geometry

```tsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function WavyPlane() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame(({ clock }) => {
    const positions = meshRef.current.geometry.attributes.position
    const time = clock.elapsedTime

    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i)
      const y = positions.getY(i)
      positions.setZ(i, Math.sin(x * 2 + time) * Math.cos(y * 2 + time) * 0.5)
    }

    positions.needsUpdate = true
    meshRef.current.geometry.computeVertexNormals()
  })

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[10, 10, 32, 32]} />
      <meshStandardMaterial color="royalblue" side={THREE.DoubleSide} />
    </mesh>
  )
}
```

## Drei Instancing

Efficient rendering of many identical objects.

### Instances Component

```tsx
import { Instances, Instance } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function InstancedBoxes() {
  const count = 1000

  return (
    <Instances limit={count} range={count}>
      <boxGeometry args={[0.5, 0.5, 0.5]} />
      <meshStandardMaterial />

      {Array.from({ length: count }, (_, i) => (
        <AnimatedInstance key={i} index={i} />
      ))}
    </Instances>
  )
}

function AnimatedInstance({ index }) {
  const ref = useRef<THREE.Object3D>(null!)

  // Random initial position
  const position = useMemo(() => [
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20,
    (Math.random() - 0.5) * 20,
  ], [])

  const color = useMemo(() =>
    ['red', 'blue', 'green', 'yellow', 'purple'][index % 5],
  [index])

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    ref.current.rotation.x = t + index
    ref.current.rotation.y = t * 0.5 + index
  })

  return (
    <Instance
      ref={ref}
      position={position}
      color={color}
      scale={0.5 + Math.random() * 0.5}
    />
  )
}
```

### Merged Geometry

For static instances, merge geometry for best performance:

```tsx
import { Merged } from '@react-three/drei'
import { useMemo } from 'react'
import * as THREE from 'three'

function MergedMeshes() {
  // Create geometries to merge
  const meshes = useMemo(() => ({
    Sphere: new THREE.SphereGeometry(0.5, 32, 32),
    Box: new THREE.BoxGeometry(1, 1, 1),
    Cone: new THREE.ConeGeometry(0.5, 1, 32),
  }), [])

  return (
    <Merged meshes={meshes}>
      {({ Sphere, Box, Cone }) => (
        <>
          <Sphere position={[-2, 0, 0]} color="red" />
          <Sphere position={[-2, 2, 0]} color="orange" />
          <Box position={[0, 0, 0]} color="blue" />
          <Box position={[0, 2, 0]} color="cyan" />
          <Cone position={[2, 0, 0]} color="green" />
          <Cone position={[2, 2, 0]} color="lime" />
        </>
      )}
    </Merged>
  )
}
```

