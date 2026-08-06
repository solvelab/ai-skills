# Reference — meshPhysicalMaterial (Advanced PBR)

Part of the `r3f-materials` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Quick Start

```tsx
import { Canvas } from '@react-three/fiber'

function Scene() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />

      <mesh>
        <boxGeometry />
        <meshStandardMaterial
          color="hotpink"
          roughness={0.5}
          metalness={0.5}
        />
      </mesh>
    </Canvas>
  )
}
```

## Material Types Overview

| Material | Use Case | Lighting |
|----------|----------|----------|
| meshBasicMaterial | Unlit, flat colors | No |
| meshLambertMaterial | Matte surfaces, fast | Yes (diffuse) |
| meshPhongMaterial | Shiny, specular | Yes |
| meshStandardMaterial | PBR, realistic | Yes (PBR) |
| meshPhysicalMaterial | Advanced PBR | Yes (PBR+) |
| meshToonMaterial | Cel-shaded | Yes (toon) |
| meshNormalMaterial | Debug normals | No |
| shaderMaterial | Custom GLSL | Custom |

## meshBasicMaterial

No lighting calculations. Always visible, fast.

```tsx
// excerpt — not a complete module; see the surrounding section for context
<mesh>
  <boxGeometry />
  <meshBasicMaterial
    color="red"
    transparent
    opacity={0.5}
    side={THREE.DoubleSide}  // FrontSide, BackSide, DoubleSide
    wireframe={false}
    map={colorTexture}
    alphaMap={alphaTexture}
    envMap={envTexture}
    fog={true}
  />
</mesh>
```

## meshStandardMaterial (PBR)

Physically-based rendering. Recommended for realistic results.

```tsx
import { useTexture } from '@react-three/drei'
import * as THREE from 'three'

function PBRMesh() {
  // Load PBR texture set
  const [colorMap, normalMap, roughnessMap, metalnessMap, aoMap] = useTexture([
    '/textures/color.jpg',
    '/textures/normal.jpg',
    '/textures/roughness.jpg',
    '/textures/metalness.jpg',
    '/textures/ao.jpg',
  ])

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial
        // Base color
        color="#ffffff"
        map={colorMap}

        // PBR properties
        roughness={1}         // 0 = mirror, 1 = diffuse
        roughnessMap={roughnessMap}
        metalness={0}         // 0 = dielectric, 1 = metal
        metalnessMap={metalnessMap}

        // Surface detail
        normalMap={normalMap}
        normalScale={[1, 1]}

        // Ambient occlusion (requires uv2)
        aoMap={aoMap}
        aoMapIntensity={1}

        // Emissive
        emissive="#000000"
        emissiveIntensity={1}
        emissiveMap={emissiveTexture}

        // Environment
        envMap={envTexture}
        envMapIntensity={1}

        // Other
        flatShading={false}
        fog={true}
        transparent={false}
      />
    </mesh>
  )
}
```

## meshPhysicalMaterial (Advanced PBR)

Extends Standard with clearcoat, transmission, sheen, etc.

```tsx
// Glass material
function Glass() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshPhysicalMaterial
        color="#ffffff"
        metalness={0}
        roughness={0}
        transmission={1}      // 0 = opaque, 1 = fully transparent
        thickness={0.5}       // Volume thickness for refraction
        ior={1.5}             // Index of refraction (glass ~1.5)
        envMapIntensity={1}
      />
    </mesh>
  )
}

// Car paint
function CarPaint() {
  return (
    <mesh>
      <boxGeometry />
      <meshPhysicalMaterial
        color="#ff0000"
        metalness={0.9}
        roughness={0.5}
        clearcoat={1}              // Clearcoat layer strength
        clearcoatRoughness={0.1}   // Clearcoat roughness
      />
    </mesh>
  )
}

// Fabric/velvet (sheen)
function Fabric() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshPhysicalMaterial
        color="#8844aa"
        roughness={0.8}
        sheen={1}
        sheenRoughness={0.5}
        sheenColor="#ff88ff"
      />
    </mesh>
  )
}

// Iridescent (soap bubbles)
function Iridescent() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshPhysicalMaterial
        color="#ffffff"
        iridescence={1}
        iridescenceIOR={1.3}
        iridescenceThicknessRange={[100, 400]}
      />
    </mesh>
  )
}
```

