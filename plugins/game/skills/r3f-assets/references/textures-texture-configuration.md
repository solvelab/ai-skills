# Reference — Textures: Texture Configuration

Part of the `r3f-assets` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

### Texture Configuration

#### Wrapping Modes

```tsx
import * as THREE from 'three'

function ConfigureWrapping() {
  const texture = useTexture('/textures/tile.jpg', (tex) => {
    // Wrapping
    tex.wrapS = THREE.RepeatWrapping      // Horizontal: ClampToEdgeWrapping, RepeatWrapping, MirroredRepeatWrapping
    tex.wrapT = THREE.RepeatWrapping      // Vertical

    // Repeat
    tex.repeat.set(4, 4)                  // Tile 4x4

    // Offset
    tex.offset.set(0.5, 0.5)              // Shift UV

    // Rotation
    tex.rotation = Math.PI / 4            // Rotate 45 degrees
    tex.center.set(0.5, 0.5)              // Rotation pivot
  })

  return (
    <mesh>
      <planeGeometry args={[10, 10]} />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}
```

#### Filtering

```tsx
function ConfigureFiltering() {
  const texture = useTexture('/textures/color.jpg', (tex) => {
    // Minification (texture larger than screen pixels)
    tex.minFilter = THREE.LinearMipmapLinearFilter  // Smooth with mipmaps (default)
    tex.minFilter = THREE.NearestFilter             // Pixelated
    tex.minFilter = THREE.LinearFilter              // Smooth, no mipmaps

    // Magnification (texture smaller than screen pixels)
    tex.magFilter = THREE.LinearFilter   // Smooth (default)
    tex.magFilter = THREE.NearestFilter  // Pixelated (retro style)

    // Anisotropic filtering (sharper at angles)
    tex.anisotropy = 16  // Usually renderer.capabilities.getMaxAnisotropy()

    // Generate mipmaps
    tex.generateMipmaps = true  // Default
  })
}
```

#### Color Space

Important for accurate colors.

```tsx
function ConfigureColorSpace() {
  const [colorMap, normalMap, roughnessMap] = useTexture([
    '/textures/color.jpg',
    '/textures/normal.jpg',
    '/textures/roughness.jpg',
  ], (textures) => {
    // Color/albedo textures should use sRGB
    textures[0].colorSpace = THREE.SRGBColorSpace

    // Data textures (normal, roughness, metalness, ao) use Linear
    // This is the default, so usually no action needed
    // textures[1].colorSpace = THREE.LinearSRGBColorSpace
    // textures[2].colorSpace = THREE.LinearSRGBColorSpace
  })
}
```

### Environment Maps

Short reference for loading environment/cube textures as data (not for lighting setup — see below).

```tsx
import { useEnvironment } from '@react-three/drei'

// Preset
const envMap = useEnvironment({ preset: 'sunset' })
// Presets: apartment, city, dawn, forest, lobby, night, park, studio, sunset, warehouse

// Custom HDR file
const envMap = useEnvironment({ files: '/hdri/studio.hdr' })

// Cube map
const envMap = useEnvironment({
  files: ['px.jpg', 'nx.jpg', 'py.jpg', 'ny.jpg', 'pz.jpg', 'nz.jpg'],
  path: '/textures/',
})
```

```tsx
import { useCubeTexture } from '@react-three/drei'

const envMap = useCubeTexture(
  ['px.jpg', 'nx.jpg', 'py.jpg', 'ny.jpg', 'pz.jpg', 'nz.jpg'],
  { path: '/textures/cube/' }
)
```

Environment lighting and IBL setup live in the r3f-lighting skill.

### Video Textures

```tsx
import { useVideoTexture } from '@react-three/drei'

function VideoPlane() {
  const texture = useVideoTexture('/video.mp4', {
    start: true,
    loop: true,
    muted: true,
    crossOrigin: 'anonymous',
  })

  return (
    <mesh>
      <planeGeometry args={[16/9 * 2, 2]} />
      <meshBasicMaterial map={texture} toneMapped={false} />
    </mesh>
  )
}
```

### Canvas Textures

```tsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function CanvasTexture() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const textureRef = useRef()

  useEffect(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 256
    canvas.height = 256
    const ctx = canvas.getContext('2d')

    // Draw on canvas
    ctx.fillStyle = 'red'
    ctx.fillRect(0, 0, 256, 256)
    ctx.fillStyle = 'white'
    ctx.font = '48px Arial'
    ctx.fillText('Hello', 50, 150)

    textureRef.current = new THREE.CanvasTexture(canvas)
  }, [])

  // Update texture dynamically
  useFrame(({ clock }) => {
    if (textureRef.current) {
      const canvas = textureRef.current.image
      const ctx = canvas.getContext('2d')
      ctx.fillStyle = `hsl(${clock.elapsedTime * 50}, 100%, 50%)`
      ctx.fillRect(0, 0, 256, 256)
      textureRef.current.needsUpdate = true
    }
  })

  return (
    <mesh ref={meshRef}>
      <planeGeometry args={[2, 2]} />
      <meshBasicMaterial map={textureRef.current} />
    </mesh>
  )
}
```

### Data Textures

```tsx
import { useMemo } from 'react'
import * as THREE from 'three'

function NoiseTexture() {
  const texture = useMemo(() => {
    const size = 256
    const data = new Uint8Array(size * size * 4)

    for (let i = 0; i < size * size; i++) {
      const value = Math.random() * 255
      data[i * 4] = value
      data[i * 4 + 1] = value
      data[i * 4 + 2] = value
      data[i * 4 + 3] = 255
    }

    const texture = new THREE.DataTexture(data, size, size)
    texture.needsUpdate = true
    return texture
  }, [])

  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <meshBasicMaterial map={texture} />
    </mesh>
  )
}
```

