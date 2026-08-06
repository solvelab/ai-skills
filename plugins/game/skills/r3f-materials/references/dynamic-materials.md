# Reference — Dynamic Materials

Part of the `r3f-materials` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Dynamic Materials

### Updating Material Properties

```tsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function AnimatedMaterial() {
  const materialRef = useRef<THREE.MeshStandardMaterial>(null!)

  useFrame(({ clock }) => {
    const t = clock.elapsedTime

    // Update color
    materialRef.current.color.setHSL((t * 0.1) % 1, 1, 0.5)

    // Update properties
    materialRef.current.roughness = (Math.sin(t) + 1) / 2
  })

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial ref={materialRef} />
    </mesh>
  )
}
```

### Shared Materials

```tsx
import { useMemo } from 'react'
import * as THREE from 'three'

function SharedMaterial() {
  // Create once, use many times
  const material = useMemo(() =>
    new THREE.MeshStandardMaterial({ color: 'red' }),
  [])

  return (
    <>
      <mesh position={[-2, 0, 0]} material={material}>
        <boxGeometry />
      </mesh>
      <mesh position={[0, 0, 0]} material={material}>
        <sphereGeometry />
      </mesh>
      <mesh position={[2, 0, 0]} material={material}>
        <coneGeometry />
      </mesh>
    </>
  )
}
```

## Multiple Materials

```tsx
// excerpt — not a complete module; see the surrounding section for context
// Different materials per face (BoxGeometry has 6 material groups)
<mesh>
  <boxGeometry />
  <meshStandardMaterial attach="material-0" color="red" />   {/* +X */}
  <meshStandardMaterial attach="material-1" color="green" /> {/* -X */}
  <meshStandardMaterial attach="material-2" color="blue" />  {/* +Y */}
  <meshStandardMaterial attach="material-3" color="yellow" />{/* -Y */}
  <meshStandardMaterial attach="material-4" color="cyan" />  {/* +Z */}
  <meshStandardMaterial attach="material-5" color="magenta" />{/* -Z */}
</mesh>
```

## Material with Textures

```tsx
import { useTexture } from '@react-three/drei'
import * as THREE from 'three'

function TexturedMaterial() {
  // Named object pattern (recommended)
  const textures = useTexture({
    map: '/textures/color.jpg',
    normalMap: '/textures/normal.jpg',
    roughnessMap: '/textures/roughness.jpg',
  })

  // Set texture properties
  Object.values(textures).forEach(texture => {
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping
    texture.repeat.set(2, 2)
  })

  return (
    <mesh>
      <planeGeometry args={[5, 5]} />
      <meshStandardMaterial {...textures} />
    </mesh>
  )
}
```

## Emissive Materials (Glow)

```tsx
// excerpt — not a complete module; see the surrounding section for context
// For bloom effect, emissive colors should exceed normal range
<meshStandardMaterial
  color="black"
  emissive="#ff0000"
  emissiveIntensity={2}    // > 1 for bloom
  toneMapped={false}       // Required for colors > 1
/>

// With emissive map
<meshStandardMaterial
  emissive="white"
  emissiveMap={emissiveTexture}
  emissiveIntensity={2}
  toneMapped={false}
/>
```

## Environment Maps

Environment maps and IBL live in r3f-lighting; loading them is covered in r3f-assets. On the material side, `envMapIntensity` scales the contribution of the environment map on `meshStandardMaterial`/`meshPhysicalMaterial`.

## Custom Shader Materials

Reach for a custom shader material when Drei's special materials (Reflector/Wobble/Distort/Transmission) don't cover the visual effect you need. Custom shader materials (shaderMaterial, uniforms, GLSL) are covered in r3f-shaders.

## Performance Tips

1. **Reuse materials**: Same material instance = batched draw calls
2. **Avoid transparent**: Requires sorting, slower
3. **Use alphaTest over transparent**: When possible, faster
4. **Simpler materials**: Basic > Lambert > Phong > Standard > Physical
5. **Limit texture sizes**: 1024-2048 usually sufficient

```tsx
// Material caching pattern
const materialCache = new Map()

function getCachedMaterial(color) {
  const key = color.toString()
  if (!materialCache.has(key)) {
    materialCache.set(key, new THREE.MeshStandardMaterial({ color }))
  }
  return materialCache.get(key)
}
```

