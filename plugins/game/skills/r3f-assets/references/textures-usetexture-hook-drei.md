# Reference — Textures: useTexture Hook (Drei)

Part of the `r3f-assets` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Textures

### Quick Start

```tsx
import { Canvas } from '@react-three/fiber'
import { useTexture } from '@react-three/drei'

function TexturedBox() {
  const texture = useTexture('/textures/wood.jpg')

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}

export default function App() {
  return (
    <Canvas>
      <ambientLight />
      <TexturedBox />
    </Canvas>
  )
}
```

### useTexture Hook (Drei)

The recommended way to load textures in R3F.

#### Single Texture

```tsx
import { useTexture } from '@react-three/drei'

function SingleTexture() {
  const texture = useTexture('/textures/color.jpg')

  return (
    <mesh>
      <planeGeometry args={[5, 5]} />
      <meshBasicMaterial map={texture} />
    </mesh>
  )
}
```

#### Multiple Textures (Array)

```tsx
function MultipleTextures() {
  const [colorMap, normalMap, roughnessMap] = useTexture([
    '/textures/color.jpg',
    '/textures/normal.jpg',
    '/textures/roughness.jpg',
  ])

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial
        map={colorMap}
        normalMap={normalMap}
        roughnessMap={roughnessMap}
      />
    </mesh>
  )
}
```

#### Named Object (Recommended for PBR)

```tsx
function PBRTextures() {
  // Named object automatically spreads to material
  const textures = useTexture({
    map: '/textures/color.jpg',
    normalMap: '/textures/normal.jpg',
    roughnessMap: '/textures/roughness.jpg',
    metalnessMap: '/textures/metalness.jpg',
    aoMap: '/textures/ao.jpg',
    displacementMap: '/textures/displacement.jpg',
  })

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial
        {...textures}
        displacementScale={0.1}
      />
    </mesh>
  )
}
```

#### With Texture Configuration

```tsx
import { useTexture } from '@react-three/drei'
import * as THREE from 'three'

function ConfiguredTextures() {
  const textures = useTexture({
    map: '/textures/color.jpg',
    normalMap: '/textures/normal.jpg',
  }, (textures) => {
    // Configure textures after loading
    Object.values(textures).forEach(texture => {
      texture.wrapS = texture.wrapT = THREE.RepeatWrapping
      texture.repeat.set(4, 4)
    })
  })

  return (
    <mesh>
      <planeGeometry args={[10, 10]} />
      <meshStandardMaterial {...textures} />
    </mesh>
  )
}
```

#### Preloading

```tsx
import { useTexture } from '@react-three/drei'

// Preload at module level
useTexture.preload('/textures/hero.jpg')
useTexture.preload(['/tex1.jpg', '/tex2.jpg'])

function Component() {
  // Will be instant if preloaded
  const texture = useTexture('/textures/hero.jpg')
}
```

### useLoader for Textures (Core R3F)

```tsx
import { useLoader } from '@react-three/fiber'
import { TextureLoader } from 'three'

function TexturedMesh() {
  const texture = useLoader(TextureLoader, '/textures/color.jpg')

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}
```

```tsx
function MultiTexture() {
  const [colorMap, normalMap, roughnessMap] = useLoader(TextureLoader, [
    '/textures/color.jpg',
    '/textures/normal.jpg',
    '/textures/roughness.jpg',
  ])

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial
        map={colorMap}
        normalMap={normalMap}
        roughnessMap={roughnessMap}
      />
    </mesh>
  )
}
```

```tsx
import { useLoader } from '@react-three/fiber'
import { TextureLoader } from 'three'

// Preload
useLoader.preload(TextureLoader, '/textures/color.jpg')
useLoader.preload(TextureLoader, ['/tex1.jpg', '/tex2.jpg'])

// Clear cache
useLoader.clear(TextureLoader, '/textures/color.jpg')
```

