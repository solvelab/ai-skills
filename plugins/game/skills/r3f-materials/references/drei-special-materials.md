# Reference — Drei Special Materials

Part of the `r3f-materials` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Drei Special Materials

### MeshReflectorMaterial

Realistic mirror-like reflections.

```tsx
import { MeshReflectorMaterial } from '@react-three/drei'

function ReflectiveFloor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
      <planeGeometry args={[10, 10]} />
      <MeshReflectorMaterial
        blur={[400, 100]}         // Blur amount [x, y]
        resolution={1024}         // Reflection resolution
        mixBlur={1}               // Mix blur with reflection
        mixStrength={0.5}         // Reflection strength
        roughness={1}
        depthScale={1.2}
        minDepthThreshold={0.4}
        maxDepthThreshold={1.4}
        color="#333"
        metalness={0.5}
        mirror={0.5}
      />
    </mesh>
  )
}
```

### MeshWobbleMaterial

Animated wobble effect.

```tsx
import { MeshWobbleMaterial } from '@react-three/drei'

function WobblyMesh() {
  return (
    <mesh>
      <torusKnotGeometry args={[1, 0.4, 100, 16]} />
      <MeshWobbleMaterial
        factor={1}       // Wobble amplitude
        speed={2}        // Wobble speed
        color="hotpink"
        metalness={0}
        roughness={0.5}
      />
    </mesh>
  )
}
```

### MeshDistortMaterial

Perlin noise distortion.

```tsx
import { MeshDistortMaterial } from '@react-three/drei'

function DistortedMesh() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <MeshDistortMaterial
        distort={0.5}    // Distortion amount
        speed={2}        // Animation speed
        color="cyan"
        roughness={0.2}
      />
    </mesh>
  )
}
```

### MeshTransmissionMaterial

Better glass/refractive materials.

```tsx
import { MeshTransmissionMaterial } from '@react-three/drei'

function GlassSphere() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <MeshTransmissionMaterial
        backside              // Render backside
        samples={16}          // Refraction samples
        resolution={1024}     // Buffer resolution
        transmission={1}      // Transmission factor
        roughness={0.0}
        thickness={0.5}       // Volume thickness
        ior={1.5}             // Index of refraction
        chromaticAberration={0.06}
        anisotropy={0.1}
        distortion={0.0}
        distortionScale={0.3}
        temporalDistortion={0.5}
        clearcoat={1}
        attenuationDistance={0.5}
        attenuationColor="#ffffff"
        color="#c9ffa1"
      />
    </mesh>
  )
}
```

### MeshDiscardMaterial

Discard fragments - useful for shadows only.

```tsx
import { MeshDiscardMaterial } from '@react-three/drei'

function ShadowOnlyMesh() {
  return (
    <mesh castShadow>
      <boxGeometry />
      <MeshDiscardMaterial />  {/* Invisible but casts shadows */}
    </mesh>
  )
}
```

## Points and Lines Materials

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Points material
<points>
  <bufferGeometry />
  <pointsMaterial
    size={0.1}
    sizeAttenuation={true}
    color="white"
    map={spriteTexture}
    transparent
    alphaTest={0.5}
    vertexColors
  />
</points>

// Line materials
<line>
  <bufferGeometry />
  <lineBasicMaterial color="white" linewidth={1} />
</line>

<line>
  <bufferGeometry />
  <lineDashedMaterial
    color="white"
    dashSize={0.5}
    gapSize={0.25}
    scale={1}
  />
</line>
```

## Common Material Properties

All materials share these base properties:

```tsx
// excerpt — not a complete module; see the surrounding section for context
<meshStandardMaterial
  // Visibility
  visible={true}
  transparent={false}
  opacity={1}
  alphaTest={0}          // Discard pixels with alpha < value

  // Rendering
  side={THREE.FrontSide} // FrontSide, BackSide, DoubleSide
  depthTest={true}
  depthWrite={true}
  colorWrite={true}

  // Blending
  blending={THREE.NormalBlending}
  // NormalBlending, AdditiveBlending, SubtractiveBlending, MultiplyBlending

  // Polygon offset (z-fighting fix)
  polygonOffset={false}
  polygonOffsetFactor={0}
  polygonOffsetUnits={0}

  // Misc
  dithering={false}
  toneMapped={true}
/>
```

