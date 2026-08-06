# Reference — Built-in Geometries

Part of the `r3f-geometry` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'

function Scene() {
  return (
    <Canvas>
      <ambientLight />
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="hotpink" />
      </mesh>
    </Canvas>
  )
}
```

## Built-in Geometries

All Three.js geometries are available as JSX elements. The `args` prop passes constructor arguments.

### Basic Shapes

```tsx
// excerpt — not a complete module; see the surrounding section for context
// BoxGeometry(width, height, depth, widthSegments, heightSegments, depthSegments)
<boxGeometry args={[1, 1, 1]} />
<boxGeometry args={[2, 1, 0.5, 2, 2, 2]} />

// SphereGeometry(radius, widthSegments, heightSegments, phiStart, phiLength, thetaStart, thetaLength)
<sphereGeometry args={[1, 32, 32]} />
<sphereGeometry args={[1, 64, 64]} />  // High quality
<sphereGeometry args={[1, 32, 32, 0, Math.PI]} />  // Hemisphere

// PlaneGeometry(width, height, widthSegments, heightSegments)
<planeGeometry args={[10, 10]} />
<planeGeometry args={[10, 10, 32, 32]} />  // Subdivided for displacement

// CircleGeometry(radius, segments, thetaStart, thetaLength)
<circleGeometry args={[1, 32]} />
<circleGeometry args={[1, 32, 0, Math.PI]} />  // Semicircle

// CylinderGeometry(radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded)
<cylinderGeometry args={[1, 1, 2, 32]} />
<cylinderGeometry args={[0, 1, 2, 32]} />  // Cone
<cylinderGeometry args={[1, 1, 2, 6]} />   // Hexagonal prism

// ConeGeometry(radius, height, radialSegments, heightSegments, openEnded)
<coneGeometry args={[1, 2, 32]} />

// TorusGeometry(radius, tube, radialSegments, tubularSegments, arc)
<torusGeometry args={[1, 0.4, 16, 100]} />

// TorusKnotGeometry(radius, tube, tubularSegments, radialSegments, p, q)
<torusKnotGeometry args={[1, 0.4, 100, 16, 2, 3]} />

// RingGeometry(innerRadius, outerRadius, thetaSegments, phiSegments)
<ringGeometry args={[0.5, 1, 32]} />
```

### Advanced Shapes

```tsx
// excerpt — not a complete module; see the surrounding section for context
// CapsuleGeometry(radius, length, capSegments, radialSegments)
<capsuleGeometry args={[0.5, 1, 4, 16]} />

// Polyhedrons
<dodecahedronGeometry args={[1, 0]} />  // radius, detail
<icosahedronGeometry args={[1, 0]} />
<octahedronGeometry args={[1, 0]} />
<tetrahedronGeometry args={[1, 0]} />

// Higher detail = more subdivisions
<icosahedronGeometry args={[1, 4]} />  // Approximates sphere
```

### Path-Based Shapes

```tsx
import * as THREE from 'three'

// LatheGeometry - revolve points around Y axis
function LatheShape() {
  const points = [
    new THREE.Vector2(0, 0),
    new THREE.Vector2(0.5, 0),
    new THREE.Vector2(0.5, 0.5),
    new THREE.Vector2(0.3, 1),
    new THREE.Vector2(0, 1),
  ]

  return (
    <mesh>
      <latheGeometry args={[points, 32]} />
      <meshStandardMaterial color="gold" side={THREE.DoubleSide} />
    </mesh>
  )
}

// TubeGeometry - extrude along a curve
function TubeShape() {
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-2, 0, 0),
    new THREE.Vector3(-1, 1, 0),
    new THREE.Vector3(1, -1, 0),
    new THREE.Vector3(2, 0, 0),
  ])

  return (
    <mesh>
      <tubeGeometry args={[curve, 64, 0.2, 8, false]} />
      <meshStandardMaterial color="blue" />
    </mesh>
  )
}

// ExtrudeGeometry - extrude a 2D shape
function ExtrudedShape() {
  const shape = new THREE.Shape()
  shape.moveTo(0, 0)
  shape.lineTo(1, 0)
  shape.lineTo(1, 1)
  shape.lineTo(0, 1)
  shape.lineTo(0, 0)

  const extrudeSettings = {
    steps: 2,
    depth: 0.5,
    bevelEnabled: true,
    bevelThickness: 0.1,
    bevelSize: 0.1,
    bevelSegments: 3,
  }

  return (
    <mesh>
      <extrudeGeometry args={[shape, extrudeSettings]} />
      <meshStandardMaterial color="purple" />
    </mesh>
  )
}
```

## Drei Shape Helpers

@react-three/drei provides convenient shape components.

```tsx
import {
  Box, Sphere, Plane, Circle, Cylinder, Cone,
  Torus, TorusKnot, Ring, Capsule, Dodecahedron,
  Icosahedron, Octahedron, Tetrahedron, RoundedBox
} from '@react-three/drei'

function DreiShapes() {
  return (
    <>
      {/* All shapes accept mesh props directly */}
      <Box args={[1, 1, 1]} position={[-3, 0, 0]}>
        <meshStandardMaterial color="red" />
      </Box>

      <Sphere args={[0.5, 32, 32]} position={[-1, 0, 0]}>
        <meshStandardMaterial color="blue" />
      </Sphere>

      <Cylinder args={[0.5, 0.5, 1, 32]} position={[1, 0, 0]}>
        <meshStandardMaterial color="green" />
      </Cylinder>

      {/* RoundedBox - box with rounded edges */}
      <RoundedBox
        args={[1, 1, 1]}      // width, height, depth
        radius={0.1}          // border radius
        smoothness={4}        // smoothness of rounded edges
        position={[3, 0, 0]}
      >
        <meshStandardMaterial color="orange" />
      </RoundedBox>
    </>
  )
}
```

